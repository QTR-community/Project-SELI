from rest_framework import serializers
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["user_id", "street", "city", "state", "latitude", "longitude"]
        read_only_fields = ["latitude", "longitude"]
