from django.contrib import admin
from .models import ServerInfo,ServerCheckResult
# Register your models here.
class ServerInfoAdmin(admin.ModelAdmin):
    pass
    # list_display use for show which column i can show
    list_display = ('server_name', 'ip_address','url_address', 'created_at', 'updated_at')
    
class ServerCheckResultAdmin(admin.ModelAdmin):
    list_display = ('server_id', 'response_time', 'status_code', 'created_at', 'updated_at' )  # Add other fields you want to display

admin.site.register(ServerInfo, ServerInfoAdmin)
admin.site.register(ServerCheckResult, ServerCheckResultAdmin)
