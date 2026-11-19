import re
from rest_framework import serializers
from .models import User



#user serializers 
class UserRegisterSerializer(serializers.ModelSerializer):
    
    #password field setup 
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        max_length=100,
        style={"input_style":"password"} #hide text in browseable api
    )
    
    class Meta:
        
        model = User
        fields = ["id","email","full_name","phone","password"]
        read_only_fields=["id"] #no write operation is allowed (it will only show in response)
        
    """validate email (makking the email lowercase and check if the email does already exists or not)"""
    def validate_email(self,value):
        
        value = value.lower()
        
        #check if the email exits or not 
        if User.objects.filter(email__iexact=value).exists():
            
            raise serializers.ValidationError(
                "A user with this email already exists"
            )
            
        return value
    
    
    """validate phone: must containe digits and must not exced or less then 11 in lenght"""
    def validate_phone(self,value):
        
        if value and not value.isdigit():
            raise serializers.ValidationError(
                "phone number must contain digits only"
            )
        return value
    
    
    """validate password password must contains 8 charecters or digts
    must have a speacial charecter and numbers and Uper case and lower case letter"""
    def validate_password(self,value):
        
         # [A-Z] means "any capital letter"
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )

        # [a-z] means "any small letter"
        if not re.search(r"[a-z]", value):
            raise serializers.ValidationError(
                "Password must contain at least one lowercase letter."
            )

        # [0-9] means "any digit"
        if not re.search(r"[0-9]", value):
            raise serializers.ValidationError(
                "Password must contain at least one number."
            )

        # [^A-Za-z0-9] means "anything that is NOT a letter or a digit",
        # which is exactly a special character like @ # $ % ! etc.
        if not re.search(r"[^A-Za-z0-9]", value):
            raise serializers.ValidationError(
                "Password must contain at least one special character."
            )

        return value
    
    """this create the user instance in the database it is called when serializers.save()"""
    def create(self, validated_data):
        
        user = User.objects.create_user(**validated_data)
        return user
        
    