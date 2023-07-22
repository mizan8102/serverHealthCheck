from django.db import models

# Create your models here.
class ServerInfo(models.Model):
    server_name = models.CharField(max_length=200)
    ip_address = models.CharField(max_length=20)
    url_address = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ServerCheckResult(model.Model):
    server_id = models.ForeignKey(ServerInfo(), on_delete=models.CASCADE())
