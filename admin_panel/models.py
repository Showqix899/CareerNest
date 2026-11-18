from django.db import models
import uuid

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