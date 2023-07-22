from rest_framework import serializers
from .models import ServerInfo

class ServerInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServerInfo
        fields = '__all__'
