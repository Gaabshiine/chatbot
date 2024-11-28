# gaabshiine_chat/urls.py
from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chat/', include('chat.urls')),  # This includes the chat app URLs
    path('', lambda request: redirect('chat/', permanent=False)),  # Redirect root URL to /chat/
]
