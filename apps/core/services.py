"""
Core business logic services
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from django.db import transaction
from django.utils import timezone
from apps.sessions.models import Session, SessionStatus
from apps.users.models import Expert, Student

# here why was this abstarction needed?
class SessionValidationService(ABC):
    """Abstract base class for session validation"""
    
    @abstractmethod
    def validate_booking(self, expert: Expert, student: Student, start_at: timezone.datetime, 
                        end_at: timezone.datetime) -> bool:
        """Validate if a booking can be made"""
        pass


class SessionOverlapValidator(SessionValidationService):
    """Concrete implementation for session overlap validation"""
    
    def validate_booking(self, expert: Expert, student: Student, start_at: timezone.datetime, 
                        end_at: timezone.datetime) -> bool:
        """Check if expert has overlapping sessions"""
        overlapping_sessions = Session.objects.filter(
            expert=expert,
            status__in=[SessionStatus.BOOKED, SessionStatus.JOINED, SessionStatus.IN_PROGRESS],
            start_at__lt=end_at,
            end_at__gt=start_at
        ).exclude(student=student)  # Exclude same student for idempotency
        
        return not overlapping_sessions.exists()


class SessionIdempotencyService:
    """Service to handle idempotent session creation"""
    
    def __init__(self, validator: SessionValidationService):
        self.validator = validator
    
    def create_or_get_session(self, expert: Expert, student: Student, start_at: timezone.datetime, 
                             end_at: timezone.datetime) -> tuple[Session, bool]:
        """
        Create a new session or return existing one (idempotent)
        Returns: (session, created)
        """
        # Check for existing session for same student and slot
        existing_session = Session.objects.filter(
            expert=expert,
            student=student,
            start_at=start_at,
            end_at=end_at,
            status=SessionStatus.BOOKED
        ).first()
        
        if existing_session:
            return existing_session, False
        
        # Validate no overlap with other students
        if not self.validator.validate_booking(expert, student, start_at, end_at):
            raise ValueError("Expert has overlapping sessions")
        
        # Create new session
        session = Session.objects.create(
            expert=expert,
            student=student,
            start_at=start_at,
            end_at=end_at
        )
        
        return session, True


class SessionStateService:
    """Service to manage session state transitions"""
    
    @staticmethod
    def join_session(session: Session) -> Session:
        """Mark session as joined"""
        if session.status != SessionStatus.BOOKED:
            raise ValueError("Session cannot be joined in current state")
        
        session.status = SessionStatus.JOINED
        session.joined_at = timezone.now()
        session.save()
        return session
    
    @staticmethod
    def end_session(session: Session) -> Session:
        """Mark session as ended and trigger summary generation"""
        if session.status not in [SessionStatus.JOINED, SessionStatus.IN_PROGRESS]:
            raise ValueError("Session cannot be ended in current state")
        
        session.status = SessionStatus.COMPLETED
        session.ended_at = timezone.now()
        session.save()
        
        # Trigger Celery task for summary generation
        from apps.sessions.tasks import generate_session_summary
        generate_session_summary.delay(str(session.id))
        
        return session