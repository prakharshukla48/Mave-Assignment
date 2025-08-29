"""
Management script to create test data
"""
import os
import django
from datetime import timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coaching_sessions.settings')
django.setup()

from apps.users.models import Expert, Student
from apps.sessions.models import Session, SessionStatus
from django.utils import timezone


def create_test_data():
    """Create sample data for testing"""
    # Create experts
    expert1 = Expert.objects.create(
        name="John Doe",
        email="john.doe@example.com",
        specialization="Python Development"
    )
    
    expert2 = Expert.objects.create(
        name="Jane Smith",
        email="jane.smith@example.com",
        specialization="Data Science"
    )
    
    # Create students
    student1 = Student.objects.create(
        name="Alice Johnson",
        email="alice.johnson@example.com",
        level="beginner"
    )
    
    student2 = Student.objects.create(
        name="Bob Wilson",
        email="bob.wilson@example.com",
        level="intermediate"
    )
    
    # Create some sessions
    now = timezone.now()
    
    # Past completed session
    Session.objects.create(
        expert=expert1,
        student=student1,
        start_at=now - timedelta(days=1, hours=2),
        end_at=now - timedelta(days=1, hours=1),
        status=SessionStatus.COMPLETED,
        joined_at=now - timedelta(days=1, hours=2),
        ended_at=now - timedelta(days=1, hours=1),
        summary="Test session summary"
    )
    
    # Future booked session
    Session.objects.create(
        expert=expert2,
        student=student2,
        start_at=now + timedelta(hours=2),
        end_at=now + timedelta(hours=3),
        status=SessionStatus.BOOKED
    )
    
    print("Test data created successfully!")
    print(f"Created {Expert.objects.count()} experts")
    print(f"Created {Student.objects.count()} students")
    print(f"Created {Session.objects.count()} sessions")


if __name__ == '__main__':
    create_test_data()