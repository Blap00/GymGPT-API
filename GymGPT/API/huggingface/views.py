from django.shortcuts import render
from django.http import JsonResponse
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
from .serializers import RegisterSerializer

# Cargar variables de entorno
load_dotenv()


# Página de inicio
def index(request):
    return render(request, 'api/index.html')

# Configurar la API Key de OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

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
                max_tokens=150,  # Ajusta la cantidad de tokens según tu necesidad
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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
