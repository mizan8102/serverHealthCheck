import logging
from CheckupApp.models import ServerCheckResult,ServerInfo
from celery import shared_task
from datetime import timedelta
from django.utils import timezone
import requests
from getmac import get_mac_address as gma


logger = logging.getLogger(__name__)
logger2 = logging.getLogger('django')

def my_function():
    
    #get 
    server_all = ServerInfo.objects.all()
    for server_info in server_all:
        server_up=False
        response_time_ms=0
        
        # check server up down
        try:
            response = requests.get(server_info.url_address)
            server_up = response.status_code >= 200 and response.status_code < 300
            if response.status_code == 404:
                server_up = False
            response_time_ms = response.elapsed.total_seconds() * 1000
        except requests.exceptions.RequestException as e:
            print("Error checking server health:", e)
            logger2.error(f"error")
            
        # create server result
        try:
            server_status= 1 if server_up else 0
            server_up = 200 if server_up else 404
            result = ServerCheckResult.objects.create(
                server_id=server_info,
                response_time=response_time_ms,
                # server_status=server_status,
                status_code=server_up,
            )
            if result.status_code==404:
                # api_url = f'https://api.sms.net.bd/sendsms?api_key=s62eks4AGUNiSXePhXd6h6yFJFox9p3DbFwpsw9k&msg={server_info.url_address} server is down&to=01645316379'
                try:
                    response = requests.get(api_url)
                except requests.exceptions.RequestException as e:
                    logger2.error(f"error {e}")
            logger2.info(f"hello world {response_time_ms}")
        except Exception as e:
            logger2.error(f"error {e}")



@shared_task
def delete_old_data():
    # Calculate the date threshold for keeping the last 10 data entries
    # threshold_date = timezone.now() - timedelta(days=10)

    # # Delete data older than the threshold date
    # ServerCheckResult.objects.filter(timestamp__lt=threshold_date).delete()
    original_string = gma()
    # modified_string = original_string.replace(":", "-")
    logger2.info("MAC ADDRESS = "+gma())