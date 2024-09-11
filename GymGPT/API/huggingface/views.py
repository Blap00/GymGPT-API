from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import openai
from dotenv import load_dotenv
import os

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
