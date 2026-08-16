from django.db import transaction
from rest_framework import serializers

from tools.models import check_mobile_number, normalize_mobile_number

from .models import Credential, Trader, Captain, Sub_Admin , Vehicle
from dashboard.models import Location
from orders.models import Trip

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
                "You must provide exactly one field: either 'email' or 'mobile_number', but not both and not no one."
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

        if has_mobile_number:
            if Credential.objects.filter(mobile_number=attrs['mobile_number']).exists():
                raise serializers.ValidationError(
                    {'mobile_number': 'A user with this mobile number already exists.'}
                )
        if has_email:
            if Credential.objects.filter(email=attrs['email']).exists():
                raise serializers.ValidationError(
                    {'email': 'A user with this email already exists.'}
                )

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

class CaptainRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,required=True,style={'input_type': 'password'})
    username = serializers.CharField(max_length=254, write_only=True, required=False, allow_null=True)
    mobile_number = serializers.CharField(max_length=25, write_only=True, required=False, allow_null=True)
    latitude = serializers.DecimalField(max_digits=12, decimal_places=9,  write_only=True, required=True)
    longitude = serializers.DecimalField(max_digits=12, decimal_places=9,  write_only=True, required=True)
    class Meta:
        model = Captain
        fields = [
            'username',
            'mobile_number',
            'password',
            'latitude',
            'longitude',
            'permanent',
            'name'
        ]
        extra_kwargs = {
            'username': {'write_only':True, 'required':False, 'allow_null':True},
            'mobile_number': {'write_only':True, 'required':False, 'allow_null':True},
            'name': {'required':True, 'allow_null':False},
            'permanent': {'read_only':True}
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

        # has_username = False
        try:
            has_username = bool(attrs['username'])
        except KeyError:
            has_username = False
        # has_mobile_number = False
        try:
            has_mobile_number = bool(attrs['mobile_number'])
        except KeyError:
            has_mobile_number = False

        if has_username == has_mobile_number:
            raise serializers.ValidationError(
                "You must provide exactly one field: either 'username' or 'mobile_number', but not both and not no one."
            )

        if len(attrs['name']) < 3:
            raise serializers.ValidationError(
                {'name': 'must be 3 characters or more'}
            )
        
        if has_username:
            if len(attrs['username']) < 5:
                raise serializers.ValidationError(
                    {'username': 'must be 5 characters or more'}
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

        if has_mobile_number:
            if Credential.objects.filter(mobile_number=attrs['mobile_number']).exists():
                raise serializers.ValidationError(
                    {'mobile_number': 'A user with this mobile number already exists.'}
                )
        if has_username:
            if Credential.objects.filter(username=attrs['username']).exists():
                raise serializers.ValidationError(
                    {'username': 'A user with this username already exists.'}
                )


        return attrs

    def create(self, validated_data):
        try:
            try:
                username = validated_data['username']
            except KeyError:
                username = None
            try:
                mobile_number = validated_data['mobile_number']
            except KeyError:
                mobile_number = None
            
            with transaction.atomic():
                credentials = Credential.objects.create_user(
                    role = Credential.Role.CAPTAIN,
                    username = username,
                    mobile_number = mobile_number,
                    password = validated_data['password']
                )
                accommodation, _ = Location.objects.get_or_create(
                    latitude = validated_data['latitude'],
                    longitude = validated_data['longitude']
                )
                captain = Captain.objects.create(
                    credentials_id = credentials.id,
                    accommodation = accommodation,
                    name = validated_data['name'],
                    permanent = False
                )

                return captain
            return None
        except KeyError as e:
            raise serializers.ValidationError(
                {f"{str(e)}": 'this field is required'}
            )
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['accommodation'] = instance.accommodation_id
        
        credentials:Credential = Credential.objects.filter(id=instance.credentials_id).first()

        representation['credentials'] = credentials.get_identifier()

        return representation


class Sub_AdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,required=True,style={'input_type': 'password'})
    email = serializers.EmailField(max_length=254, write_only=True, allow_null=False)
    class Meta:
        model = Sub_Admin
        fields = [
            'email',
            'password',
            'branch',
            'name'
        ]
        extra_kwargs = {
            'branch': {'required':True},
            'name': {'required':True}
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


        if len(attrs['name']) < 3:
            raise serializers.ValidationError(
                {'name': 'must be 3 characters or more'}
            )
        
        if len(attrs['password']) < 8:
            raise serializers.ValidationError(
                {'password': 'must be 8 characters or more'}
            )
        
        if Credential.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError(
                {'email': 'A user with this email already exists.'}
            )

        return attrs
    
    def create(self, validated_data):
        try:
            with transaction.atomic():
                credentials = Credential.objects.create_user(
                    role = Credential.Role.SUB_ADMIN,
                    email = validated_data['email'],
                    password = validated_data['password']
                )
                sub_admin = Sub_Admin.objects.create(
                    credentials_id = credentials.id,
                    name = validated_data['name'],
                    branch = validated_data['branch'],
                )

                return sub_admin
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


class VehicleSerializer(serializers.ModelSerializer):
    captain = serializers.PrimaryKeyRelatedField(
            queryset=Captain.objects.all(),
            required=True
        )

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "type",
            "accepted_volume",
            "fuel_consumption_per_1km",
            "feul_type",
            "verified",
            "delivery",
            "captain",
        ]
        extra_kwargs = {
            'id': {'read_only':True}
        } 

        def create(self, validated_data):
            validated_data["type"] = 'a'
            validated_data["feul_type"] = 'a'

            captain_id = validated_data["captain"]
            captain = Captain.objects.filter(id=captain_id)

            if not captain.exists():
                raise serializers.ValidationError("Captain doesn't exist")

            vehicle = Vehicle.objects.create(**validated_data)
            return vehicle


class CaptainTripListSerializer(serializers.ModelSerializer):
    vehicle_ids = serializers.SerializerMethodField()
    load_count = serializers.SerializerMethodField()
    total_weight = serializers.SerializerMethodField()
    total_volume = serializers.SerializerMethodField()
    origin_location_ids = serializers.SerializerMethodField()
    destination_location_ids = serializers.SerializerMethodField()
    origin_branch_ids = serializers.SerializerMethodField()
    destination_branch_ids = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = [
            'id',
            'status',
            'launch_datetime',
            'arrival_datetime',
            'vehicle_ids',
            'load_count',
            'total_weight',
            'total_volume',
            'origin_location_ids',
            'destination_location_ids',
            'origin_branch_ids',
            'destination_branch_ids',
        ]

    def _loads(self, trip):
        return trip.captain_order_loads

    def get_vehicle_ids(self, trip):
        return sorted({load.vehicle_id for load in self._loads(trip)})

    def get_load_count(self, trip):
        return len(self._loads(trip))

    def get_total_weight(self, trip):
        return sum(load.order.weight for load in self._loads(trip))

    def get_total_volume(self, trip):
        return sum(load.order.volume for load in self._loads(trip))

    def get_origin_location_ids(self, trip):
        return sorted({
            load.order.from_location_id
            for load in self._loads(trip)
            if load.order.from_location_id is not None
        })

    def get_destination_location_ids(self, trip):
        return sorted({
            load.order.to_location_id
            for load in self._loads(trip)
            if load.order.to_location_id is not None
        })

    def get_origin_branch_ids(self, trip):
        return sorted({
            load.order.from_branch_id
            for load in self._loads(trip)
            if load.order.from_branch_id is not None
        })

    def get_destination_branch_ids(self, trip):
        return sorted({
            load.order.to_branch_id
            for load in self._loads(trip)
            if load.order.to_branch_id is not None
        })
