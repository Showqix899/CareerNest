
from django import forms

from .models import Skill, City, ProjectDescription,UserProfile,CV


class BootstrapModelForm(forms.ModelForm):
    """Reusable Bootstrap styling for ModelForms."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():

            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({
                    "class": "form-select"
                })

            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    "class": "form-check-input"
                })

            else:
                field.widget.attrs.update({
                    "class": "form-control"
                })


class SkillForm(BootstrapModelForm):

    class Meta:
        model = Skill
        fields = ["name"]

        #adding bootstrap classes
        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "Enter skill name",
            }),
        }


class CityForm(BootstrapModelForm):

    class Meta:
        model = City
        fields = ["name"]
        
        #adding bootstrap classes
        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "Enter city name",
            }),
        }


class ProjectDescriptionForm(BootstrapModelForm):

    class Meta:
        model = ProjectDescription
        fields = ["title", "description"]

        #adding bootstrap classes
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter project title...",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Describe your project...",
            }),
        }
        

class UserProfileForm(forms.ModelForm):
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        
        #adding bootstrap classes
        for field in self.fields.values():
            field.widget.attrs["class"]="form-control"
            
        self.fields["phone"].widget.attrs["placeholder"]="Your Phone Number"
        self.fields["address"].widget.attrs["placeholder"]="Your Address"
        self.fields["city"].widget.attrs["placeholder"]="City"
        self.fields["address"].widget.attrs["placeholder"]="Your Address"
        self.fields["skills"].widget.attrs["placeholder"]="Your Skills"
        self.fields["experience"].widget.attrs["placeholder"]="Your Work Experience"
        

    class Meta:
        model = UserProfile
        fields = [
            "profile_pic",
            "phone",
            "address",
            "city",
            "skills",
            "experience",
        ]
        
        widgets = {
            "skills":forms.SelectMultiple(),
        }
        
    def clean_skills(self):

        skills = self.cleaned_data.get("skills")

        if skills.count() > 12:
            raise forms.ValidationError(
                "You can select a maximum of 12 skills."
            )

        return skills


        
class UserCVForms(forms.ModelForm):
    class Meta:
        model = CV
        fields = ["title", "file"] # Make sure these match your CV model fields
        
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "CV Title (e.g., Software Engineer CV)"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"