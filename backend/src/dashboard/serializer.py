from rest_Framework import serializers

from .models import Branch


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = [
            'id',
            'title',
            'longitude',
            'latitude'
        ]
        extra_kwargs = {
            'id': {'read_only':True}
        }