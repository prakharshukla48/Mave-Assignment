"""
User models for Experts and Students
"""
from django.db import models
from apps.core.models import BaseUser


class Expert(BaseUser):
    """Expert model - can coach students"""
    specialization = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)

    class Meta:
        db_table = 'experts'


class Student(BaseUser):
    """Student model - can book sessions with experts"""
    level = models.CharField(max_length=50, default='beginner')

    class Meta:
        db_table = 'students'