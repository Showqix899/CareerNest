from django import forms 
from django.contrib.auth.forms import BaseUserCreationForm
from django.contrib.auth.forms import AuthenticationForm

from .models import User


class RegisterForm(BaseUserCreationForm):
    full_name = forms.CharField(max_length=150)
    class Meta:
        model = User
        fields = ["full_name","email"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        #bootstrap styling now sot he tmeplates in step 6 stay simple 
        for field in self.fields.values(): 
            field.widget.attrs["class"] = "form-control"
            
        self.fields["full_name"].widget.attrs["placeholder"] = "Your full Name"
        self.fields["email"].widget.attrs["placeholder"] = "you@example.ccom"
        
    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email
    
    def save(self,commit=True):
        
        user = super().save(commit=False)
        user.is_active=False
        if commit:
            user.save()
        return user
    
class LoginForm(AuthenticationForm):
    
    username = forms.EmailField(label="Email")
    
    def __init__(self,*args, **kwargs):
        
        super().__init__(*args,**kwargs)
        
        for field in self.fields.values():
            
            field.widget.attrs["class"]="form-control"

        self.fields["username"].widget.attrs["placeholder"]="you@example.com"
        self.fields["password"].widget.attrs["placeholder"]="Your password"
        
    def clean(self):
        
        email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        
        if email and password:
            
            user = User.objects.filter(email__iexact=email).first()
            if user:
                self.cleaned_data["username"] = user.email
                
                if not user.is_active and user.check_password(password):
                    raise forms.ValidationError(
                        "Your account isnot activated yet .",
                        "please check your email for activation email.",
                        code="inactive"
                    )

        return super().clean()