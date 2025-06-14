from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User, Conversation, Message

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = [
            'user_id', 'username', 'email', 'password', 
            'first_name', 'last_name', 'phone_number', 
            'role', 'is_online', 'created_at'
        ]
        read_only_fields = ['user_id', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        """
        Create a new user with encrypted password
        """
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        """
        Update user instance, handling password separately
        """
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance

class UserBasicSerializer(serializers.ModelSerializer):
    """
    Basic user serializer for nested relationships (excludes sensitive data)
    """
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'first_name', 'last_name', 'is_online']
        read_only_fields = fields

class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model
    """
    sender = UserBasicSerializer(read_only=True)
    sender_id = serializers.UUIDField(write_only=True, source='sender.user_id')
    
    class Meta:
        model = Message
        fields = [
            'message_id', 'conversation', 'sender', 'sender_id',
            'message_body', 'sent_at'
        ]
        read_only_fields = ['message_id', 'sent_at']

    def create(self, validated_data):
        """
        Create a new message
        """
        sender_data = validated_data.pop('sender', {})
        sender_id = sender_data.get('user_id')
        
        if sender_id:
            try:
                sender = User.objects.get(user_id=sender_id)
                validated_data['sender'] = sender
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid sender ID")
        
        return Message.objects.create(**validated_data)

class MessageCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for creating messages
    """
    class Meta:
        model = Message
        fields = ['conversation', 'message_body']

class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation model with nested messages
    """
    participants = UserBasicSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'participant_ids',
            'messages', 'message_count', 'last_message', 'created_at'
        ]
        read_only_fields = ['conversation_id', 'created_at']

    def get_message_count(self, obj):
        """
        Get total number of messages in the conversation
        """
        return obj.messages.count()

    def get_last_message(self, obj):
        """
        Get the most recent message in the conversation
        """
        last_message = obj.messages.last()
        if last_message:
            return MessageSerializer(last_message).data
        return None

    def create(self, validated_data):
        """
        Create a new conversation with participants
        """
        participant_ids = validated_data.pop('participant_ids', [])
        conversation = Conversation.objects.create(**validated_data)
        
        if participant_ids:
            participants = User.objects.filter(user_id__in=participant_ids)
            conversation.participants.set(participants)
        
        return conversation

    def update(self, instance, validated_data):
        """
        Update conversation and its participants
        """
        participant_ids = validated_data.pop('participant_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if participant_ids is not None:
            participants = User.objects.filter(user_id__in=participant_ids)
            instance.participants.set(participants)
        
        instance.save()
        return instance

class ConversationListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing conversations (without all messages)
    """
    participants = UserBasicSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'message_count',
            'last_message', 'unread_count', 'created_at'
        ]
        read_only_fields = fields

    def get_message_count(self, obj):
        """
        Get total number of messages in the conversation
        """
        return obj.messages.count()

    def get_last_message(self, obj):
        """
        Get the most recent message in the conversation
        """
        last_message = obj.messages.last()
        if last_message:
            return {
                'message_id': last_message.message_id,
                'message_body': last_message.message_body,
                'sender': last_message.sender.username,
                'sent_at': last_message.sent_at
            }
        return None

    def get_unread_count(self, obj):
        """
        Get number of unread messages for the current user
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # This is a placeholder - you might want to implement read status tracking
            return 0
        return 0

class ConversationDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for a single conversation with all messages
    """
    participants = UserBasicSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'messages', 'created_at'
        ]
        read_only_fields = fields