from rest_framework import permissions
from rest_framework.permissions import BasePermission

class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user

class IsParticipantOfConversation(BasePermission):
    """
    Enhanced permission to only allow authenticated participants of a conversation to access it.
    """
    def has_permission(self, request, view):
        # First check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        return True
    
    def has_object_permission(self, request, view, obj):
        # Ensure user is authenticated and active
        if not request.user or not request.user.is_authenticated or not request.user.is_active:
            return False
        
        # Check if user is a participant in the conversation
        return request.user in obj.participants.all()

class IsMessageOwner(BasePermission):
    """
    Custom permission to only allow message owners to edit/delete their messages.
    Participants can view messages in their conversations.
    """
    def has_permission(self, request, view):
        # First check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        return True
    
    def has_object_permission(self, request, view, obj):
        # Ensure user is authenticated and active
        if not request.user or not request.user.is_authenticated or not request.user.is_active:
            return False
        
        # Allow read access to conversation participants
        if request.method in permissions.SAFE_METHODS:
            return request.user in obj.conversation.participants.all()
        
        # Write permissions (POST, PUT, PATCH, DELETE) only for message owner
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return obj.sender == request.user
        
        return False

class IsConversationParticipant(BasePermission):
    """
    Custom permission to check if user is participant in conversation for nested routes.
    """
    def has_permission(self, request, view):
        # First check if user is authenticated
        if not request.user or not request.user.is_authenticated or not request.user.is_active:
            return False
            
        # For nested routes, check if user is participant of parent conversation
        conversation_id = view.kwargs.get('conversation_pk')
        if conversation_id:
            from .models import Conversation
            try:
                conversation = Conversation.objects.get(conversation_id=conversation_id)
                return request.user in conversation.participants.all()
            except Conversation.DoesNotExist:
                return False
        return True

class IsAuthenticatedAndActive(BasePermission):
    """
    Custom permission to check if user is authenticated and active.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_active
        )

class IsMessageParticipant(BasePermission):
    """
    Custom permission for message operations - allows participants to send, view messages
    but only owners can update/delete.
    """
    def has_permission(self, request, view):
        # First check if user is authenticated
        if not request.user or not request.user.is_authenticated or not request.user.is_active:
            return False
        return True
    
    def has_object_permission(self, request, view, obj):
        # Ensure user is authenticated and active
        if not request.user or not request.user.is_authenticated or not request.user.is_active:
            return False
        
        # For viewing messages (GET, HEAD, OPTIONS), user must be participant in conversation
        if request.method in permissions.SAFE_METHODS:
            return request.user in obj.conversation.participants.all()
        
        # For creating messages (POST), user must be participant in conversation
        if request.method == 'POST':
            return request.user in obj.conversation.participants.all()
        
        # For updating/deleting messages (PUT, PATCH, DELETE), user must be the sender
        if request.method in ["PUT", "PATCH", "DELETE"]:
            return obj.sender == request.user
        
        return False