
from django import forms
from django.core.exceptions import ValidationError

from .models import Skill, City, ProjectDescription,UserProfile,CV,ProjectMedia


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
            


class MultipleFileInput(forms.FileInput):  # FileInput avoids the "Clear" checkbox
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """A FileField that accepts and validates a list of files."""

    def __init__(self, *args, content_type_prefix=None, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        self.content_type_prefix = content_type_prefix
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean

        if not data:
            return []

        if not isinstance(data, (list, tuple)):
            data = [data]

        files = []
        for f in data:
            cleaned = single_file_clean(f, initial)
            if cleaned is None:
                continue
            # Server-side type check (the `accept` attribute is only a browser hint)
            content_type = getattr(cleaned, "content_type", "") or ""
            if self.content_type_prefix and not content_type.startswith(self.content_type_prefix):
                raise ValidationError(
                    f'"{cleaned.name}" is not a valid {self.content_type_prefix.rstrip("/")} file.'
                )
            files.append(cleaned)
        return files


class ProjectMediaForm(forms.Form):
    images = MultipleFileField(
        widget=MultipleFileInput(attrs={"multiple": True, "accept": "image/*"}),
        required=False,
        content_type_prefix="image/",
    )
    videos = MultipleFileField(
        widget=MultipleFileInput(attrs={"multiple": True, "accept": "video/*"}),
        required=False,
        content_type_prefix="video/",
    )

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop("project", None)
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def clean(self):
        cleaned_data = super().clean()

        if not self.project:
            raise ValidationError("Project instance is required for validation.")

        images = cleaned_data.get("images") or []
        videos = cleaned_data.get("videos") or []

        if not images and not videos:
            raise ValidationError("Please select at least one image or video.")

        existing_images = ProjectMedia.objects.filter(
            project=self.project, media_type=ProjectMedia.MediaType.IMAGE
        ).count()
        existing_videos = ProjectMedia.objects.filter(
            project=self.project, media_type=ProjectMedia.MediaType.VIDEO
        ).count()

        if existing_images + len(images) > 5:
            raise ValidationError(
                f"You currently have {existing_images} images. "
                f"Uploading {len(images)} more exceeds the maximum limit of 5 images."
            )

        if existing_videos + len(videos) > 3:
            raise ValidationError(
                f"You currently have {existing_videos} videos. "
                f"Uploading {len(videos)} more exceeds the maximum limit of 3 videos."
            )

        return cleaned_data

    def save(self):
        saved_media = []

        for img in self.cleaned_data.get("images", []):
            saved_media.append(ProjectMedia.objects.create(
                project=self.project,
                file=img,
                media_type=ProjectMedia.MediaType.IMAGE,
            ))

        for vid in self.cleaned_data.get("videos", []):
            saved_media.append(ProjectMedia.objects.create(
                project=self.project,
                file=vid,
                media_type=ProjectMedia.MediaType.VIDEO,
            ))

        return saved_media