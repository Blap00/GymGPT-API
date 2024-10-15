from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import generics,permissions
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
import json
import openai  # type: ignore
from dotenv import load_dotenv
import os
from rest_framework import status  # type: ignore
from rest_framework.response import Response  # type: ignore
from rest_framework.decorators import api_view  # type: ignore

# Importar modelos y serializers
from .models import *  # Importando modelos desde models.py
from .serializers import RegisterSerializer, LoginSerializer, UserEditSerializer, FeedbackSerializer

# Cargar variables de entorno
load_dotenv()
User = get_user_model()

# Página de inicio
def index(request):
    return render(request, 'api/index.html')

# Configurar la API Key de OpenAI
openai.api_key = os.environ.get('OPENAI_API_KEY')

@csrf_exempt
@api_view(['POST'])
def interpret_text(request):
    try:
        # Obtener los datos de la solicitud
        data = request.data
        text_input = data.get('text', '').strip()

        if not text_input:
            return Response({'error': 'No se proporcionó texto'}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener la configuración desde la base de datos
        config = OpenAIConfig.objects.first()
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

        # Extraer la respuesta generada
        generated_text = response['choices'][0]['message']['content'].strip()

        return Response({'response': generated_text}, status=status.HTTP_200_OK)

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
            return Response({"message": "Inicio de sesión exitoso", "user": user.username}, status=status.HTTP_200_OK)
        else:
            print("Serializer errors: ", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

User = get_user_model()

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
        return self.request.user
    
class FeedbackCreateView(generics.CreateAPIView):
    queryset = FeedbackModel.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
