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
import uuid


from rest_framework import status, exceptions  # type: ignore
from rest_framework.response import Response  # type: ignore
from rest_framework.decorators import api_view, permission_classes  # type: ignore
from rest_framework.permissions import IsAuthenticated, AllowAny  # type: ignore
from rest_framework.views import APIView  # type: ignore
from rest_framework import generics, permissions  # type: ignore

# JWT
from rest_framework_simplejwt.tokens import RefreshToken


# GOOGLE AUTH
from google.oauth2 import id_token
from google.auth.transport import requests

# Importar modelos y serializers
from .models import *  # Importando modelos desde models.py
from .serializers import *

# Cargar variables de entorno
load_dotenv()
User = get_user_model()


# Configurar la API Key de OpenAI
openai.api_key = os.environ.get('OPENAI_API_KEY')
User = get_user_model()

# Configura la API de firebase para verificar con GOOGLE
import firebase_admin
from firebase_admin import credentials, auth

# Inicializa Firebase (haz esto una sola vez en tu proyecto)


# IT WILL GIVE MACHINE INFO, CONFIGURED INSIDE THE MODELS
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def interpret_MachineInfo(request):
    try:
        # Obtener los datos de la solicitud
        data = request.data
        machine_input = data.get('machine_type', '').strip()
        difficult = data.get('difficult', '').strip()

        if not machine_input:
            return Response({'error': 'No se proporcionó el tipo de máquina'}, status=status.HTTP_400_BAD_REQUEST)

        # Mapeo de dificultad
        def get_difficulty_string(difficult):
            difficult_map = {
                "0": "Fácil",
                "1": "Medio",
                "2": "Difícil"
            }
            return difficult_map.get(difficult, "Desconocido")  # "Desconocido" si el valor no coincide con las claves

        # Convertir la dificultad
        difficult_string = get_difficulty_string(difficult)

        # Obtener la configuración desde la base de datos
        config = OpenAIConfig.objects.filter(use='Give machine INFO').first()
        if not config:
            return Response({'error': 'No se ha configurado la API de OpenAI'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Llamada a la API de OpenAI con los valores de la configuración
        response = openai.ChatCompletion.create(
            model=config.model,
            messages=[
                {"role": "system", "content": config.system_message},
                {"role": "user", "content": f"Describe en HTML la máquina {machine_input} y sus características. Nivel de dificultad: {difficult_string}. Utiliza <p>, <ul>, <li> y encabezados <h2> o <h3> para estructurar la información."}
            ],
            max_tokens=config.max_tokens,
            temperature=config.temperature
        )
        tipo_maquina_response = openai.ChatCompletion.create(
            model=config.model,
            messages=[
                {"role": "system", "content": config.system_message},
                {"role": "user", "content": f"¿Qué tipo de máquina es {machine_input}?. Utiliza <p>, <ul>, <li> y encabezados <h2> o <h3> para estructurar la información."}
            ],
            max_tokens=config.max_tokens,
            temperature=config.temperature
        )

        # Extraer la respuesta generada
        generated_text = response['choices'][0]['message']['content'].strip()
        tipo_maquina = tipo_maquina_response['choices'][0]['message']['content'].strip()
        processed_text = generated_text.replace("\n\n", "").replace("\n", "").replace("```", "").replace("html","").replace('< lang="es">', "")
        processed_MachineTyoe = tipo_maquina.replace("\n\n", "").replace("\n", "").replace("```", "").replace("html","").replace('< lang="es">', "")
        # Almacenar la rutina generada en la base de datos
        user = request.user  # Obtener el usuario autenticado
        machine = MachineInfoGeneratedAI(
            usuario=user,
            nom_maquina=machine_input, # DELIVER MACHINE-INPUT
            tipo_maquina=processed_MachineTyoe, # DELIVER TIPO_MAQUINA PROCESSED
            AI_use=config,
            MachineInfo=processed_text # DELIVER GENERATED_TEXT  PROCESSED
        )
        machine.save()

        return Response({'response': processed_MachineTyoe}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# IT WILL GIVE ROUTINE INFO, CONFIGURED INSIDE THE MODELS


# Get the last Machine info generated by USER, it is saved in DBA
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMachineInfo(request, id):
    try:
        IdUser = id
        user = CustomUser.objects.filter(id=IdUser).first()
        machine_info = MachineInfoGeneratedAI.objects.filter(usuario=user).order_by('-id').first()
        context = {
            'Machine_name': machine_info.nom_maquina.capitalize(),
            'Machine_type': machine_info.tipo_maquina.capitalize(),
            'Machine_info': machine_info.MachineInfo,
            'Created_at': machine_info.created_at,
            'message': str(machine_info)  # Llamada a __str__ para obtener el mensaje
        }
        return Response(context, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



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
        processed_text = generated_text.replace("\n\n", "<br />").replace("\n", "<br />").replace("```","").replace("html","")

        configExcersice =  OpenAIConfig.objects.filter(use='Give by Hours excersice INFO').first()
        if not configExcersice:
            return Response({'error': 'No se ha configurado la API de OpenAI de configExcersice'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        excercise = openai.ChatCompletion.create(
            model=configExcersice.model,
            messages=[
                {"role": "system", "content": configExcersice.system_message},
                {"role": "user", "content": text_input}
            ],
            max_tokens=configExcersice.max_tokens,
            temperature=configExcersice.temperature
        )

        
        # Obtener la informacion en formato de horas:
        text_principalExcersice = excercise['choices'][0]['message']['content'].strip()


        configHoras = OpenAIConfig.objects.filter(use='Give by Hours INFO').first()
        if not configHoras:
            return Response({'error': 'No se ha configurado la API de OpenAI de ConfigHoras'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Llamada a la API de OpenAI con los valores de la configuración
        horas = openai.ChatCompletion.create(
            model=configHoras.model,
            messages=[
                {"role": "system", "content": configHoras.system_message},
                {"role": "user", "content": f'{text_input}, {text_principalExcersice}'}
            ],
            max_tokens=configHoras.max_tokens,
            temperature=configHoras.temperature
        )
        generated_text = horas['choices'][0]['message']['content'].strip()
        # Almacenar la rutina generada en la base de datos
        user = request.user  # Obtener el usuario autenticado
        routine = RoutineGeneratedAI(
            usuario=user,  # Aquí user será la instancia correcta de CustomUser si está autenticado
            AI_use=config,
            objective=text_input,
            principalExerciseGen = text_principalExcersice,
            horarioExcerciseGen = generated_text,
            routineGenerated=processed_text
        )
        routine.save()

        # Retornar la respuesta y confirmar el guardado
        return Response({'response': generated_text, 'message': 'Rutina generada y almacenada con éxito'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def getRoutineInfo(request, id):
    try:
        user = CustomUser.objects.filter(id=id).first()  # Obtener el usuario autenticado
        objetivo = request.data.get('objetivo')  # Obtener el nombre del objetivo desde la solicitud, si se proporciona
        
        if objetivo:
            routine_info = RoutineGeneratedAI.objects.filter(usuario=user, objetivo=objetivo).order_by('-created_at').first()
        else:
            routine_info = RoutineGeneratedAI.objects.filter(usuario=user).order_by('-created_at').first()

        # Validar si se encontró alguna rutina
        if routine_info:
            return Response({
                'Routine': routine_info.routineGenerated.capitalize(),
                'created_at': routine_info.created_at,
                'message': 'Routine Info GET LAST BY USER AND OBJECTIVE' if objetivo else 'Routine Info GET LAST BY USER'
            }, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'No se encontró información de rutina para el usuario y/o objetivo'}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as ex:
        return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
                <h5>Para ingresar a nuestro sitio desde Vercel hasta cubrir todos los dispositivos, favor ingresar a 
                    <a href="https://gym-gpt-front.vercel.app/home" style="color: #28a745;">este enlace</a>.
                </h5>
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

from rest_framework_simplejwt.tokens import RefreshToken
from google.auth.transport import requests
import time

# Configura tu CLIENT_ID (ID del cliente de tu app en GCP)
GOOGLE_CLIENT_ID = "552925030949-fr3rra4lje9enhf74b2diig9qddvrf2e.apps.googleusercontent.com"
 
@api_view(['POST'])
def LoginGoogleAuth(request):
    time.sleep(2)
    try:
        # Obtén el token enviado desde el frontend
        google_token = request.data.get('token', None)
        if not google_token:
            return Response({"error": "Token no proporcionado."}, status=status.HTTP_400_BAD_REQUEST)
        # Verifica el token de Google
        print("Verifica el token de Google")
        try:
            print(GOOGLE_CLIENT_ID)
            id_info = id_token.verify_oauth2_token(google_token, requests.Request(), 
                                                   GOOGLE_CLIENT_ID)
        except ValueError as e:
            return Response({"error": "El Id_info no es valido. "+str(e)}, status=status.HTTP_400_BAD_REQUEST)

        print(f" id info = {id_info}")
        # Asegúrate de que el token esté emitido por Google y sea válido para tu aplicación

        if id_info['aud'] != GOOGLE_CLIENT_ID:
            return Response({"error": "El token no coincide con el CLIENT_ID."}, status=status.HTTP_400_BAD_REQUEST)
        print("IT GET HERE!")
        # Extrae la información del usuario
        email = id_info.get('email')
        name = id_info.get('name', '')
        first_name, last_name = name.split(' ', 1) if ' ' in name else (name, '')

        # Busca o crea el usuario en la base de datos
        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
                'first_name': first_name,
                'last_name': last_name,
            }
        )
        print("IS DOING GREAT")
        # Genera el token JWT
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        # Serializar y devolver los datos del usuario
        serializer = CustomUserSerializer(user)
        return Response({
            "message": "Inicio de sesión exitoso.",
            "user": serializer.data,
            "accessTokens": str(access_token),
            'refreshTokens': str(refresh), 
        }, status=status.HTTP_200_OK)

    except ValueError:
        return Response({"error": "Token inválido o expirado."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
                        un mail a <a href="mailto://fabian.palma.ramos@gmail.com">Correo de atención al usuario</a> informando
                        su situación y nosotros haremos lo posible por recuperar su cuenta, si olvido la contraseña de
                        ingreso, favor de ingresar '¿Olvido la contraseña?' en la Aplicación.
                    </p>
                    <h5>Para ingresar a nuestro sitio desde Vercel hasta cubrir todos los dispositivos, favor ingresar a 
                        <a href="https://gym-gpt-front.vercel.app/home" style="color: #28a745;">este enlace</a>.
                    </h5>

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
        # Obtener el usuario por ID
        user = CustomUser.objects.filter(id=id).first()
        if not user:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        # Obtener todas las rutinas del usuario y formatearlas
        routines = RoutineGeneratedAI.objects.filter(usuario=user)
        routines_data = [
            {
                'user_id': routine.usuario.id,  # Solo el ID del usuario en lugar del objeto completo
                'goal': routine.objective,
                'routine': routine.routineGenerated,
                'created_at': routine.created_at,
            } for routine in routines
        ]

        # Imagen de usuario, si está presente
        imagefieldResponse = user.image.url if user.image else ''

        # Datos de usuario a retornar
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
            'image': imagefieldResponse,
            'subscription': user.subscription
        }

        return JsonResponse({"user": user_data}, status=status.HTTP_200_OK)

    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print("Error: " + str(e))
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RequestPasswordResetView(generics.GenericAPIView):
    serializer_class = RequestPasswordResetSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']

            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                return Response({"message": "El correo proporcionado no está registrado."}, status=status.HTTP_400_BAD_REQUEST)

            recovery_code = get_random_string(length=6, allowed_chars='0123456789')

            VerificationCode.objects.update_or_create(email=email, defaults={"code": recovery_code})
            stored_code = VerificationCode.objects.get(email=email,  code =recovery_code)


            subject = "Recuperación de contraseña"
            html_message = f"""
            <div style="font-family: Arial, sans-serif; color: #333;">
                <h3 style="color: #007BFF;">Código de Recuperación</h3>
                <p>Estimado {user.first_name},</p>
                <p>Has solicitado recuperar tu contraseña. Utiliza el siguiente código para restablecerla:</p>
                <h2 style="color: #28a745;">{str(stored_code)}</h2>
                <p>Este código es válido por 5 minutos. Si no solicitaste este correo, ignóralo.</p>

            </div>
            """
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [user.email]
            try:
                send_mail(subject, "", from_email, recipient_list, html_message=html_message)
            except Exception as ex:
                print("Error enviando el correo:", ex)

            return Response({"message": "Correo enviado con el código de recuperación."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ValidateRecoveryCodeView(generics.GenericAPIView):
    serializer_class = VerifyTokenSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = ValidateMailAndCodeSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "El correo y el código son válidos."}, status=status.HTTP_200_OK)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            recovery_code = serializer.validated_data['validation_code']
            new_password = serializer.validated_data['new_password']

            user = CustomUser.objects.filter(email=email).first()
            if not user:
                return Response({"message": "El correo proporcionado no está registrado."}, status=status.HTTP_400_BAD_REQUEST)

            # Verificar el código de recuperación
            stored_code = VerificationCode.objects.get(email=email, code=recovery_code)
            if not stored_code or stored_code != recovery_code:
                return Response({"message": "Código de recuperación inválido o expirado."}, status=status.HTTP_400_BAD_REQUEST)

            # Cambiar la contraseña
            user.set_password(new_password)
            user.save()

            # Eliminar el código de recuperación del caché
            cache.delete(f'recovery_code_{user.id}')
            
            # Enviar mensaje informando el cambio en la cuenta:
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                return Response({"message": "El correo proporcionado no está registrado."}, status=status.HTTP_400_BAD_REQUEST)


            subject = "Contraseña modificada"
            html_message = f"""
            <div style="font-family: Arial, sans-serif; color: #333;">
                <h3 style="color: #007BFF;">Modificación de Contraseña</h3>
                <p>Estimado {user.first_name},</p>
                <p>Te enviamos este correo para confirmar que tu contraseña ha sido modificada exitosamente.</p>
                <p>Si realizaste este cambio, puedes ignorar este mensaje. Sin embargo, si no solicitaste esta modificación, te recomendamos tomar acción de inmediato.</p>
                <p>Por favor, responde a este correo o envía un mensaje a 
                <a href="mailto:fabian.palma.ramos@gmail.com">soporte@GymGPT.com</a> para recibir asistencia y proteger la seguridad de tu cuenta.</p>
                <p>Atentamente,</p>
                <p>El equipo de soporte</p>
            </div>
            """
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [user.email]
            try:
                send_mail(subject, "", from_email, recipient_list, html_message=html_message)
            except Exception as ex:
                print("Error enviando el correo:", ex)
            return Response({"message": "Contraseña restablecida exitosamente."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Get a list of Routines to send to FRONT 'searched from WEB'
@api_view(['GET'])
def getRoutinesGlobal(request):
    try:
        routineBucket = [
            {'name': 'Rutina de Piernas Básica'},
            {'name': 'Rutina de Piernas Avanzada'},
            {'name': 'Rutina de Glúteos'},
            {'name': 'Rutina de Glúteos y Piernas'},
            {'name': 'Rutina de Cardio Completo'},
            {'name': 'Rutina de Cardio para Principiantes'},
            {'name': 'Rutina de Cardio HIIT'},
            {'name': 'Rutina de Abdomen'},
            {'name': 'Rutina de Core y Abdomen'},
            {'name': 'Rutina de Abdomen Inferior'},
            {'name': 'Rutina de Brazos'},
            {'name': 'Rutina de Bíceps'},
            {'name': 'Rutina de Tríceps'},
            {'name': 'Rutina de Pecho'},
            {'name': 'Rutina de Espalda'},
            {'name': 'Rutina de Hombros'},
            {'name': 'Rutina de Espalda y Bíceps'},
            {'name': 'Rutina de Pecho y Tríceps'},
            {'name': 'Rutina de Pecho Avanzada'},
            {'name': 'Rutina de Piernas y Core'},
            {'name': 'Rutina de Glúteos y Abdomen'},
            {'name': 'Rutina de Cardio Intensivo'},
            {'name': 'Rutina de Yoga Básica'},
            {'name': 'Rutina de Yoga Avanzada'},
            {'name': 'Rutina de Flexibilidad'},
            {'name': 'Rutina de Resistencia General'},
            {'name': 'Rutina de Equilibrio y Coordinación'},
            {'name': 'Rutina Funcional para Todo el Cuerpo'},
            {'name': 'Rutina de Movilidad'},
            {'name': 'Rutina de Agilidad'},
            {'name': 'Rutina de Fuerza y Potencia'},
            {'name': 'Rutina de Calistenia para Principiantes'},
            {'name': 'Rutina de Calistenia Avanzada'},
            {'name': 'Rutina de Fuerza para Todo el Cuerpo'},
            {'name': 'Rutina de Entrenamiento de Alta Intensidad'},
            {'name': 'Rutina de Entrenamiento de Bajo Impacto'},
            {'name': 'Rutina de Kickboxing'},
            {'name': 'Rutina de Entrenamiento Funcional'},
            {'name': 'Rutina de Cardio y Core'},
            {'name': 'Rutina de Glúteos Intensiva'},
            {'name': 'Rutina de Piernas y Cardio'},
            {'name': 'Rutina de Cardio para Quemar Grasa'},
            {'name': 'Rutina de Alta Resistencia'},
            {'name': 'Rutina de Entrenamiento con Pesas'},
            {'name': 'Rutina de Circuito Completo'},
            {'name': 'Rutina de Descanso Activo'},
            {'name': 'Rutina de Calentamiento'},
            {'name': 'Rutina de Enfriamiento'},
            {'name': 'Rutina de Relajación Muscular'}
        ]
        return Response({'routines':routineBucket}, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getLastRoutineUser(request, id):
    try:
        routines = RoutineGeneratedAI.objects.filter(usuario=id).order_by('-id').first()
        routine = routines.objective
        return Response({'routine': routine}, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getRoutineInfoAll(request, id):
    try:
        user = CustomUser.objects.filter(id=id).first()  # Obtener el usuario autenticado
        objetivo = request.data.get('objetivo')  # Obtener el nombre del objetivo desde la solicitud, si se proporciona
        
        # Filtrar las rutinas del usuario y ordenar por fecha de creación
        if objetivo:
            # Si se proporciona un objetivo, buscar por usuario y objetivo, ordenando por fecha descendente
            routine_info = RoutineGeneratedAI.objects.filter(usuario=user, objetivo=objetivo).order_by('-created_at').first()

        else:
            # Si no se proporciona un objetivo, buscar solo por usuario y la fecha más reciente
            routine_info = RoutineGeneratedAI.objects.filter(usuario=user).order_by('-created_at').first()
        # Validar si se encontró alguna rutina
        if routine_info:
            return Response({
                'Rutina': routine_info.objective.capitalize(),
                'Ejercicio':routine_info.principalExerciseGen.capitalize(),
                'Duracion': routine_info.horarioExcerciseGen,
                'GeneratedRoutine': routine_info.routineGenerated,
                'NomUsuario': user.first_name.capitalize()
            }, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'No se encontró información de rutina para el usuario y/o objetivo'}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as ex:
        return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Validación CODE
class ValidateMailAndCodeView(APIView):
    def post(self, request):
        serializer = ValidateMailAndCodeSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "El correo y el código son válidos."}, status=status.HTTP_200_OK)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

# Envio de MAIL
class SendVerificationCodeView(APIView):
    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"message": "El correo es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si el correo ya está registrado
        if CustomUser.objects.filter(email=email).exists():
            return Response({"message": "El correo ya está registrado."}, status=status.HTTP_400_BAD_REQUEST)

        # Generar código único
        code = get_random_string(length=4, allowed_chars='0123456789')

        # Guardar código en la base de datos
        VerificationCode.objects.update_or_create(email=email, defaults={"code": code})
        print("LOL?")
        # Enviar correo con el código
        subject = "Código de verificación"
        html_message = f"""
            <div style="font-family: Arial, sans-serif; color: #333;">
                <h3 style="color: #007BFF;">Código de validación</h3>
                <p>Estimado,</p>
                <p>Para registrar su usuario en nuestro sistema necesita utilizar el siguiente código:</p>
                <h2 style="color: #28a745;">{str(code)}</h2>
                <p>Este código es válido por 5 minutos. Si no solicitaste este correo, ignóralo.</p>

            </div>
            """
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        try:
            send_mail(subject, "", from_email, recipient_list, html_message=html_message)
            return Response({"message": "El código de verificación ha sido enviado a tu correo."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": "Error al enviar el correo.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        