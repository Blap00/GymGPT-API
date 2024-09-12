from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt #Testing
import json
import openai
from dotenv import load_dotenv
import os
# THERE WE WILL IMPORT MODELS & FORMS:
from .models import * # Importing models from models.py

# Cargar variables de entorno
load_dotenv()
keyApi = os.environ['OPENAI_API_KEY']  # Asegúrate de usar la clave correcta

# Página de inicio
def index(request):
    return render(request, 'api/index.html')

@csrf_exempt
def interpret_text(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text_input = data.get('text', '')

            if not text_input:
                return JsonResponse({'error': 'No text provided'}, status=400)

            # Configurar la API Key de OpenAI
            openai.api_key = keyApi

            # Llamada a la API de OpenAI usando la nueva sintaxis (>=1.0.0)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Modelo más avanzado compatible con chat
                messages=[
                    {"role": "system", "content": "Eres un asistente que responde en español."},
                    {"role": "user", "content": text_input}
                ],
                max_tokens=100,
                temperature=0.7
            )

            # Extraer la respuesta generada
            generated_text = response['choices'][0]['message']['content'].strip()

            return JsonResponse({'response': generated_text}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'POST request required'}, status=400)

@ensure_csrf_cookie
def registerUsuario(request):
    if request.method == 'POST':
        try:
            # Obtener datos del cuerpo de la solicitud
            data = json.loads(request.body)
            username = data.get('username', '')
            password = data.get('password', '')
            email = data.get('email', '')

            # Validar datos
            if not username or not password or not email:
                return JsonResponse({'error': 'Faltan datos obligatorios.'}, status=400)

            # Verificar si el usuario ya existe
            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'El nombre de usuario ya existe.'}, status=400)

            # Crear el nuevo usuario
            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password)  # Hash de la contraseña
            )

            # Confirmar el registro exitoso
            return JsonResponse({'message': 'Usuario registrado exitosamente.'}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Se requiere una solicitud POST.'}, status=400)