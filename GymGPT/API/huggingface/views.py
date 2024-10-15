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
from .serializers import RegisterSerializer, LoginSerializer, UserEditSerializer

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
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text_input = data.get('text', '')

            if not text_input:
                return JsonResponse({'error': 'No se proporcionó texto'}, status=400)

            # Llamada a la API de OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un asistente que responde en español y conoce sobre gimnasios y las máquinas, tienes la habilidad de guiar a un principiante a utilizar la maquina, las posiciones, la fuerza requerida y el paso a paso mostrando la maquina"},
                    {"role": "user", "content": text_input}
                ],
                max_tokens=1600,  # Ajusta la cantidad de tokens según tu necesidad
                temperature=0.7
            )

            # Extraer la respuesta generada
            generated_text = response['choices'][0]['message']['content'].strip()

            return JsonResponse({'response': generated_text}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Se requiere una solicitud POST'}, status=400)


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