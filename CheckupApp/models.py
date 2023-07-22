from django.db import models

# Create your models here.
class ServerInfo(models.Model):
    server_name = models.CharField(max_length=200)
    ip_address = models.CharField(max_length=20,null=True)
    url_address = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ServerCheckResult(models.Model):
    server_id = models.ForeignKey(ServerInfo, on_delete=models.CASCADE)
    response_time = models.CharField(max_length=200)
    server_stauts = models.IntegerField(default=1)
    status_code = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
