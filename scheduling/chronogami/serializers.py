from rest_framework import serializers
from scheduling.models import AvailabilitySlots, SchedulingPreference, APIClient
from swaps.models import Session

class AvailabilitySlotsSerializer(serializers.ModelSerializer):
    """
    Serializes a user's weekly availability slot.
    """

    day_name = serializers.SerializerMethodField()

    class Meta:
        model = AvailabilitySlots
        fields = ["id", "day_of_week", "day_name", "start_time", "end_time", "is_active"]
        read_only_fields = ["id", "day_name"]

    def get_day_name(self, obj):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[obj.day_of_week]
    
class TimeSuggestionSerializer(serializers.Serializer):
    """
    Request body for getting amsrt time suggestions.
    External apps send two user IDs and a duration.
    """

    user_a_id = serializers.IntegerField(help_text = "ID of the first user")
    user_b_id = serializers.IntegerField(help_text = "ID of the second user")
    duration_minutes = serializers.IntegerField(
        default = 60,
        min_value = 15,
        max_value = 480,
        help_text = "Session duration in minutes (15-480)"
    )
    num_suggestions = serializers.IntegerField(
        default = 5,
        min_value = 1,
        max_value = 20,
        help_text = "Number of suggestions to return (1-20)"
    )
    after_datetime = serializers.DateTime(
        required = False,
        help_text = "Only suggest times after this date and time (ISO 8601, UTC)"
    )

class ConflictCheckSerializer(serializers.Serializer):
    """
    Request body for checking if a time slot has conflicts
    """

    user_id = serializers.IntegerField(help_text="User ID to check conflicts for")
    proposed_datetime = serializers.DateTimeField(help_text="Proposed session start (ISO 8601, UTC)")
    duration_minutes = serializers.IntegerField(
        default = 60,
        min_value = 15,
        max_value = 480
    )
    timezone = serializers.CharField(
        default='UTC',
        help_text = 'IANA timezone string e.g. Africa/Nairobi'
    )

class SessionSerializer(serializers.ModelSerializer):
    """
    Serializes a session for API responses
    """
    swap_id = serializers.IntegerField(source='swap_request.id', read_only=True)
    sender = serializers.CharField(source='swap_request.sender.username', read_only=True)
    receiver = serializers.CharField(source='swap_request.receiver.username', read_only=True)
    skill_name = serializers.CharField(source='swap_request.offered_skill.skill.name', read_only=True)
    
    class Meta:
        model = Session
        fields = [
            'id', 'swap_id', 'sender', 'receiver', 'skill_name',
            'scheduled_date', 'duration_minutes', 'timezone',
            'is_virtual', 'meeting_link',
            'location_name', 'location_lat', 'location_lng',
            'status', 'notes', 'google_event_id',
        ]
        read_only_fields= ['id', 'swap_id', 'sender', 'receiver', 'skill_name', 'google_event_id']
                           

class AvailabilitySlotCreateSerializer(serializers.ModelSerializer):
    """
    Creating new availability slots via API.
    """

    class Meta:
        model = AvailabilitySlots
        fields = ["day_of_week", "start_time", "end_time"]

    def validate(self, data):
        if data["start_time"] >= data["end_time"]:
            raise serializers.ValidationError(
                "end time must be after start time."
            )
        return data
    
class APIClientSerializer(serializers.ModelSerializer):
    """
    Registering new API clients.
    """

    class Meta:
        model = APIClient
        fields = ["id", "name", "description", "api_key", "is_active", "created_at", "request_count", "last_used"]
        read_only_fields = ["id", "api_key", "created_at", "request_count", "last_used"]
