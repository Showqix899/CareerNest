from django.db import models
import uuid
from accounts.models import User
from django.core.exceptions import ValidationError
from admin_panel.models import Skill,City

#user profile 
class UserProfile(models.Model):
    
    id = models.UUIDField(unique=True,primary_key=True,default=uuid.uuid4,editable=False)
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="profiles")
    profile_pic = models.FileField(upload_to='static/profile_pic',null=True,blank=True)
    address=models.TextField(null=True,blank=True)
    city = models.OneToOneField(City,on_delete=models.CASCADE,related_name='cities')
    Skills=models.ManyToManyField(Skill,related_name="skills")
    experiance=models.TextField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        
        return f"{self.user.email}'s profile"
    
#project description 
class ProjectDescription(models.Model):
    
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=100,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
        
    def __str__(self):
        return self.title
    
#prject media
class ProjectMedia(models.Model):
    
    class MediaType(models.TextChoices):
        IMAGE='image','Image'
        VIDEO='video','Video'
        
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(ProjectDescription, on_delete=models.CASCADE, related_name='proj_des')
    file = models.FileField(upload_to='static/project_media/')
    media_type = models.CharField(max_length=10, choices=MediaType.choices)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.media_type} for {self.project.title}"



#user's cv
class CV(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cvs'
    )

    file = models.FileField(upload_to='static/cvs')

    title = models.CharField(max_length=150)

    created_at = models.DateTimeField(auto_now_add=True)
    