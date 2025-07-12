from django.shortcuts import render
from django.views import View
from .forms import CalculatorForm
from decimal import Decimal, ROUND_HALF_UP
from .models import TableIpAddressSort, Table



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
        recent_tables = TableIpAddressSort.objects.filter(ip=current_ip).order_by('-id')

        return render(request, 'home/home.html', {'form': form,
                                                  'recent_tables': recent_tables})

    def post(self, request):
        if 'clear' in request.POST:
            form = CalculatorForm()
            current_ip = self.get_client_ip(request)
            TableIpAddressSort.objects.filter(ip=current_ip).delete()
            recent_tables = []
            return render(request, 'home/home.html', {'form': form,
                                                  'recent_tables': recent_tables})
        

        form = CalculatorForm(request.POST)
        if form.is_valid():
            target = form.cleaned_data['target']
            dist = form.cleaned_data['dist']
            calculator = Calculator(target, dist)


            current_ip = self.get_client_ip(request)

            if Table.objects.filter(target=target, dist=dist).count() <= 10:
                table = Table()
                table.target = target
                table.dist = dist
                table.first_try = calculator.resurt_one_try()
                table.second_try = calculator.resurt_two_try()
                table.third_try = calculator.resurt_three_try()
                table.mrad = calculator.result_MRAD()
                table.save()
            else:
                Table.objects.filter(target=target, dist=dist).delete()

                table = Table()
                table.target = target
                table.dist = dist
                table.first_try = calculator.resurt_one_try()
                table.second_try = calculator.resurt_two_try()
                table.third_try = calculator.resurt_three_try()
                table.mrad = calculator.result_MRAD()
                table.save()

            if TableIpAddressSort.objects.filter(ip=current_ip).count() <= 10:
                sort_table_for_ip = TableIpAddressSort()
                sort_table_for_ip.ip = current_ip
                sort_table_for_ip.table = table
                sort_table_for_ip.save()
            else:
                sort_table_for_ip = TableIpAddressSort.objects.filter(ip=current_ip).delete()
                sort_table_for_ip = TableIpAddressSort()
                sort_table_for_ip.ip = current_ip
                sort_table_for_ip.table = table
                sort_table_for_ip.save()
            
            recent_tables = TableIpAddressSort.objects.filter(ip=current_ip).order_by('-id')
        else:
            recent_tables = []

        return render(
            request, 'home/home.html', 
            {
                'form': form,
                'recent_tables': recent_tables
            })   

        