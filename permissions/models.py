from django.db import models

class Permission(models.Model):
    name = models.CharField(max_length=30, unique=True)
    code = models.SlugField(max_length=30, unique=True)
    
    def __str__(self) -> str:
        return self.name
