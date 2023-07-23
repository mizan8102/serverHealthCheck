from django.shortcuts import render
import paramiko
from django.shortcuts import render
from django.http import HttpResponse
import psutil
import requests
import time
from .models import ServerInfo,ServerCheckResult
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import ServerInfoSerializer,ServerCheckResultSerializer
from rest_framework import status
from django.http import JsonResponse
from django.http import JsonResponse
from celery import shared_task
from datetime import timedelta
from django.utils import timezone
# Create your views here.


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

#server up down and response time 


#server up down checking 
@api_view(['GET'])
def server_up_down_check(request):
    server_info_instances = ServerCheckResult.objects.all().order_by('-id')[:10]
    serializer = ServerCheckResultSerializer(server_info_instances, many=True)  # Use many=True for a queryset
    return Response(serializer.data)
   
def index(request):
    return ssh_health_check(request)
 