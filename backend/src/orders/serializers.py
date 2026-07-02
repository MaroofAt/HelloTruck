
from rest_framework import serializers

from .models import Order
from users.models import Credential


class OrderSerializer(serializers.ModelSerializer):
    from_branch = serializers.IntegerField(required=False, allow_null=True)
    special_shipment = serializers.IntegerField(required=False, allow_null=True)
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
            'special_shipment'
        ]
        read_only_fields = ['price']
    
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

    def validate_distance(self, value):
        
        if value and not value.endswith('km'):
            return f"{value}km"
        return value
    
    def validate_trader(self, value):
        
        try:
            trader = Credential.objects.get(id=value)
            if trader.role != Credential.Role.TRADER:
                raise serializers.ValidationError("User is not a trader")
        except Credential.DoesNotExist:
            raise serializers.ValidationError("Trader does not exist")
        return value
    
    def create(self, validated_data):
        
    
        price = self.calculate_price(validated_data)
        validated_data['price'] = price
        
        
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
    
    def calculate_price(self, data):
        return 500