from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from apps.sessions.models import Session
from apps.users.models import Expert, Student
from apps.sessions.serializers import (
    SessionSerializer, BookSessionSerializer, 
    JoinSessionSerializer, EndSessionSerializer
)
from apps.core.services import SessionIdempotencyService, SessionOverlapValidator, SessionStateService


@api_view(['POST'])
def book_session(request):
    serializer = BookSessionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # this will make sure the race condition is handled when two users try to book at same time
        with transaction.atomic():
            # Get expert and student
            expert = get_object_or_404(Expert, id=serializer.validated_data['expert_id'])
            student = get_object_or_404(Student, id=serializer.validated_data['student_id'])
            
            # Create session service
            validator = SessionOverlapValidator()
            session_service = SessionIdempotencyService(validator)
            
            # Create or get session
            session, created = session_service.create_or_get_session(
                expert=expert,
                student=student,
                start_at=serializer.validated_data['start_at'],
                end_at=serializer.validated_data['end_at']
            )
            
            # Serialize response
            session_serializer = SessionSerializer(session)
            
            if created:
                return Response(session_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(session_serializer.data, status=status.HTTP_200_OK)
                
    except ValueError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_409_CONFLICT
        )
    except Exception as e:
        return Response(
            {'error': 'Internal server error'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def join_session(request):
    serializer = JoinSessionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        session = get_object_or_404(Session, id=serializer.validated_data['session_id'])
        session = SessionStateService.join_session(session)
        
        session_serializer = SessionSerializer(session)
        return Response(session_serializer.data, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': 'Internal server error'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def end_session(request):
    serializer = EndSessionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        session = get_object_or_404(Session, id=serializer.validated_data['session_id'])
        session = SessionStateService.end_session(session)
        
        session_serializer = SessionSerializer(session)
        return Response(session_serializer.data, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': 'Internal server error'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )