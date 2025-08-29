"""
Core models and abstract base classes
"""
from django.db import models
from django.utils import timezone
import uuid


class TimestampedModel(models.Model):
    """Abstract base model with created and updated timestamps"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """Abstract base model with UUID primary key"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class BaseUser(TimestampedModel, UUIDModel):
    """Abstract base user model"""
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.name} ({self.email})"