
from celery import shared_task
from django.utils import timezone
from apps.sessions.models import Session


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_session_summary(self, session_id: str):
    try:
        session = Session.objects.get(id=session_id)
        
        # Generate summary
        duration_hours = session.duration_minutes // 60
        duration_minutes = session.duration_minutes % 60
        duration_str = f"{duration_hours:02d}:{duration_minutes:02d}"
        
        summary = (
            f"Session {session.id} — {session.session_name}\n"
            f"Duration: {duration_str}\n"
            f"Expert: {session.expert.name} (ID {session.expert.id})\n"
            f"Student: {session.student.name} (ID {session.student.id})"
        )
        
        #Update session with summary
        session.summary = summary
        session.save(update_fields=['summary'])
        
        return f"Summary generated for session {session_id}"
        
    except Session.DoesNotExist:
        # Session doesn't exist, retry might not help
        return f"Session {session_id} not found"
    except Exception as exc:
        # Retry on transient errors
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        else:
            # Log final failure
            return f"Failed to generate summary for session {session_id} after {self.max_retries} retries"