# api/serializers.py
from rest_framework import serializers
from .models import Post  # use your model name

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"
