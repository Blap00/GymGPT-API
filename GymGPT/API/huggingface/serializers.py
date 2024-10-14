from rest_framework import serializers # type: ignore
from .models import CustomUser  # Importa tu modelo de usuario personalizado
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']  # Asegúrate de incluir todos los campos necesarios

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])  # Asegúrate de establecer la contraseña correctamente
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