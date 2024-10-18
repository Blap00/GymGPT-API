from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, null=False)  # Hacer el email único
    weight = models.IntegerField(null=True)
    height = models.IntegerField(null=True)
    age = models.IntegerField(null=True)
    gender = models.CharField(max_length=10, null=True)
    image = models.FileField(null=True)
    def __str__(self):
        return str(self.id)
# Feedback info
class FeedbackModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=25, null=False)
    last_name = models.CharField(max_length=25, null=False)
    email = models.EmailField(max_length=60, null=False)
    feedback = models.TextField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)

class OpenAIConfig(models.Model):
    model = models.CharField(max_length=50, default='gpt-3.5-turbo', help_text="Modelo de OpenAI a utilizar.")
    temperature = models.FloatField(default=0.7, help_text="Controla la aleatoriedad de las respuestas (0 a 2).")
    max_tokens = models.IntegerField(default=1600, help_text="Número máximo de tokens en la respuesta.")
    system_message = models.TextField(default="Eres un asistente que responde en español y conoce sobre gimnasios y las máquinas.", help_text="Mensaje del sistema que guía las respuestas de OpenAI.")

    class Meta:
        verbose_name = "Configuración de OpenAI"
        verbose_name_plural = "Configuración de OpenAI"

    def __str__(self):
        return f"Configuración de OpenAI (Modelo: {self.model})"


class FitnessRoutine(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    goal = models.CharField(max_length=255)
    routine = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Rutina del usuario {self.user.first_name}, objetivo: {self.goal}"


class Maquinas(models.Model):
    nom_maquina = models.CharField(max_length=100)
    tipo_maquina = models.CharField(max_length=100)
    descripcion_uso = models.TextField
    inteligencia_artificial = models.ForeignKey(OpenAIConfig,on_delete=models.CASCADE, null=False)
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    def __str__(self):
        return f"Maquina {self.nom_maquina} usada por {self.usuario} con IA {self.inteligencia_artificial}"

class Ejercicios(models.Model):
    grupo_muscular = models.CharField(max_length=25)
    niv_dificultad = models.CharField(max_length=25)
    repeticiones = models.IntegerField()
    series = models.IntegerField()
    instrucciones = models.TextField()
    videoDemostrativo = models.CharField(max_length=255)
    maquina = models.ForeignKey(Maquinas, on_delete=models.CASCADE)
    ia = models.ForeignKey(OpenAIConfig, on_delete=models.CASCADE)
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    def __str__(self):
        return f"Ejercicio {self.grupo_muscular} para {self.usuario} con {self.repeticiones} repeticiones"