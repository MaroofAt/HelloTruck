from django.db import transaction
from rest_framework import serializers

from tools.models import check_mobile_number, normalize_mobile_number

from .models import Credential, Trader

class TraderRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,required=True,style={'input_type': 'password'})
    email = serializers.EmailField(max_length=254, write_only=True, required=False, allow_null=True)
    mobile_number = serializers.CharField(max_length=25, write_only=True, required=False, allow_null=True)
    class Meta:
        model = Trader
        fields = [
            'email',
            'mobile_number',
            'password',
            'ecommerce',
            'name'
        ]
        extra_kwargs = {
            'email': {'write_only':True, 'required':False, 'allow_null':True},
            'mobile_number': {'write_only':True, 'required':False, 'allow_null':True},
            'name': {'required':True, 'allow_null':False}
        }
    
    def validate(self, attrs):
        try:
            if not attrs['password']:  # Check for empty string/None
                raise serializers.ValidationError({
                    'password': 'This field may not be blank (empty).'
                })
        except KeyError:
            raise serializers.ValidationError({
                'password': 'This field is required.'
            })

        attrs = super().validate(attrs)

        # has_email = False
        try:
            has_email = bool(attrs['email'])
        except KeyError:
            has_email = False
        # has_mobile_number = False
        try:
            has_mobile_number = bool(attrs['mobile_number'])
        except KeyError:
            has_mobile_number = False

        if has_email == has_mobile_number:
            raise serializers.ValidationError(
                "You must provide exactly one field: either 'field_a' or 'field_b', but not both and not no one."
            )

        if len(attrs['name']) < 3:
            raise serializers.ValidationError(
                {'name': 'must be 3 characters or more'}
            )
        
        if len(attrs['password']) < 8:
            raise serializers.ValidationError(
                {'password': 'must be 8 characters or more'}
            )
        
        if has_mobile_number:
            if not check_mobile_number(attrs['mobile_number']):
                raise serializers.ValidationError(
                    {'mobile_number': 'it is not a normal correct mobile_number'}
                )
            attrs['mobile_number'] = normalize_mobile_number(attrs['mobile_number'])

        return attrs

    def create(self, validated_data):
        try:
            try:
                email = validated_data['email']
            except KeyError:
                email = None
            try:
                mobile_number = validated_data['mobile_number']
            except KeyError:
                mobile_number = None
            
            with transaction.atomic():
                credentials = Credential.objects.create_user(
                    role = Credential.Role.TRADER,
                    email = email,
                    mobile_number = mobile_number,
                    password = validated_data['password']
                )
                trader = Trader.objects.create(
                    credentials_id = credentials.id,
                    ecommerce = validated_data['ecommerce'],
                    name = validated_data['name'],
                )

                return trader
            return None
        except KeyError as e:
            raise serializers.ValidationError(
                {f"{str(e)}": 'this field is required'}
            )
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        credentials:Credential = Credential.objects.filter(id=instance.credentials_id).first()

        representation['credentials'] = credentials.get_identifier()

        return representation

