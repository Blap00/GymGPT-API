from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.mail import send_mail
from django.core.cache import cache
from django.utils.crypto import get_random_string

import openai  # type: ignore
from dotenv import load_dotenv
import os

from rest_framework import status, exceptions  # type: ignore
from rest_framework.response import Response  # type: ignore
from rest_framework.decorators import api_view, permission_classes  # type: ignore
from rest_framework.permissions import IsAuthenticated, AllowAny  # type: ignore
from rest_framework.views import APIView  # type: ignore
from rest_framework import generics, permissions  # type: ignore


# Importar modelos y serializers
from .models import *  # Importando modelos desde models.py
from .serializers import RegisterSerializer, LoginSerializer, UserEditSerializer, FeedbackSerializer, PasswordResetConfirmSerializer, RequestPasswordResetSerializer

# Cargar variables de entorno
load_dotenv()
User = get_user_model()

# # Página de inicio
# def index(request):
#     return render(request, 'api/index.html')

# Configurar la API Key de OpenAI
openai.api_key = os.environ.get('OPENAI_API_KEY')
User = get_user_model()


# IT WILL GIVE MACHINE INFO, CONFIGURED INSIDE THE MODELS
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def interpret_MachineInfo(request):
    try:
        # Obtener los datos de la solicitud
        data = request.data
        machine_input = data.get('machine_type', '').strip()

        if not machine_input:
            return Response({'error': 'No se proporcionó el tipo de máquina'}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener la configuración desde la base de datos
        config = OpenAIConfig.objects.filter(use='Give machine INFO').first()
        if not config:
            return Response({'error': 'No se ha configurado la API de OpenAI'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # Llamada a la API de OpenAI con los valores de la configuración
        response = openai.ChatCompletion.create(
            model=config.model,
            messages=[
                {"role": "system", "content": config.system_message},
                {"role": "user", "content": f"Describe la máquina {
                    machine_input} y sus características."}
            ],
            max_tokens=config.max_tokens,
            temperature=config.temperature
        )
        tipo_maquina = openai.ChatCompletion.create(
            model=config.model,
            messages=[
                {"role": "system", "content": config.system_message},
                {"role": "user", "content": f"Que tipo de maquina es {machine_input}"}
            ],
            max_tokens=config.max_tokens,
            temperature=config.temperature
        )
        # Extraer la respuesta generada
        generated_text = response['choices'][0]['message']['content'].strip()
        tipo_maquina = tipo_maquina['choices'][0]['message']['content'].strip()

        # Almacenar la rutina generada en la base de datos
        user = request.user  # Obtener el usuario autenticado
        machine = MachineInfoGeneratedAI(
            usuario=user,  # Aquí user será la instancia correcta de CustomUser si está autenticado
            nom_maquina=machine_input,
            tipo_maquina=tipo_maquina,
            AI_use=config,
            MachineInfo=generated_text
        )
        machine.save()

        return Response({'response': generated_text}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# IT WILL GIVE ROUTINE INFO, CONFIGURED INSIDE THE MODELS


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Añadir permiso de autenticación
def interpret_Routine(request):
    try:
        # Obtener los datos de la solicitud
        data = request.data
        text_input = data.get('routine', '').strip()

        if not text_input:
            return Response({'error': 'No se proporcionó texto'}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener la configuración desde la base de datos
        config = OpenAIConfig.objects.filter(use='Give Routine INFO').first()
        if not config:
            return Response({'error': 'No se ha configurado la API de OpenAI'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Llamada a la API de OpenAI con los valores de la configuración
        response = openai.ChatCompletion.create(
            model=config.model,
            messages=[
                {"role": "system", "content": config.system_message},
                {"role": "user", "content": text_input}
            ],
            max_tokens=config.max_tokens,
            temperature=config.temperature
        )

        # Extraer la respuesta generada por OpenAI
        generated_text = response['choices'][0]['message']['content'].strip()

        # Almacenar la rutina generada en la base de datos
        user = request.user  # Obtener el usuario autenticado
        routine = RoutineGeneratedAI(
            usuario=user,  # Aquí user será la instancia correcta de CustomUser si está autenticado
            AI_use=config,
            routineGenerated=generated_text
        )
        routine.save()

        # Retornar la respuesta y confirmar el guardado
        return Response({'response': generated_text, 'message': 'Rutina generada y almacenada con éxito'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            # Configurar los detalles del correo
            subject = "Bienvenido a GymGPT"

            # Mensaje en HTML con estilos inline
            html_message = """
            <div style="font-family: Arial, sans-serif; color: #333;">
                <h3 style="color: #007BFF;">Bienvenido a GymGPT</h3>
                <p>
                    Nuestra aplicación permite a los usuarios escanear las máquinas y comprender su uso, además de marcar y llevar un 
                    seguimiento sobre ellas. Con un diseño responsivo y una arquitectura de API RESTful, GymGPT está construido para 
                    adaptarse a diversas necesidades, desde el uso personal hasta la integración en entornos de Gimnasio. Esta 
                    combinación de tecnologías modernas y buenas prácticas de desarrollo garantiza una experiencia fluida y confiable 
                    para el usuario final.
                </p>
                <h5>Para ingresar a nuestro repositorio temporal hasta llegar a producción, favor ingresar a 
                    <a href="https://github.com/Blap00/GymGPT-API" style="color: #28a745;">este enlace</a>.
                </h5>
                <h6 style="color: #dc3545;">Si has recibido este enlace por error o te han llegado múltiples notificaciones no deseadas,
                    por favor ignora este mensaje o bloquea al remitente. Gracias.</h6>
            </div>
            """

            from_email = settings.EMAIL_HOST_USER
            recipient_list = [user.email]

            # Enviar el correo con el mensaje HTML
            send_mail(
                subject,
                "",
                from_email,
                recipient_list,
                fail_silently=False,
                html_message=html_message  # Aquí se incluye el mensaje HTML
            )
            return Response({"message": "Usuario registrado con éxito"}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            # Envía los errores detallados en la respuesta
            return Response({"message": "Usuario no registrado", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def LoginView(request):
    if request.method == 'POST':
        print("Data request: ", request.data)

        email = request.data.get('email', None)
        username = CustomUser.objects.filter(
            email=email).first() if email else None
        print(f"User found: {username.username if username else 'No user'}")

        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            print("Serializer is valid")
            user = serializer.validated_data['user']
            return Response({"message": "Inicio de sesión exitoso", "user": user.id}, status=status.HTTP_200_OK)
        else:
            print("Serializer errors: ", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserEditView(generics.UpdateAPIView):
    """
    Vista para permitir que los usuarios editen su perfil.
    """
    serializer_class = UserEditSerializer

    # Solo usuarios autenticados pueden actualizarse
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Obtiene el usuario autenticado que realizará la actualización.
        """
        # print(self.request.user)

       
        return self.request.user


class UserEditarMultiParser(APIView):
    def put(self, request, *args, **kwargs):
        # Obtén el usuario actual
        user = request.user

        # Verifica si se ha enviado la imagen
        if 'image' not in request.data:
            raise exceptions.ParseError(
                "No has seleccionado el archivo a subir")

        # Serializa el usuario con los datos de la solicitud
        serializer = UserEditSerializer(
            instance=user, data=request.data, context={'request': request})

        if serializer.is_valid():
            # Guarda los cambios en la instancia del usuario
            # MAIL
            user = serializer.save()

            # Configurar los detalles del correo
            subject = f"Modificacion de usuario {[user.first_name]} {[user.last_name]}, GymGPT"

            # Mensaje en HTML con estilos inline
            html_message = """
                <div style="font-family: Arial, sans-serif; color: #333;">
                    <p>
                        Hemos recibido una modificación de usuario desde tu cuenta, si esto ha sido una equivocación o
                        similar, favor revisar su cuenta de GymGPT de no tener acceso a la cuenta solicitamos que nos envie
                        un mail a <a href="mailto://test1ngm4il001@gmail.com">Correo de atención al usuario</a> informando
                        su situación y nosotros haremos lo posible por recuperar su cuenta, si olvido la contraseña de
                        ingreso, favor de ingresar '¿Olvido la contraseña?' en la Aplicación.
                    </p>
                    <h5>Para ingresar a nuestro repositorio temporal hasta llegar a producción, favor ingresar a
                        <a href="https://github.com/Blap00/GymGPT-API" style="color: #28a745;">este enlace</a>.
                    </h5>
                    <h6 style="color: #dc3545;">Si has recibido este enlace por error o te han llegado múltiples notificaciones no deseadas,
                        por favor ignora este mensaje o bloquea al remitente. Gracias.</h6>
                </div>
                """

            from_email = settings.EMAIL_HOST_USER
            recipient_list = [user.email]

            # Enviar el correo con el mensaje HTML
            send_mail(
                subject,
                "",
                from_email,
                recipient_list,
                fail_silently=False,
                html_message=html_message  # Aquí se incluye el mensaje HTML
            )

            # Devuelve la respuesta con los datos del serializer
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FeedbackCreateView(generics.CreateAPIView):
    queryset = FeedbackModel.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['GET'])
def get_user(request, id):
    try:
        user = CustomUser.objects.filter(id=id).first()
        # Aquí puedes incluir los campos que desees retornar
        routines = RoutineGeneratedAI.objects.filter(
            user=user)  # Obtén todas las rutinas del usuario

        # Formatear las rutinas
        routines_data = [
            {
                'user': routine.user,
                'goal': routine.goal,
                'routine': routine.routine,
                'created_at': routine.created_at,
            } for routine in routines
        ]
        imagefieldResponse = ''
        if user.image:
            imagefieldResponse = user.image.url
        else:
            imagefieldResponse = ''
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'height': user.height,
            'age': user.age,
            'weight': user.weight,
            'routines': routines_data,
            'image': imagefieldResponse
            # Incluye otros campos según sea necesario
        }
        return JsonResponse({"user": user_data}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print("Error"+str(e))
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RequestPasswordResetView(generics.GenericAPIView):
    serializer_class = RequestPasswordResetSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']

            try:
                user = CustomUser.objects.get(email=email)  # Cambia esto
            except CustomUser.DoesNotExist:  # Cambia aquí también
                return Response({"message": "El correo proporcionado no está registrado."}, status=status.HTTP_400_BAD_REQUEST)

            # Generar y enviar el código de recuperación
            recovery_code = get_random_string(length=6, allowed_chars='0123456789')
            cache.set(f'recovery_code_{user.id}', recovery_code, timeout=600)

            # Enviar el correo con el código de recuperación
            subject = "Recuperación de contraseña"
            html_message = f"""
            <div style="font-family: Arial, sans-serif; color: #333;">
                <h3 style="color: #007BFF;">Código de Recuperación</h3>
                <p>Estimado {user.first_name},</p>
                <p>Has solicitado recuperar tu contraseña. Utiliza el siguiente código para restablecerla:</p>
                <h2 style="color: #28a745;">{recovery_code}</h2>
                <p>Este código es válido por 10 minutos. Si no solicitaste este correo, ignóralo.</p>
            </div>
            """

            from_email = settings.EMAIL_HOST_USER
            recipient_list = [user.email]
            send_mail(subject, "", from_email, recipient_list, fail_silently=False, html_message=html_message)

            return Response({"message": "Correo enviado con el código de recuperación."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            recovery_code = serializer.validated_data['recovery_code']
            new_password = serializer.validated_data['new_password']

            try:
                user = CustomUser.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"message": "El correo proporcionado no está registrado."}, status=status.HTTP_400_BAD_REQUEST)

            # Verificar el código de recuperación
            stored_code = cache.get(f'recovery_code_{user.id}')
            if not stored_code or stored_code != recovery_code:
                return Response({"message": "Código de recuperación inválido o expirado."}, status=status.HTTP_400_BAD_REQUEST)

            # Cambiar la contraseña
            user.set_password(new_password)
            user.save()

            # Eliminar el código de recuperación del caché
            cache.delete(f'recovery_code_{user.id}')

            return Response({"message": "Contraseña actualizada con éxito."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

