from django.shortcuts import render
import paramiko
from django.shortcuts import render
from django.http import HttpResponse
import psutil
import requests
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ServerInfo,ServerCheckResult
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import ServerInfoSerializer,ServerCheckResultSerializer,CureentServerSerializer, CurrentServerSerializer
from rest_framework import status
from django.http import JsonResponse
from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from django.db.models import Max
from django.db.models import OuterRef, Subquery, Prefetch

# Create your views here.
class SSHHealthCheckAPI(APIView):
    def get(self, request):
        hostname = "188.166.242.10"
        username = "root"
        password = "zit.CKL@+[2023]SVR"

        try:
            # Establish an SSH connection
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname, username=username, password=password)

            # Commands to check server health
            commands = [
                "uptime",
                "df -h",
                "free -h",
                "ping -c 4 google.com",
                "netstat -tuln",
                "tail /var/log/syslog",
                "tail /var/log/auth.log",
                "top -bn1",
            ]

            health_check_results = {}

            for command in commands:
                stdin, stdout, stderr = ssh_client.exec_command(command)
                output = stdout.read().decode("utf-8")
                health_check_results[command] = output

            # Close the SSH connection
            ssh_client.close()

            # Return the health check results as JSON response
            return Response({"results": health_check_results}, status=status.HTTP_200_OK)

        except paramiko.AuthenticationException:
            return Response("Authentication failed. Please check your credentials.", status=status.HTTP_401_UNAUTHORIZED)
        except paramiko.SSHException as e:
            return Response(f"SSH error: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except paramiko.BadHostKeyException as e:
            return Response(f"Host key could not be verified: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response(f"Error: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def server_info_list(request):
    server_info = ServerInfo.objects.all()
    # serializer = ServerInfoSerializer(server_info, many=True)  # Use many=True for a queryset
    data = list(server_info.values())  # Convert the queryset to a list of dictionaries
    response_data = {
            'status': 'success',
            'data': data,
        }
    return JsonResponse(response_data)

@api_view(['POST'])
def create_server_info(request):
    serializer=ServerInfoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

def collect_server_usage(hostname, username, password):
    try:
        # Establish an SSH connection
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname, username=username, password=password)

        # Commands to get CPU and RAM usage
        cpu_usage_command = "top -bn1 | awk '/Cpu\(s\):/ {print $2}'"
        ram_usage_command = "free | awk '/Mem:/ {print $3/$2 * 100.0}'"

        stdin, stdout, stderr = ssh_client.exec_command(cpu_usage_command)
        cpu_usage = float(stdout.read().decode("utf-8").strip())

        stdin, stdout, stderr = ssh_client.exec_command(ram_usage_command)
        ram_usage = float(stdout.read().decode("utf-8").strip())

        # Save the data to the database
        ServerUsage.objects.create(cpu_usage=cpu_usage, ram_usage=ram_usage)

        # Close the SSH connection
        ssh_client.close()

        return JsonResponse({"success": True})

    except paramiko.AuthenticationException:
        return JsonResponse({"error": "Authentication failed. Please check your credentials."})
    except paramiko.SSHException as e:
        return JsonResponse({"error": f"SSH error: {e}"})
    except paramiko.BadHostKeyException as e:
        return JsonResponse({"error": f"Host key could not be verified: {e}"})
    except Exception as e:
        return JsonResponse({"error": f"Error: {e}"})
    
def ssh_health_check(request):
    hostname = "188.166.242.10"
    username = "root"
    password = "zit.CKL@+[2023]SVR"

    try:
        # Establish an SSH connection
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname, username=username, password=password)

        # Commands to check server health
        commands = [
            "uptime",
            "df -h",
            "free -h",
            "ping -c 4 google.com",
            "netstat -tuln",
            "tail /var/log/syslog",
            "tail /var/log/auth.log",
            "top -bn1",
        ]

        health_check_results = {}

        for command in commands:
            stdin, stdout, stderr = ssh_client.exec_command(command)
            output = stdout.read().decode("utf-8")
            health_check_results[command] = output

        # Close the SSH connection
        ssh_client.close()

        return render(request, "index.html", {"results": health_check_results})

    except paramiko.AuthenticationException:
        return HttpResponse("Authentication failed. Please check your credentials.")
    except paramiko.SSHException as e:
        return HttpResponse(f"SSH error: {e}")
    except paramiko.BadHostKeyException as e:
        return HttpResponse(f"Host key could not be verified: {e}")
    except Exception as e:
        return HttpResponse(f"Error: {e}")


def server_up_down_check_histories():
    server_check_results = ServerCheckResult.objects.select_related('server_id').order_by('-id')[:20]
    serialized_data = []
    for result in server_check_results:
        serialized_result = {
            'id': result.id,
            'response_time': result.response_time,
            'status_code': result.status_code,
            'created_at': result.created_at,
            'updated_at': result.updated_at,
            'server_name': result.server_id.server_name,
            'ip_address' : result.server_id.ip_address,
            'url_address' :result.server_id.url_address
        }

        # Append the serialized data to the list
        serialized_data.append(serialized_result)
    return serialized_data



@api_view(['GET'])
def server_up_down_check(request):
    try:
        latest_created_at = ServerCheckResult.objects.filter(
            server_id=OuterRef('server_id')
        ).values('server_id').annotate(max_created_at=Max('created_at')).values('max_created_at')
        latest_results = ServerCheckResult.objects.filter(
            created_at__in=Subquery(latest_created_at)
        )
        queryset = ServerCheckResult.objects.filter(
            id__in=Subquery(latest_results.values('id'))
        ).prefetch_related(
            Prefetch('server_id', queryset=ServerInfo.objects.all(), to_attr='server_info')
        )
        data_list = []
        for result in queryset:
            server_info_instance = result.server_id.server_info[0] if hasattr(result.server_id, 'server_info') else None
            data = {
                'server_id': result.server_id.id,
                'server_name': result.server_id.server_name if result.server_id else None,
                'ip_address': result.server_id.ip_address,
                'url_address': result.server_id.url_address,
                'response_time': result.response_time,
                'status_code': result.status_code,
                'created_at':result.created_at
            }
            data_list.append(data)

        return JsonResponse({'data': data_list,'data_his':server_up_down_check_histories()})
    except ServerCheckResult.DoesNotExist:
        return JsonResponse({'error': 'No ServerCheckResults found'}, status=404)
   
   
def index(request):
    return ssh_health_check(request)
 