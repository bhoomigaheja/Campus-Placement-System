from django.db import models
from core.models import BaseModel

class Branch(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class Skill(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
