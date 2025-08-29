# models needed for sessions after coaching is booked
from django.db import models
from django.core.exceptions import ValidationError
from apps.core.models import TimestampedModel, UUIDModel
from apps.users.models import Expert, Student


class SessionStatus(models.TextChoices):
    BOOKED = 'BOOKED', 'Booked'
    JOINED = 'JOINED', 'Joined'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    COMPLETED = 'COMPLETED', 'Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'


class Session(TimestampedModel, UUIDModel):
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE, related_name='sessions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='sessions')
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=SessionStatus.choices, default=SessionStatus.BOOKED)
    joined_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    summary = models.TextField(blank=True)
    
    class Meta:
        db_table = 'sessions'
        indexes = [
            models.Index(fields=['expert', 'start_at', 'end_at']),
            models.Index(fields=['student', 'start_at', 'end_at']),
            models.Index(fields=['status']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_at__gt=models.F('start_at')),
                name='session_end_after_start'
            ),
        ] # end should always be greater than start time

    def clean(self):
        if self.start_at and self.end_at and self.start_at >= self.end_at:
            raise ValidationError("End time must be after start time")
        
        if self.start_at and self.start_at < timezone.now():
            raise ValidationError("Start time cannot be in the past")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Session {self.id} - {self.expert.name} & {self.student.name} @ {self.start_at}"

    @property
    def duration_minutes(self):
        if self.start_at and self.end_at:
            return int((self.end_at - self.start_at).total_seconds() / 60)
        return 0

    @property
    def session_name(self):
        return f"- @ {self.start_at.strftime('%Y-%m-%d %H:%M UTC')}"