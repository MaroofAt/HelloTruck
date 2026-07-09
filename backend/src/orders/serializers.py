
from rest_framework import serializers

from .models import Order
from users.models import Credential , Trader 
from dashboard.models import Branch , Location 
from .models import Special_Shipment

import math


class OrderSerializer(serializers.ModelSerializer):
    # from_branch = serializers.IntegerField(required=False, allow_null=True)
    # special_shipment = serializers.IntegerField(required=False, allow_null=True)
    trader = serializers.PrimaryKeyRelatedField(
        queryset=Trader.objects.all(),
        required=True
    )
    from_branch = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.all(),
        required=False,
        allow_null=True
    )
    to_branch = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.all(),
        required=False,
        allow_null=True
    )
    from_location = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        required=False,
        allow_null=True
    )
    to_location = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
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
    longitude_from = serializers.FloatField(write_only=True , required=False , allow_null=True)
    latitude_from = serializers.FloatField(write_only = True , required=False , allow_null=True)
    longitude_to = serializers.FloatField(write_only=True , required=False , allow_null=True)
    latitude_to = serializers.FloatField(write_only = True , required=False , allow_null=True)
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
            # 'destination',
            'from_branch',
            'to_branch',
            'from_location',
            'to_location',
            'special_shipment',
            'longitude_from',
            'latitude_from',
            'longitude_to',
            'latitude_to',
        ]
        extra_kwargs = {
            'from_location': {'required': False},
            'to_location': {'required': False},
            'from_branch': {'required': False},
            'to_branch': {'required': False},

            'longitude_from': {'required': False},
            'latitude_from': {'required': False},
            'longitude_to': {'required': False},
            'latitude_to': {'required': False},
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
        longitude_from = validated_data.pop("longitude_from")
        latitude_from = validated_data.pop("latitude_from")
        longitude_to = validated_data.pop("longitude_to")
        latitude_to = validated_data.pop("latitude_to")

        if longitude_from != None and latitude_from != None:
            validated_data["from_location"] , created = Location.objects.get_or_create(
                latitude=latitude_from, longitude=longitude_from
            )

        if longitude_to != None and latitude_to != None:
            validated_data["to_location"] , created = Location.objects.get_or_create(
                latitude=latitude_to,longitude=longitude_to
            )
        
    
        # created = Location.objects.get_or_create(
        #     latitude_from=latitude_from, longitude_from=longitude_from,  latitude_to=latitude_to,longitude_to=longitude_to
        # )

        
        # print(validated_data["destination"] ,"////////////////////////////////////////////////////")

        price = self.calculate_price(validated_data)
        
        if validated_data["delivery"] == True and validated_data["from_branch"] == None and validated_data["to_branch"] == None:

            distance = self.calculate_distance( validated_data["from_location"] , validated_data["to_location"])

        elif validated_data["delivery"] == False and validated_data["from_location"] == None and validated_data["to_location"] == None:

            distance = self.calculate_distance( validated_data["from_branch"] , validated_data["to_branch"])

        elif validated_data["delivery"] == True and validated_data["from_branch"] == None and validated_data["to_location"] == None:
        
            distance = self.calculate_distance( validated_data["from_location"] , validated_data["to_branch"])

        elif validated_data["delivery"] == True and validated_data["from_location"] == None and validated_data["to_branch"] == None:
                        
            distance = self.calculate_distance( validated_data["from_branch"] , validated_data["to_location"])

        else:
            raise serializers.ValidationError({
                "you should revers the delivery flag"
            })
        
            
        validated_data['price'] = price
        validated_data["distance"] = distance
        
        order = Order.objects.create(**validated_data)
        return order
    

    def partial_update(self, instance , validated_data):
        # print("//////////////////////////////////////////////////////////")
        longitude_from = validated_data.pop("longitude")
        latitude_from = validated_data.pop("latitude")
        longitude_to = validated_data.pop("longitude")
        latitude_to = validated_data.pop("latitude")

        validated_data["destination"] , created = Location.objects.get_or_create(
            latitude_from=latitude_from, longitude_from=longitude_from,  latitude_to=latitude_to,longitude_to=longitude_to
        )
        
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
    

    def calculate_distance(self , fromm , to):
        print("//////////////////////////////////////////////////////////////////////////////////")
        # damascuse 
            # Latitude: 33.518529
            # Longitude: 36.302309
        
        # homs 
            # Latitude: 34.731826 
            # Longitude: 36.711907

        # suwayda
            # Latitude: 32.706028
            # Longitude: 36.581003
        
        site1 = Branch.objects.filter(pk = fromm.id)

        site2 = Branch.objects.filter(pk = to.id)

        if site1.exists():
            location1 = Location.objects.filter(pk=site1.id).first()

        else:
            location1 = Location.objects.filter(pk=fromm.id).first()
        

        if site2.exists():
            location2 = Location.objects.filter(pk = site2.id).first()

        else :
            location2 = Location.objects.filter(pk = to.id).first()


        
        # branch1 = Branch.objects.filter(pk = fromm.id).first()
        # # branch2 = Branch.objects.filter(pk = destination.id).first()
        # location1 = Location.objects.filter(pk=branch1.id).first()
        # location2 = Location.objects.filter(pk = to.id).first()

        lat1 = location1.latitude
        lon1 = location1.longitude
        lat2 = location2.latitude
        lon2 = location2.longitude

        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))

        r = 6371
        return round(c*r)

    def calculate_price(self, data):
        return 500
    
