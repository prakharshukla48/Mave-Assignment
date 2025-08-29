from rest_framework import serializers
from apps.sessions.models import Session, SessionStatus
from apps.users.models import Expert, Student


class ExpertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expert
        fields = ['id', 'name', 'email', 'specialization', 'bio']


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name', 'email', 'level']


class SessionSerializer(serializers.ModelSerializer):
    expert = ExpertSerializer(read_only=True)
    student = StudentSerializer(read_only=True)
    duration_minutes = serializers.ReadOnlyField()
    session_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Session
        fields = [
            'id', 'expert', 'student', 'start_at', 'end_at', 'status',
            'joined_at', 'ended_at', 'summary', 'duration_minutes',
            'session_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'joined_at', 'ended_at', 'summary', 'created_at', 'updated_at']


class BookSessionSerializer(serializers.Serializer):
    expert_id = serializers.UUIDField()
    student_id = serializers.UUIDField()
    start_at = serializers.DateTimeField()
    end_at = serializers.DateTimeField()
    
    def validate(self, attrs):
        """Validate booking data"""
        if attrs['start_at'] >= attrs['end_at']:
            raise serializers.ValidationError("End time must be after start time")
        
        if attrs['start_at'] < timezone.now():
            raise serializers.ValidationError("Start time cannot be in the past")
        
        return attrs


class JoinSessionSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()


class EndSessionSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()