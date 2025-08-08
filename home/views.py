import json
import os
from django.shortcuts import render
from dotenv import load_dotenv
from django.views import View
from .forms import CalculatorForm
from decimal import Decimal, ROUND_HALF_UP
from .models import TableIpAddressSort, Table
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from google.oauth2 import service_account




load_dotenv()
def round_half_up(value, ndigits):
    return float(Decimal(str(value)).quantize(Decimal('1.' + '0'*ndigits), rounding=ROUND_HALF_UP))


class Calculator():
    def __init__(self, target, dist):
        self.target = target
        self.dist = dist

    def resurt_one_try(self):
        if not self.target or not self.dist:
            return 0
        
        try:
            value = ((-1 * float(self.target)) / (float(self.dist) / 100)) + 8
            if 1 <= round_half_up(value, 2) <= 6 and round_half_up(value, 2) != 0:
                return round_half_up(value, 2)
            else:
                return 'Вы не попали в допустимый диапазон'
        except:
            return 0

    def resurt_two_try(self):
        try:
            return round_half_up(self.resurt_one_try() * 0.75, 2)
        except:
            return 'Вы не попали в допустимый диапазон'
    

    def resurt_three_try(self):
        try:
            return round_half_up(self.resurt_one_try() * 0.5, 2)
        except:
            return 'Вы не попали в допустимый диапазон'

    def result_MRAD(self):
        try:
            return round_half_up(float(self.target) / (float(self.dist) * 0.1), 2)
        except:
            return 0

class CalculatorView(View):
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 

    def get(self, request):
        form = CalculatorForm()
        current_ip = self.get_client_ip(request)
        recent_tables = TableIpAddressSort.objects.filter(ip=current_ip).select_related('table').order_by('-id')

        analytic = GoogleAnalyticsView()
        return render(request, 'home/home.html', {'form': form,
                                                  'recent_tables': recent_tables,
                                                  'visits': analytic.sessions
                                                  })

    def post(self, request):
        if 'clear' in request.POST:
            form = CalculatorForm()
            current_ip = self.get_client_ip(request)
            TableIpAddressSort.objects.filter(ip=current_ip).delete()
            recent_tables = []
            
            analytic = GoogleAnalyticsView()
            return render(request, 'home/home.html', 
                      {'form': form,
                        'recent_tables': recent_tables,
                        'visits': analytic.sessions
                      })
        

        form = CalculatorForm(request.POST)
        if form.is_valid():
            target = form.cleaned_data['target']
            dist = form.cleaned_data['dist']
            calculator = Calculator(target, dist)

            current_ip = self.get_client_ip(request)

            table = Table.objects.create(target=target, dist=dist, first_try=calculator.resurt_one_try(), second_try=calculator.resurt_two_try(), third_try=calculator.resurt_three_try(), mrad=calculator.result_MRAD())
            TableIpAddressSort.objects.create(ip=current_ip, table=table)
            recent_tables = TableIpAddressSort.objects.filter(ip=current_ip).select_related('table').order_by('-id')
        else:
            recent_tables = []
        
        analytic = GoogleAnalyticsView()
        return render(request, 'home/home.html', 
                      {'form': form,
                        'recent_tables': recent_tables,
                        'visits': analytic.sessions
                      })

class GoogleAnalyticsView():
    def response(self, type):
        users = 0
        property_id = '499888015'
        
        # Получаем данные из переменных окружения или файла (для локальной разработки)
        if os.getenv('GOOGLE_SERVICE_ACCOUNT_TYPE'):
            # Используем переменные окружения
            service_account_info = {
                "type": os.getenv('GOOGLE_SERVICE_ACCOUNT_TYPE'),
                "project_id": os.getenv('GOOGLE_PROJECT_ID'),
                "private_key_id": os.getenv('GOOGLE_PRIVATE_KEY_ID'),
                "private_key": os.getenv('GOOGLE_PRIVATE_KEY').replace('\\n', '\n'),
                "client_email": os.getenv('GOOGLE_CLIENT_EMAIL'),
                "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                "auth_uri": os.getenv('GOOGLE_AUTH_URI'),
                "token_uri": os.getenv('GOOGLE_TOKEN_URI'),
                "auth_provider_x509_cert_url": os.getenv('GOOGLE_AUTH_PROVIDER_X509_CERT_URL'),
                "client_x509_cert_url": os.getenv('GOOGLE_CLIENT_X509_CERT_URL'),
                "universe_domain": os.getenv('GOOGLE_UNIVERSE_DOMAIN')
            }
            credentials = service_account.Credentials.from_service_account_info(service_account_info)
        else:
            # Fallback для локальной разработки
            JSON_PATH = 'data/service.json'
            credentials = service_account.Credentials.from_service_account_file(JSON_PATH)
        client = BetaAnalyticsDataClient(credentials=credentials)
        
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="city")],
            metrics=[Metric(name=f"{type}")],
            date_ranges=[DateRange(start_date="2020-03-31", end_date="today")],
        )
        response = client.run_report(request)
        
        for row in response.rows:
            print(row)
            users += int(row.metric_values[0].value)
            
        return users
    
    
    def activeUsers(self):
        return self.response(type='activeUsers')

    def screenPageViews(self):
        return self.response(type='screenPageViews')
    
    def sessions(self):
        return self.response(type='sessions')