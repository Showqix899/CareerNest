from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)

from django.db import models
from django.utils import timezone
import uuid


class UserManager(BaseUserManager):
    
    def create_user(self,email,password=None,**extra_fields):
        
        if not email:
            raise ValueError("Users must have an email address")
        
        #normalize email lowercase the domain part
        email = self.normalize_email(email)
        
        user = self.model(email=email,**extra_fields) #build the user object 
        user.set_password(password) #hash password
        user.save(using=self._db) #now write to the database
        
        return user
    
    def create_superuser(self,email,password=None, **extra_fields):
        
        #A super user with flags switched on 
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        return self.create_user(email,password,**extra_fields)
    

class User(AbstractBaseUser,PermissionsMixin):
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    email = models.EmailField(unique=True)           # unique=True is REQUIRED for the login field
    full_name = models.CharField(max_length=150)

    is_active = models.BooleanField(default=True)    # False = account disabled, can't log in
    is_staff = models.BooleanField(default=False)    # True = can access /admin/
    date_joined = models.DateTimeField(default=timezone.now)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    
    def __str__(self):
        return self.email