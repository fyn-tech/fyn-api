from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import model_to_dict
import uuid

class User(AbstractUser, models.Model):    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.username} {self.id}"