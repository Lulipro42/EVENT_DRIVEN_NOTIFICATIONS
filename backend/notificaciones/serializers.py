from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import transaction
from .models import Cliente
from rest_framework_simplejwt.tokens import RefreshToken

class ClienteSerializer(serializers.ModelSerializer):
    # SENIOR TIP: Declaramos 'password' explícitamente porque NO pertenece al modelo Cliente.
    # Usamos 'write_only' para que jamás se exponga en las respuestas JSON de la API.
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
        # Quitamos 'user' de los campos requeridos en el JSON de entrada, 
        # ya que la API lo creará internamente de forma automática.
        fields = ['user', 'email', 'password']
        
        # Mantenemos tus validaciones limpias para el email
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

        # SENIOR TIP: Usamos una transacción atómica. Si la creación del Cliente falla, 
        # el Usuario de Django tampoco se guarda en la base de datos (evita datos basura).
        with transaction.atomic():
            # 1. Creamos el usuario base de Django (aquí se encripta la contraseña automáticamente)
            user = User.objects.create_user(
                username=email,  # Usamos el email como username del sistema
                email=email,
                password=password
            )
            
            # 2. Creamos el perfil del cliente vinculándolo al usuario recién creado
            cliente = Cliente.objects.create(
                user=user,
                **validated_data
            )
            
        return cliente


    def to_representation(self, instance):
        """
        Transforma la instancia guardada (el cliente) en el JSON de respuesta final.
        """
        # Obtenemos la representación estándar del objeto
        ret = super().to_representation(instance)
        
        # 2. Generamos los tokens basándonos en el usuario (instance.user)
        refresh = RefreshToken.for_user(instance.user)
        
        # 3. Inyectamos los tokens en el diccionario de respuesta
        ret['access'] = str(refresh.access_token)
        ret['refresh'] = str(refresh)
        
        return ret