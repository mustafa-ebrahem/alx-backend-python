from django.shortcuts import render
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    ConversationListSerializer,
    ConversationDetailSerializer,
    MessageSerializer,
    MessageCreateSerializer,
    UserBasicSerializer
)
from .permissions import (
    IsParticipantOfConversation,
    IsMessageOwner,
    IsConversationParticipant,
    IsAuthenticatedAndActive,
    IsMessageParticipant
)

User = get_user_model()

class MessagePagination(PageNumberPagination):
    """
    Custom pagination for messages
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations
    """
    permission_classes = [IsAuthenticatedAndActive, IsParticipantOfConversation]
    pagination_class = MessagePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['created_at']
    search_fields = ['participants__username', 'participants__email', 'participants__first_name', 'participants__last_name']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Filter conversations to only show those the user participates in
        """
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related('participants', 'messages')

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'list':
            return ConversationListSerializer
        elif self.action == 'retrieve':
            return ConversationDetailSerializer
        return ConversationSerializer

    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        if self.action == 'create':
            # For creating conversations, only need to be authenticated
            permission_classes = [IsAuthenticatedAndActive]
        else:
            # For other actions, need to be a participant
            permission_classes = [IsAuthenticatedAndActive, IsParticipantOfConversation]
        
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """
        Create a new conversation
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Add the current user as a participant
        participant_ids = request.data.get('participant_ids', [])
        if str(request.user.user_id) not in participant_ids:
            participant_ids.append(str(request.user.user_id))
        
        # Validate participants exist
        participants = User.objects.filter(user_id__in=participant_ids)
        if participants.count() != len(participant_ids):
            return Response(
                {'error': 'One or more participant IDs are invalid'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if conversation already exists between these participants
        if len(participant_ids) == 2:
            existing_conversation = Conversation.objects.filter(
                participants__user_id__in=participant_ids
            ).annotate(
                participant_count=Count('participants')
            ).filter(participant_count=2)
            
            if existing_conversation.exists():
                conversation = existing_conversation.first()
                serializer = ConversationDetailSerializer(conversation)
                return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Create new conversation
        conversation = serializer.save()
        conversation.participants.set(participants)
        
        response_serializer = ConversationDetailSerializer(conversation)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticatedAndActive, IsParticipantOfConversation])
    def send_message(self, request, pk=None):
        """
        Send a message to a specific conversation
        """
        conversation = self.get_object()
        
        # Check if user is a participant
        if not conversation.participants.filter(user_id=request.user.user_id).exists():
            return Response(
                {'error': 'You are not a participant in this conversation'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create message
        message_data = request.data.copy()
        message_data['conversation'] = conversation.conversation_id
        
        serializer = MessageCreateSerializer(data=message_data)
        serializer.is_valid(raise_exception=True)
        
        message = serializer.save(sender=request.user)
        
        # Return the created message with full details
        response_serializer = MessageSerializer(message)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticatedAndActive, IsParticipantOfConversation])
    def messages(self, request, pk=None):
        """
        Get all messages for a specific conversation with pagination
        """
        conversation = self.get_object()
        
        # Check if user is a participant
        if not conversation.participants.filter(user_id=request.user.user_id).exists():
            return Response(
                {'error': 'You are not a participant in this conversation'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        messages = conversation.messages.all().select_related('sender')
        
        # Apply pagination
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticatedAndActive, IsParticipantOfConversation])
    def add_participant(self, request, pk=None):
        """
        Add a participant to an existing conversation
        """
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_to_add = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user is already a participant
        if conversation.participants.filter(user_id=user_id).exists():
            return Response(
                {'error': 'User is already a participant'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        conversation.participants.add(user_to_add)
        
        serializer = ConversationDetailSerializer(conversation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticatedAndActive, IsParticipantOfConversation])
    def remove_participant(self, request, pk=None):
        """
        Remove a participant from a conversation
        """
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_to_remove = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Don't allow removing the last participant
        if conversation.participants.count() <= 1:
            return Response(
                {'error': 'Cannot remove the last participant'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        conversation.participants.remove(user_to_remove)
        
        serializer = ConversationDetailSerializer(conversation)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages with proper permission controls
    """
    permission_classes = [IsAuthenticatedAndActive, IsMessageParticipant]
    pagination_class = MessagePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['conversation', 'sender', 'sent_at']
    search_fields = ['content']
    ordering_fields = ['sent_at']
    ordering = ['-sent_at']

    def get_queryset(self):
        """
        Filter messages to only show those from conversations the user participates in
        """
        user_conversations = Conversation.objects.filter(participants=self.request.user)
        return Message.objects.filter(
            conversation__in=user_conversations
        ).select_related('sender', 'conversation')

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer

    def get_permissions(self):
        """
        Apply different permissions based on action
        """
        if self.action in ['list', 'retrieve']:
            # For viewing messages, check if user is conversation participant
            permission_classes = [IsAuthenticatedAndActive, IsMessageParticipant]
        elif self.action == 'create':
            # For creating messages, check if user is conversation participant
            permission_classes = [IsAuthenticatedAndActive, IsMessageParticipant]
        else:
            # For update/delete, check if user is message owner
            permission_classes = [IsAuthenticatedAndActive, IsMessageOwner]
        
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """
        Set the sender to the current user when creating a message
        """
        serializer.save(sender=self.request.user)
