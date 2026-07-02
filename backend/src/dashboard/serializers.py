from rest_framework import serializers

from .models import Branch , Location


class BranchSerializer(serializers.ModelSerializer):

    longitude = serializers.FloatField(write_only=True)
    latitude = serializers.FloatField(write_only = True)

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

    def create (self, validated_data):

        longitude = validated_data.pop("longitude")
        latitude = validated_data.pop("latitude")

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
