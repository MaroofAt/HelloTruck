
from rest_framework import serializers

from .models import Order
from users.models import Credential , Trader 
from dashboard.models import Branch , Location 
from .models import Special_Shipment

import math


class OrderSerializer(serializers.ModelSerializer):
    from_branch = serializers.IntegerField(required=False, allow_null=True)
    special_shipment = serializers.IntegerField(required=False, allow_null=True)
    trader = serializers.PrimaryKeyRelatedField(
        queryset=Trader.objects.all(),
        required=True
    )
    from_branch = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.all(),
        required=False,
        allow_null=True
    )
    # destination = serializers.PrimaryKeyRelatedField(
    #     queryset=Location.objects.all(),
    #     required=True
    # )
    special_shipment = serializers.PrimaryKeyRelatedField(
        queryset=Special_Shipment.objects.all(),
        required=False,
        allow_null=True
    )
    longitude = serializers.FloatField(write_only=True)
    latitude = serializers.FloatField(write_only = True)
    class Meta:
        model = Order
        fields = [
            'id',
            'volume',
            'weight', 
            'goods_type',
            'price',
            'distance',
            'delivery',
            'shipment_type',
            'trader',
            'destination',
            'from_branch',
            'special_shipment',
            'longitude',
            'latitude'
        ]
        extra_kwargs = {
            'destination': {'required': False}
        }
        read_only_fields = ['price' , 'distance']
    
    def validate(self, data):
        if data.get('volume', 0) <= 0:
            raise serializers.ValidationError({
                'volume': 'Volume must be greater than 0'
            })
        
        if data.get('weight', 0) <= 0:
            raise serializers.ValidationError({
                'weight': 'Weight must be greater than 0'
            })
        
        return data

    # def validate_distance(self, value):
        
    #     if value and not value.endswith('km'):
    #         return f"{value}km"
    #     return value
    
    def validate_trader(self, value):
        
        try:
            if value.credentials.role != Credential.Role.TRADER:
                raise serializers.ValidationError("User is not a trader")
        except Credential.DoesNotExist:
            raise serializers.ValidationError("Trader does not exist")
        return value
    

    def create(self, validated_data):
        longitude = validated_data.pop("longitude")
        latitude = validated_data.pop("latitude")

        validated_data["destination"] , created = Location.objects.get_or_create(
            latitude=latitude, longitude=longitude, 
        )
        
        print(validated_data["destination"] ,"////////////////////////////////////////////////////")

        price = self.calculate_price(validated_data)
        distance = self.calculate_distance( validated_data["from_branch"] , validated_data["destination"])
        validated_data['price'] = price
        validated_data["distance"] = distance
        
        order = Order.objects.create(**validated_data)
        return order
    

    def update(self, instance , validated_data):
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        
        instance.price = self.calculate_price({
            'volume': instance.volume,
            'weight': instance.weight,
            'goods_type': instance.goods_type,
            'distance': instance.distance,
            'delivery': instance.delivery,
            'shipment_type': instance.shipment_type,
        })
        
        instance.save()
        return instance
    

    def calculate_distance(self , from_branch , destination):
        # damascuse 
            # Latitude: 33.518529
            # Longitude: 36.302309
        
        # homs 
            # Latitude: 34.731826 
            # Longitude: 36.711907

        # suwayda
            # Latitude: 32.706028
            # Longitude: 36.581003

        branch1 = Branch.objects.filter(pk = from_branch.id).first()
        # branch2 = Branch.objects.filter(pk = destination.id).first()
        locatio1 = Location.objects.filter(pk=branch1.id).first()
        locatio2 = Location.objects.filter(pk = destination.id).first()

        lat1 = locatio1.latitude
        lon1 = locatio1.longitude
        lat2 = locatio2.latitude
        lon2 = locatio2.longitude

        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))

        r = 6371
        return round(c*r)

    def calculate_price(self, data):
        return 500
    
