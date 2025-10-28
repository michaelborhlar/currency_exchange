from rest_framework import serializers
from .models import Country, RefreshStatus


class CountrySerializer(serializers.ModelSerializer):
    class Meta: 
        model = Country
        fields = "__all__"
        
class RefreshStatusSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = RefreshStatus
        fields = '__all__'
