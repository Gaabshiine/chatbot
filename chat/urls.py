# chat/urls.py
from django.urls import path
from .views import chat_view
from . import views

urlpatterns = [
    path("", views.chat_view, name="chat"),
    path('delete_all_chats/', views.delete_all_chats, name='delete_all_chats'),
    path('edit_chat/<int:chat_id>/', views.edit_chat, name='edit_chat'),
    
]
