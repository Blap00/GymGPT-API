from rest_framework import serializers # type: ignore
from .models import CustomUser, FeedbackModel, FitnessRoutine  # Importa tu modelo de usuario personalizado
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate

from django.contrib.auth import get_user_model
from PIL import Image
from io import BytesIO

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'password']  

    def create(self, validated_data):
        email = validated_data['email']
        username = email.split('@')[0]

        # Crear el usuario utilizando los valores proporcionados
        user = CustomUser(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=email,
            username=username
        )
        user.set_password(validated_data['password'])
        user.save()
        
        return user
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    username_or_email = serializers.CharField(required=False)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        username_or_email = attrs.get('username_or_email')
        password = attrs.get('password')

        # Verificar si se proporciona un email o un nombre de usuario
        if email:
            user = CustomUser.objects.filter(email=email).first()
            if not user:
                raise serializers.ValidationError('Usuario con este email no encontrado.')
            username_or_email = user.username

        if not username_or_email:
            raise serializers.ValidationError('Se requiere un nombre de usuario o email.')

        # Autenticar usando el backend
        user = authenticate(username=username_or_email, password=password)

        if user is None:
            raise serializers.ValidationError('Credenciales incorrectas.')

        attrs['user'] = user
        return attrs


class UserEditSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    image = serializers.ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'password', 'age', 'height', 'weight', 'gender', 'image']

    def validate_image(self, value):
        """Validar que el archivo es una imagen y cumple los requisitos."""
        if value.size > 5 * 1024 * 1024:  # Límite de 5MB
            raise serializers.ValidationError("La imagen es demasiado grande (máx. 5MB).")

        # Verificar si es un archivo de imagen válido
        try:
            # Intentar abrir la imagen con Pillow
            img = Image.open(value)
            img.verify()  # Verifica que la imagen no esté corrupta
        except (IOError, SyntaxError):
            raise serializers.ValidationError("Sube una imagen válida. El archivo subido no es una imagen válida o está corrupto.")

        return value

    

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackModel
        fields = ['id', 'first_name', 'last_name', 'email', 'feedback', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class FitnessRoutineSerializer(serializers.ModelSerializer):
    class Meta:
        model = FitnessRoutine
        fields = ['user', 'goal', 'routine', 'created_at']