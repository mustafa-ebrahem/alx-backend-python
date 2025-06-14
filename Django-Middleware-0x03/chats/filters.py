import django_filters
from django_filters import rest_framework as filters
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Message, Conversation

User = get_user_model()

class MessageFilter(filters.FilterSet):
    """
    Filter class for Message model to filter messages by various criteria
    """
    # Filter by conversation
    conversation = filters.UUIDFilter(field_name='conversation__conversation_id')
    
    # Filter by sender
    sender = filters.UUIDFilter(field_name='sender__user_id')
    sender_username = filters.CharFilter(field_name='sender__username', lookup_expr='icontains')
    
    # Filter by date range
    sent_after = filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    sent_before = filters.DateTimeFilter(field_name='sent_at', lookup_expr='lte')
    sent_at = filters.DateTimeFilter(field_name='sent_at')
    
    # Filter by date (without time)
    sent_date = filters.DateFilter(field_name='sent_at__date')
    sent_date_after = filters.DateFilter(field_name='sent_at__date', lookup_expr='gte')
    sent_date_before = filters.DateFilter(field_name='sent_at__date', lookup_expr='lte')
    
    # Filter by content
    content = filters.CharFilter(field_name='content', lookup_expr='icontains')
    content_exact = filters.CharFilter(field_name='content', lookup_expr='exact')
    
    # Filter by time range (last hour, day, week, month)
    time_range = filters.ChoiceFilter(
        choices=[
            ('hour', 'Last Hour'),
            ('day', 'Last Day'),
            ('week', 'Last Week'),
            ('month', 'Last Month'),
        ],
        method='filter_by_time_range'
    )

    class Meta:
        model = Message
        fields = [
            'conversation',
            'sender',
            'sender_username',
            'sent_after',
            'sent_before',
            'sent_at',
            'sent_date',
            'sent_date_after',
            'sent_date_before',
            'content',
            'content_exact',
            'time_range',
        ]

    def filter_by_time_range(self, queryset, name, value):
        """
        Filter messages by predefined time ranges
        """
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        
        if value == 'hour':
            time_threshold = now - timedelta(hours=1)
        elif value == 'day':
            time_threshold = now - timedelta(days=1)
        elif value == 'week':
            time_threshold = now - timedelta(weeks=1)
        elif value == 'month':
            time_threshold = now - timedelta(days=30)
        else:
            return queryset
        
        return queryset.filter(sent_at__gte=time_threshold)

class ConversationFilter(filters.FilterSet):
    """
    Filter class for Conversation model to filter conversations by participants
    """
    # Filter by participant
    participant = filters.UUIDFilter(field_name='participants__user_id')
    participant_username = filters.CharFilter(field_name='participants__username', lookup_expr='icontains')
    participant_email = filters.CharFilter(field_name='participants__email', lookup_expr='icontains')
    
    # Filter by multiple participants (comma-separated UUIDs)
    participants = filters.CharFilter(method='filter_by_participants')
    
    # Filter by creation date
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    created_date = filters.DateFilter(field_name='created_at__date')
    
    # Filter conversations with messages in a time range
    has_messages_after = filters.DateTimeFilter(method='filter_has_messages_after')
    has_messages_before = filters.DateTimeFilter(method='filter_has_messages_before')
    
    # Filter by participant count
    min_participants = filters.NumberFilter(method='filter_min_participants')
    max_participants = filters.NumberFilter(method='filter_max_participants')

    class Meta:
        model = Conversation
        fields = [
            'participant',
            'participant_username',
            'participant_email',
            'participants',
            'created_after',
            'created_before',
            'created_date',
            'has_messages_after',
            'has_messages_before',
            'min_participants',
            'max_participants',
        ]

    def filter_by_participants(self, queryset, name, value):
        """
        Filter conversations that include all specified participants (AND logic)
        Expected format: "uuid1,uuid2,uuid3"
        """
        if not value:
            return queryset
        
        participant_ids = [pid.strip() for pid in value.split(',') if pid.strip()]
        
        for participant_id in participant_ids:
            try:
                queryset = queryset.filter(participants__user_id=participant_id)
            except ValueError:
                # Invalid UUID format
                continue
        
        return queryset.distinct()

    def filter_has_messages_after(self, queryset, name, value):
        """
        Filter conversations that have messages sent after the specified date
        """
        return queryset.filter(messages__sent_at__gte=value).distinct()

    def filter_has_messages_before(self, queryset, name, value):
        """
        Filter conversations that have messages sent before the specified date
        """
        return queryset.filter(messages__sent_at__lte=value).distinct()

    def filter_min_participants(self, queryset, name, value):
        """
        Filter conversations with at least the specified number of participants
        """
        from django.db.models import Count
        return queryset.annotate(
            participant_count=Count('participants')
        ).filter(participant_count__gte=value)

    def filter_max_participants(self, queryset, name, value):
        """
        Filter conversations with at most the specified number of participants
        """
        from django.db.models import Count
        return queryset.annotate(
            participant_count=Count('participants')
        ).filter(participant_count__lte=value)