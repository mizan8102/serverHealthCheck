# serializers.py

from rest_framework import serializers
from .models import ServerInfo, ServerCheckResult

class ServerCheckResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServerCheckResult
        fields = '__all__'

class ServerInfoSerializer(serializers.ModelSerializer):
    servercheckresult_set = ServerCheckResultSerializer(many=True, read_only=True)

    class Meta:
        model = ServerInfo
        fields = ('id', 'server_name', 'ip_address', 'url_address', 'created_at', 'updated_at', 'servercheckresult_set')

    def to_representation(self, instance):
        # Get the last 10 ServerCheckResult instances related to the ServerInfo instance
        last_10_results = instance.servercheckresult_set.all().order_by('-id')[:10]
        # Serialize the last 10 ServerCheckResult instances
        last_10_results_data = ServerCheckResultSerializer(last_10_results, many=True).data
        # Get the default serialized representation of the ServerInfo instance
        data = super().to_representation(instance)
        # Include the serialized last 10 ServerCheckResult instances in the data
        data['servercheckresult_set'] = last_10_results_data
        return data
    
class CureentServerSerializer(serializers.ModelSerializer):
    server_id = ServerInfoSerializer(many=True, read_only=True)  # Use many=True for related objects
    
    class Meta:
        model = ServerCheckResult
        fields = ['response_time', 'server_id']