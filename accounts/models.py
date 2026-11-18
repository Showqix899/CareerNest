from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)
import uuid
from django.utils import timezone
# Create your models here.


class UserManager(BaseUserManager):
    
    def create_user(self,email,password=None,**extrafield):
        
        if not email:
            raise ValueError("Users must have an email address")
        
        #normalize email lowercase the domain part 
        email = self.normalize_email(email)
        
        user = self.model(email=email,**extrafield)
        user.set_password(password) #hash password 
        user.save(using=self._db) #now write to the database 
        
        return user
    
    def create_superuser(self,email,password=None,**extrafields):
        
        #A super user with flags switched on 
        extrafields.setdefault('is_staff',True)
        extrafields.setdefault('is_superuser',True)
        return self.create_user(email,password,**extrafields)


""" Custom User Model """
class User(AbstractBaseUser,PermissionsMixin):
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    email = models.EmailField(unique=True)
    full_name=models.CharField(max_length=150)
    phone=models.CharField(max_length=11,null=True,blank=True)
    is_active=models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    objects= UserManager() #to apply custom method
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS=['full_name']
    
    def __str__(self):
        return self.email
    
    
    