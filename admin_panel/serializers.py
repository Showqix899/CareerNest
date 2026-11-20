from .models import Skill,City
from rest_framework import serializers



#city serialzers
class CitySerializer(serializers.ModelSerializer):
    """this serialzer city name and save in database"""
    class Meta:
        model = City
        fields = ["id","name",]
        read_only_fields = ["id"]
        
    def validate_name(self,value):
        
        value = value.strip().lower() #strip any white space and also make it lowercase
        
        qs=City.objects.filter(name=value)
        
        if qs.exists():
            
            raise serializers.ValidationError(
                "A city with this name already exists"
            )
            
        return value
    
    
    
# serializers.py
class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name"]
        read_only_fields = ["id"]

    def validate_name(self, value):
        value = value.strip().lower()
        qs = Skill.objects.filter(name=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Skill already exists.")
        return value
    