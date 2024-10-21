from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import generics,permissions # type: ignore
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
import json
import openai  # type: ignore
from dotenv import load_dotenv
import os
from rest_framework import status  # type: ignore
from rest_framework.response import Response  # type: ignore
from rest_framework.decorators import api_view, permission_classes  # type: ignore
from rest_framework.permissions import IsAuthenticated # type: ignore


# Importar modelos y serializers
from .models import *  # Importando modelos desde models.py
from .serializers import RegisterSerializer, LoginSerializer, UserEditSerializer, FeedbackSerializer

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
                {"role": "user", "content": f"Describe la máquina {machine_input} y sus características."}
            ],
            max_tokens=config.max_tokens,
            temperature=config.temperature
        )

        # Extraer la respuesta generada
        generated_text = response['choices'][0]['message']['content'].strip()

        # Almacenar la rutina generada en la base de datos
        user = request.user  # Obtener el usuario autenticado
        machine = MachineInfoGeneratedAI(
            usuario=user,  # Aquí user será la instancia correcta de CustomUser si está autenticado
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
            serializer.save()
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
        username = CustomUser.objects.filter(email=email).first() if email else None
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
    permission_classes = [permissions.IsAuthenticated]  # Solo usuarios autenticados pueden actualizarse
    def get_object(self):
        """
        Obtiene el usuario autenticado que realizará la actualización.
        """
        # print(self.request.user)
        return self.request.user
    
class FeedbackCreateView(generics.CreateAPIView):
    queryset = FeedbackModel.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]


User = get_user_model()

@api_view(['GET'])
def get_user(request, id):
    try:
        user = CustomUser.objects.filter(id=id).first()
        # Aquí puedes incluir los campos que desees retornar
        routines = RoutineGeneratedAI.objects.filter(user = user)  # Obtén todas las rutinas del usuario

        # Formatear las rutinas
        routines_data = [
            {
                'user': routine.user,
                'goal': routine.goal,
                'routine': routine.routine,
                'created_at': routine.created_at,
            } for routine in routines
        ]
        imagefieldResponse =''
        if user.image:
            imagefieldResponse = user.image.url
        else:
            imagefieldResponse =''
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
        return JsonResponse({"user":user_data}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print("Error"+str(e))
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    



