from django.shortcuts import render
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from dotenv import main # type: ignore
import os

main.load_dotenv()
keyApi = os.environ['HUGGINGFACE_API_KEY']

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

            headers = {
                'Authorization': f'Bearer ' + keyApi,
                'Content-Type': 'application/json'
            }

            # Generación de texto con mrm8488/gpt2-spanish
            payload = {
                'inputs': text_input
            }

            # Usar el modelo ajustado para español
            response = requests.post('https://api-inference.huggingface.co/models/mrm8488/gpt2-spanish', headers=headers, json=payload)
            response_data = response.json()

            if 'error' in response_data:
                return JsonResponse({'error': response_data['error']}, status=response.status_code)

            generated_text = response_data[0]['generated_text']

            # Retornar texto generado en español
            return JsonResponse({'response': generated_text}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'POST request required'}, status=400)
