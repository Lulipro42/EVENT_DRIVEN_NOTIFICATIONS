from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import transaction
from .models import Cliente
from rest_framework_simplejwt.tokens import RefreshToken

class ClienteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        error_messages={
            'required': 'La contraseña es obligatoria para el registro.'
        }
    )

    class Meta:
        model = Cliente
        fields = ['user', 'email', 'password']
        
        extra_kwargs = {
            'email': {
                'required': True,
                'error_messages': {
                    'required': 'Este campo es obligatorio.',
                    'invalid': 'Por favor, introduce una dirección de correo válida.'
                }
            }
        }

    def validate_email(self, value):
        """
        Validación de negocio: El email debe ser único tanto en el modelo Cliente 
        como en el modelo User de Django para evitar colisiones de cuentas.
        """
        email_limpio = value.lower().strip()
        
        if User.objects.filter(email=email_limpio).exists() or Cliente.objects.filter(email=email_limpio).exists():
            raise serializers.ValidationError("Este correo electrónico ya está registrado.")
        return value

    def create(self, validated_data):
        """
        Control del flujo de creación y persistencia de datos.
        """
        email = validated_data.get('email')
        password = validated_data.pop('password') # Extraemos la contraseña para que no ensucie al Cliente

        with transaction.atomic():
            user = User.objects.create_user(
                username=email, 
                email=email,
                password=password
            )
            
            cliente = Cliente.objects.create(
                user=user,
                **validated_data
            )
            
        return cliente

    def to_representation(self, instance):
        """
        Transforma la instancia guardada (el cliente) en el JSON de respuesta final.
        """
        ret = super().to_representation(instance)
        refresh = RefreshToken.for_user(instance.user)
        ret['access'] = str(refresh.access_token)
        ret['refresh'] = str(refresh)
        
        return ret