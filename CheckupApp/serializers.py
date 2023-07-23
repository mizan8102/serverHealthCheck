from rest_framework import serializers
from .models import ServerInfo, ServerCheckResult



class ServerInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServerInfo
        fields = ('id', 'server_name', 'ip_address', 'url_address', 'created_at', 'updated_at')

class ServerCheckResultSerializer(serializers.ModelSerializer):
    server_id = ServerInfoSerializer(many=False, read_only=True)

    class Meta:
        model = ServerCheckResult
        fields = ('id', 'server_id', 'response_time', 'server_stauts', 'status_code', 'created_at', 'updated_at')
