
from rest_framework import serializers

from .models import Order
from users.models import Credential , Trader 
from dashboard.models import Branch , Location 
from .models import Special_Shipment

import math
from decimal import Decimal, ROUND_HALF_UP

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
        
        #validate the branch and location here (note making the request have the both ) TODO
        if data.get('from_branch') is not None and data.get('to_branch') is not None:

            if data.get("longitude_from") is not None or data.get("longitude_to") is not None or data.get("latitude_to") is not None or data.get("latitude_from") is not None :
                # print("///////////////////////////////////////////////////////////")
                raise serializers.ValidationError({
                    'location': 'you should choose one from and to direction'
                })

        # if data.get('from_location') is not None and data.get('to_location') is not None:
        #     if data.get("from_branch") is not None or data.get("to_branch") is not None:
        #         raise serializers.ValidationError({
        #             'location': 'you should choose one from and to direction'
        #         }) 

        if (data.get("longitude_from") is not None and data.get("latitude_from") is None) or (data.get("latitude_from") is not None and data.get("longitude_from") is None):
            raise serializers.ValidationError({
                    'location': 'you should select the longitude_from and latitude_from not one of them'
                })
        
        if (data.get("longitude_to") is not None and data.get("latitude_to") is None) or (data.get("latitude_to") is not None and data.get("longitude_to") is None):
            raise serializers.ValidationError({
                    'location': 'you should select the longitude_to and latitude_to not one of them'
                })
        
        if data.get("longitude_from") is not None and data.get("longitude_to") is not None and data.get("latitude_to") is not None and data.get("latitude_from") is not None :
            if data.get('from_branch') is not None or data.get('to_branch') is not None:
                raise serializers.ValidationError({
                    'location': 'you should choose one from and to direction'
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
        longitude_from = validated_data.pop("longitude_from" , None)
        latitude_from = validated_data.pop("latitude_from" , None)
        longitude_to = validated_data.pop("longitude_to" , None)
        latitude_to = validated_data.pop("latitude_to" , None)


        if longitude_from == '':
            longitude_from = None
        if latitude_from == '':
            latitude_from = None
        if longitude_to == '':
            longitude_to = None
        if latitude_to == '':
            latitude_to = None

        if longitude_from is not None and latitude_from is not None:
            from_location, created = Location.objects.get_or_create(
                latitude=latitude_from,
                longitude=longitude_from
            )
            validated_data["from_location"] = from_location
    
    # Create or get to_location
        if longitude_to is not None and latitude_to is not None:
            to_location, created = Location.objects.get_or_create(
                latitude=latitude_to,
                longitude=longitude_to
            )
            validated_data["to_location"] = to_location
        

        delivery = validated_data.get("delivery")
        from_branch = validated_data.get("from_branch")
        to_branch = validated_data.get("to_branch")
        from_location = validated_data.get("from_location") 
        to_location = validated_data.get("to_location") 
    
        # created = Location.objects.get_or_create(
        #     latitude_from=latitude_from, longitude_from=longitude_from,  latitude_to=latitude_to,longitude_to=longitude_to
        # )

        
        # print(validated_data["longitude_from"] ,"////////////////////////////////////////////////////" ,  validated_data["longitude_to"])

        price = self.calculate_price(validated_data)
        
        if delivery == True and from_branch == None and to_branch == None:

            distance = self.calculate_distance( from_location , to_location)

        elif delivery == False and from_location == None and to_location == None:

            distance = self.calculate_distance( from_branch , to_branch)

        elif delivery == True and from_branch == None and to_location == None:
        
            distance = self.calculate_distance( from_location , to_branch)

        elif delivery == True and from_location == None and to_branch == None:
                        
            distance = self.calculate_distance( from_branch , to_location)

        else:
            raise serializers.ValidationError({
                "you should revers the delivery flag or you'r entering the same from/to "
            })
        
            
        validated_data['price'] = price
        validated_data["distance"] = distance
        
        order = Order.objects.create(**validated_data)
        return order
    

    def partial_update(self, instance , validated_data):
        # print("//////////////////////////////////////////////////////////")
        longitude_from = validated_data.pop("longitude_from" , None)
        latitude_from = validated_data.pop("latitude_from" , None)
        longitude_to = validated_data.pop("longitude_to" , None)
        latitude_to = validated_data.pop("latitude_to" , None)
        
        if longitude_from == '':
            longitude_from = None
        if latitude_from == '':
            latitude_from = None
        if longitude_to == '':
            longitude_to = None
        if latitude_to == '':
            latitude_to = None

        if longitude_from is not None and latitude_from is not None:
            from_location, created = Location.objects.get_or_create(
                latitude=latitude_from,
                longitude=longitude_from
            )
            validated_data["from_location"] = from_location
    
        if longitude_to is not None and latitude_to is not None:
            to_location, created = Location.objects.get_or_create(
                latitude=latitude_to,
                longitude=longitude_to
            )
            validated_data["to_location"] = to_location


        delivery = validated_data.get("delivery") | instance.delivery
        from_branch = validated_data.get("from_branch") | instance.from_branch
        to_branch = validated_data.get("to_branch") | instance.to_branch
        from_location = validated_data.get("from_location") | instance.from_location
        to_location = validated_data.get("to_location") | instance.to_location  
    
        # created = Location.objects.get_or_create(
        #     latitude_from=latitude_from, longitude_from=longitude_from,  latitude_to=latitude_to,longitude_to=longitude_to
        # )

        
        # print(validated_data["longitude_from"] ,"////////////////////////////////////////////////////" ,  validated_data["longitude_to"])

        # price = self.calculate_price(validated_data)

        print(from_branch , to_branch , from_location ,to_location)
        
        if delivery == True and from_branch == None and to_branch == None:

            distance = self.calculate_distance( from_location , to_location)

        elif delivery == False and from_location == None and to_location == None:

            distance = self.calculate_distance( from_branch , to_branch)

        elif delivery == True and from_branch == None and to_location == None:
        
            distance = self.calculate_distance( from_location , to_branch)

        elif delivery == True and from_location == None and to_branch == None:
                        
            distance = self.calculate_distance( from_branch , to_location)

        else:
            raise serializers.ValidationError({
                "you should revers the delivery flag or you'r entering the same from/to "
            })


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
            site1 = site1.first()
            location1 = Location.objects.filter(pk=site1.id).first()

        else:
            location1 = Location.objects.filter(pk=fromm.id).first()
        

        if site2.exists():
            site2 = site2.first()

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
        # return 500
        """
        Calculate order price based on multiple factors.
        
        Args:
            data: Dictionary containing order data with keys:
                - volume (float): Volume in cubic meters
                - weight (float): Weight in kg
                - goods_type (str): Type of goods
                - distance (str): Distance in km (e.g., "100km")
                - delivery (bool): Delivery flag
                - shipment_type (str): Type of shipment
                - special_shipment (bool/None): Special shipment indicator
        
        Returns:
            float: Calculated price
        """
        
        # Extract and parse data
        volume = float(data.get('volume', 0))
        weight = float(data.get('weight', 0))
        goods_type = data.get('goods_type', 'normal')
        distance_str = data.get('distance', '0km')
        delivery = data.get('delivery', False)
        shipment_type = data.get('shipment_type', 'LTL')
        special_shipment = data.get('special_shipment')
        
        # Parse distance to numeric value
        try:
            distance = float(distance_str.lower().replace('km', '').strip())
        except (ValueError, AttributeError):
            distance = 0.0
        
        # ============================================
        # 1. BASE RATE CALCULATIONS
        # ============================================
        
        # Base rate per unit (can be adjusted)
        base_rate = 10
        
        # Volume and weight rates
        volume_rate = base_rate * volume
        weight_rate = base_rate * weight * 0.5  # Weight is less impactful
        
        # Combined base price
        base_price = volume_rate + weight_rate
        
        # ============================================
        # 2. GOODS TYPE MULTIPLIER AND SURCHARGES
        # ============================================
        
        # Goods type multiplier
        goods_multipliers = {
            'liquid': 1.5,
            'need_refrigeration': 2.0,
            'normal_breakable': 1.3,
            'normal': 1.0
        }
        goods_multiplier = goods_multipliers.get(goods_type, 1.0)
        
        # Goods type handling fees
        handling_fees = {
            'liquid': 50.0,
            'need_refrigeration': 100.0,
            'normal_breakable': 30.0,
            'normal': 20.0
        }
        handling_fee = handling_fees.get(goods_type, 20.0)
        
        # Surcharges based on goods type
        surcharge = 0.0
        if goods_type == 'liquid':
            surcharge += base_price * 0.15  # 15% safety surcharge
        elif goods_type == 'need_refrigeration':
            surcharge += base_price * 0.25  # 25% refrigeration surcharge
            if distance > 100:  # Extra cooling charge for long distance
                surcharge += distance * 0.5
        elif goods_type == 'normal_breakable':
            surcharge += base_price * 0.10  # 10% breakable surcharge
            surcharge += 10.0  # Packaging fee
        
        # Apply goods multiplier
        base_price *= goods_multiplier
        
        # ============================================
        # 3. DISTANCE-BASED PRICING
        # ============================================
        
        # Distance rates based on shipment type
        distance_rates = {
            'LTL': 2.5,
            'EUV': 3.0,
            'SPECIAL_SHIPMENT': 5.0,
            'FROM_BRANCH': 2.0,
            'TO_BRANCH': 2.0,
            'ecommerce_delivery': 3.5
        }
        distance_rate = distance_rates.get(shipment_type, 2.5)
        
        # Base distance price
        distance_price = distance * distance_rate
        
        # Additional distance charges
        if distance > 200:
            distance_price += (distance - 200) * 1.5  # Long distance surcharge
        elif distance > 100:
            distance_price += (distance - 100) * 0.5  # Medium distance surcharge
        
        # ============================================
        # 4. VOLUME AND WEIGHT ADJUSTMENTS
        # ============================================
        
        # Volume-weight ratio (1 cubic meter = 250 kg)
        volume_weight_ratio = 250
        weight_equivalent = volume * volume_weight_ratio
        
        # Effective weight (use the greater of actual weight or volume-equivalent)
        effective_weight = max(weight, weight_equivalent)
        
        # Volume and weight based pricing
        volume_weight_price = effective_weight * 0.3
        
        # Apply shipment type volume/weight multipliers
        shipment_multipliers = {
            'LTL': {'volume': 1.0, 'weight': 1.0},
            'EUV': {'volume': 1.2, 'weight': 1.1},
            'SPECIAL_SHIPMENT': {'volume': 1.5, 'weight': 1.3},
            'FROM_BRANCH': {'volume': 0.9, 'weight': 0.9},
            'TO_BRANCH': {'volume': 0.9, 'weight': 0.9},
            'ecommerce_delivery': {'volume': 1.1, 'weight': 1.0}
        }
        multipliers = shipment_multipliers.get(shipment_type, {'volume': 1.0, 'weight': 1.0})
        
        volume_weight_price *= (multipliers['volume'] + multipliers['weight']) / 2
        
        # ============================================
        # 5. DELIVERY FEES
        # ============================================
        
        delivery_fee = 0.0
        if delivery:
            delivery_fee = 50.0  # Base delivery fee
            delivery_fee += distance * 0.5  # Per km delivery fee
            
            # Add delivery surcharge (10% of base price)
            delivery_surcharge = base_price * 0.10
            delivery_fee += delivery_surcharge
        
        # ============================================
        # 6. SHIPMENT TYPE SPECIFIC ADJUSTMENTS
        # ============================================
        
        shipment_adjustment = 0.0
        
        if shipment_type == 'ecommerce_delivery':
            shipment_adjustment += base_price * 0.08  # 8% ecommerce surcharge
            shipment_adjustment += 30.0  # Ecommerce handling fee
        
        elif shipment_type == 'FROM_BRANCH':
            shipment_adjustment += 25.0  # Branch pickup fee
            if not delivery:
                shipment_adjustment -= 10.0  # Discount for branch pickup
        
        elif shipment_type == 'TO_BRANCH':
            shipment_adjustment += 25.0  # Branch delivery fee
            if not delivery:
                shipment_adjustment -= 10.0  # Discount for branch delivery
        
        elif shipment_type == 'SPECIAL_SHIPMENT':
            shipment_adjustment += 200.0  # Special handling fee
            if special_shipment:
                shipment_adjustment += 100.0  # Additional special shipment fee
        
        # ============================================
        # 7. MINIMUM CHARGE CHECK
        # ============================================
        
        # Minimum charges based on shipment type
        min_charges = {
            'LTL': 100.0,
            'EUV': 150.0,
            'SPECIAL_SHIPMENT': 500.0,
            'FROM_BRANCH': 50.0,
            'TO_BRANCH': 50.0,
            'ecommerce_delivery': 120.0
        }
        min_charge = min_charges.get(shipment_type, 100.0)
        
        # ============================================
        # 8. CALCULATE TOTAL
        # ============================================
        
        # Sum all components
        total = (
            base_price +           # Base price with goods multiplier
            distance_price +       # Distance-based pricing
            volume_weight_price +  # Volume and weight pricing
            surcharge +            # Goods type surcharges
            handling_fee +         # Handling fees
            delivery_fee +         # Delivery fees
            shipment_adjustment    # Shipment type adjustments
        )
        
        # Apply minimum charge if total is less
        if total < min_charge:
            total = min_charge
        
        # Add margin (profit)
        margin_percentage = 0.20  # 20% margin
        total *= (1 + margin_percentage)
        
        # Round to 2 decimal places
        total = Decimal(str(total)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        return float(total)
    
