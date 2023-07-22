from django.contrib import admin
from .models import ServerInfo
# Register your models here.
class ServerInfoAdmin(admin.ModelAdmin):
    pass
    # list_display use for show which column i can show
    list_display = ('server_name', 'ip_address','url_address', 'created_at', 'updated_at')
    
admin.site.register(ServerInfo, ServerInfoAdmin)