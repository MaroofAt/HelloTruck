from rest_framework import serializers

from .models import Branch , Location


class BranchSerializer(serializers.ModelSerializer):

    longitude = serializers.FloatField(required=False)
    latitude = serializers.FloatField(required=False)

    class Meta:
        model = Branch
        fields = [
            'id',
            'title',
            'location',
            'longitude',
            'latitude'
        ]
        extra_kwargs = {
            'id': {'read_only':True},
            'location': {'required': False}
        }

    def to_representation(self, instance):
        
        ret = super().to_representation(instance)
        if instance.location:
            ret['longitude'] = float(instance.location.longitude)
            ret['latitude'] = float(instance.location.latitude)
        else:
            ret['longitude'] = None
            ret['latitude'] = None
        return ret

    def create (self, validated_data):

        longitude = validated_data.pop("longitude" , None)
        latitude = validated_data.pop("latitude", None)
        # print(longitude)
        # print(latitude)
        if longitude is None or latitude is None:
            raise serializers.ValidationError({
                'non_field_errors': 'Both latitude and longitude are required to create a branch.'
            })

        location , created = Location.objects.get_or_create(
            latitude=latitude, longitude=longitude, 
        )

        branch = Branch.objects.create(
            location = location,
            **validated_data
        )
        branch.save()
        return branch
    
    def update(self , instance , validated_data):
        longitude = validated_data.pop("longitude" , None)
        latitude = validated_data.pop("latitude" , None)
        
        location , created = Location.objects.get_or_create(
            latitude=latitude, longitude=longitude, 
        )

        instance.location = location

        instance.title = validated_data.get("title" , instance.title)

        instance.save()
        return instance
    

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = [
            "id",
            "latitude",
            "longitude"
        ]
