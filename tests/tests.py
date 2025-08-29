"""
Tests for session functionality
"""
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from apps.sessions.models import Session, SessionStatus
from apps.users.models import Expert, Student
from apps.sessions.views import book_session, join_session, end_session
from django.test import RequestFactory
from rest_framework.test import APIClient
import json


class SessionTestCase(TestCase):
    """Base test case for sessions"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.client = APIClient()
        
        # Create test users
        self.expert = Expert.objects.create(
            name="Test Expert",
            email="expert@test.com",
            specialization="Python Development"
        )
        
        self.student1 = Student.objects.create(
            name="Test Student 1",
            email="student1@test.com"
        )
        
        self.student2 = Student.objects.create(
            name="Test Student 2",
            email="student2@test.com"
        )
        
        # Test time slots
        self.now = timezone.now()
        self.start_time = self.now + timedelta(hours=1)
        self.end_time = self.start_time + timedelta(hours=1)
        
        # Overlapping time slot
        self.overlap_start = self.start_time + timedelta(minutes=30)
        self.overlap_end = self.end_time + timedelta(minutes=30)


class BookSessionTestCase(SessionTestCase):
    """Test booking sessions"""
    
    def test_happy_path_booking(self):
        """Test successful session booking"""
        data = {
            'expert_id': str(self.expert.id),
            'student_id': str(self.student1.id),
            'start_at': self.start_time.isoformat(),
            'end_at': self.end_time.isoformat()
        }
        
        response = self.client.post('/api/sessions/book/', data, format='json')
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Session.objects.count(), 1)
        
        session = Session.objects.first()
        self.assertEqual(session.status, SessionStatus.BOOKED)
        self.assertEqual(session.expert, self.expert)
        self.assertEqual(session.student, self.student1)
    
    def test_overlap_rejection(self):
        """Test that overlapping sessions are rejected"""
        # Book first session
        Session.objects.create(
            expert=self.expert,
            student=self.student1,
            start_at=self.start_time,
            end_at=self.end_time,
            status=SessionStatus.BOOKED
        )
        
        # Try to book overlapping session with different student
        data = {
            'expert_id': str(self.expert.id),
            'student_id': str(self.student2.id),
            'start_at': self.overlap_start.isoformat(),
            'end_at': self.overlap_end.isoformat()
        }
        
        response = self.client.post('/api/sessions/book/', data, format='json')
        
        self.assertEqual(response.status_code, 409)
        self.assertEqual(Session.objects.count(), 1)  # Only first session exists
    
    def test_idempotent_booking(self):
        """Test that same student can book same slot multiple times"""
        data = {
            'expert_id': str(self.expert.id),
            'student_id': str(self.student1.id),
            'start_at': self.start_time.isoformat(),
            'end_at': self.end_time.isoformat()
        }
        
        # First booking
        response1 = self.client.post('/api/sessions/book/', data, format='json')
        self.assertEqual(response1.status_code, 201)
        
        # Second booking (same data)
        response2 = self.client.post('/api/sessions/book/', data, format='json')
        self.assertEqual(response2.status_code, 200)
        
        # Should only have one session
        self.assertEqual(Session.objects.count(), 1)
        
        # Both responses should return the same session
        self.assertEqual(response1.data['id'], response2.data['id'])


class SessionFlowTestCase(SessionTestCase):
    """Test session flow (join, end)"""
    
    def setUp(self):
        super().setUp()
        # Create a booked session
        self.session = Session.objects.create(
            expert=self.expert,
            student=self.student1,
            start_at=self.start_time,
            end_at=self.end_time,
            status=SessionStatus.BOOKED
        )
    
    def test_join_session(self):
        """Test joining a session"""
        data = {'session_id': str(self.session.id)}
        
        response = self.client.post('/api/sessions/join/', data, format='json')
        
        self.assertEqual(response.status_code, 200)
        
        # Refresh session from database
        self.session.refresh_from_db()
        self.assertEqual(self.session.status, SessionStatus.JOINED)
        self.assertIsNotNone(self.session.joined_at)
    
    def test_end_session(self):
        """Test ending a session"""
        # First join the session
        self.session.status = SessionStatus.JOINED
        self.session.joined_at = timezone.now()
        self.session.save()
        
        data = {'session_id': str(self.session.id)}
        
        response = self.client.post('/api/sessions/end/', data, format='json')
        
        self.assertEqual(response.status_code, 200)
        
        # Refresh session from database
        self.session.refresh_from_db()
        self.assertEqual(self.session.status, SessionStatus.COMPLETED)
        self.assertIsNotNone(self.session.ended_at)
        