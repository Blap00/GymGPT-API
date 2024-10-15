from rest_framework import serializers # type: ignore
from .models import CustomUser, FeedbackModel  # Importa tu modelo de usuario personalizado
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate

from django.contrib.auth import get_user_model

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
    

class UserEditSerializer(serializers.ModelSerializer):
    # Se define el campo password para poder actualizarlo
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])

    class Meta:
        model = CustomUser
        # Incluye los campos que el usuario podrá editar
        fields = ['first_name', 'last_name', 'password', 'age', 'height', 'weight', 'gender']

    def update(self, instance, validated_data):
        # Actualizar los campos del usuario
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.age = validated_data.get('age', instance.age)
        instance.height = validated_data.get('height', instance.height)
        instance.weight = validated_data.get('weight', instance.weight)
        instance.gender = validated_data.get('gender', instance.gender)

        # Solo establece una nueva contraseña si se proporciona
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)

        instance.save()
        return instance
    

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackModel
        fields = ['id', 'first_name', 'last_name', 'email', 'feedback', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']