from django.urls import path
from apps.sessions import views

app_name = 'sessions'

urlpatterns = [
    path('book/', views.book_session, name='book_session'),
    path('join/', views.join_session, name='join_session'),
    path('end/', views.end_session, name='end_session'),
]