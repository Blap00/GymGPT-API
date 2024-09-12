from rest_framework import serializers # type: ignore
from .models import CustomUser  # Importa tu modelo de usuario personalizado
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser  # Usamos CustomUser en lugar de User
        fields = ('nombre', 'password', 'password2', 'mail')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs

    def create(self, validated_data):
        user = CustomUser.objects.create(
            nombre=validated_data['nombre'],
            mail=validated_data['mail']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
