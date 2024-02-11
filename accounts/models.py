from django.db import models
from django.contrib.auth.models import AbstractUser,Group,Permission

# Create your models here.
class CustomUser(AbstractUser):
    is_teacher = models.BooleanField(default=False)
    email = models.EmailField(unique=True)
