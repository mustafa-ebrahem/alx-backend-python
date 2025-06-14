from django.contrib import admin
from django.urls import path, include
from rest_framework_nested.routers import NestedDefaultRouter
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet
from . import auth

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

# Create nested router for messages within conversations
conversations_router = NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversations_router.register(r'messages', MessageViewSet, basename='conversation-messages')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', include(conversations_router.urls)),

    # Authentication endpoints
    path('api/auth/register/', auth.register_user, name='register'),
    path('api/auth/login/', auth.login_user, name='login'),
    path('api/auth/logout/', auth.logout_user, name='logout'),
    path('api/auth/refresh/', auth.refresh_token, name='refresh_token'),
    path('api/auth/profile/', auth.user_profile, name='user_profile'),
    path('api/auth/profile/update/', auth.update_profile, name='update_profile'),
    path('api/auth/change-password/', auth.change_password, name='change_password'),
    path('api/auth/online-status/', auth.update_online_status, name='update_online_status'),
]
