from django.db import models
import uuid
from accounts.models import User
from django.core.exceptions import ValidationError

# Create your models here.



#skilss
class Skill(models.Model):
    
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    name = models.CharField(max_length=100,unique=True)
    
    def __str__(self):
        return self.name
    

#citys
class City(models.Model):
    
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
#project description 
class ProjectDescription(models.Model):
    
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=100,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
        
    def __str__(self):
        return self.title


#user profle
class UserProfile(models.Model):
    
    id = models.UUIDField(unique=True,primary_key=True,default=uuid.uuid4,editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profiles')
    profile_pic=models.FileField(upload_to='static/profile_pics',null=True,blank=True)
    phone = models.CharField(max_length=13,null=True,blank=True)
    address = models.TextField(max_length=255)
    city = models.ForeignKey(City,related_name="profiles",on_delete=models.CASCADE)
    skills = models.ManyToManyField(Skill,related_name="profiles")
    experience = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(
                fields=['-created_at'],
                name='profile_created_idx'
            )
        ]
    
    def __str__(self):
        return f"{self.user.email}'s Profile"


#user profle
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
    
    
    
    
    

    
    
    

    
    
    
    
    
    
    