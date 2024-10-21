from rest_framework import serializers # type: ignore
from .models import *  # Importa tu modelo de usuario personalizado
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
    current_password = serializers.CharField(write_only=True)
    image = serializers.ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'current_password', 'age', 'height', 'weight', 'gender', 'image']

    def validate_current_password(self, value):
        """
        Verifica que la contraseña actual proporcionada sea correcta.
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("La contraseña actual no es correcta.")
        return value

    def update(self, instance, validated_data):
        # Eliminamos la contraseña actual del diccionario de datos validados
        validated_data.pop('current_password', None)
        
        # Actualizamos solo los otros campos
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.age = validated_data.get('age', instance.age)
        instance.height = validated_data.get('height', instance.height)
        instance.weight = validated_data.get('weight', instance.weight)
        instance.gender = validated_data.get('gender', instance.gender)

        # Verificar si hay una imagen para actualizar
        if 'image' in validated_data:
            instance.image = validated_data.get('image', instance.image)

        # Guardamos las actualizaciones
        instance.save()
        return instance

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackModel
        fields = ['id', 'first_name', 'last_name', 'email', 'feedback', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
