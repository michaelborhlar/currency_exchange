from rest_framework import serializers
from .models import Country, RefreshStatus


class CountrySerializer(serializers.ModelSerializer):
    class Meta: 
        model = Country
        fields = "__all__"
        
    def get_estimated_gdp(self, obj):
        if obj.estimated_gdp is None:
            return None
        # obj.estimated_gdp may be Decimal — convert to float
        try:
            return float(obj.estimated_gdp)
        except Exception:
            return None


        
class RefreshStatusSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = RefreshStatus
        fields = '__all__'
