import calendar
import datetime
from calendar import HTMLCalendar

from dateutil.relativedelta import relativedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.checks import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views import View
from django.contrib import messages
from django.views.generic import DeleteView

from WorkShedule.forms import LoginUserForm, AddUserForm, WorkDayForm
from WorkShedule.utils import *
from .models import *


def temp(request):
    return ('siema')


class Homepage(View):
    def get(self, request):
        return render(request, 'WorkShedule/base.html')


class TestView(View):
    def get(self, request, day=datetime.now()):
        cal = Calendar(day.year, day.month)

        html_cal = cal.formatmonth(withyear=True)
        return render(request, 'WorkShedule/home.html', context={'html_cal': html_cal})


def is_three_worker(month_number):
    date = datetime.today()
    current_day = date.replace(day=1, month=month_number)
    days_not_enough_worker = []
    while current_day.month == month_number:
        if WorkDay.objects.filter(date_day=current_day).count() < 3:
            days_not_enough_worker.append(current_day)
        current_day = current_day + timedelta(days=1)
    return days_not_enough_worker


class CalendarView(View):

    def get(self, request, month_number=None):
        month_number = month_number if month_number is not None else datetime.now().month
        day = datetime.now()
        mycall = Calendar(day.year, int(month_number))
        prev_month = (int(month_number) - 1)
        if prev_month == 0:
            prev_month = 12
        next_month = (int(month_number) + 1)
        if next_month == 13:
            next_month = 1
        call = mycall.formatmonth(withyear=True)
        form = WorkDayForm()
        not_enough_worker_list = is_three_worker(int(month_number))

        if request.user.is_authenticated:

            worker = User.objects.get(id=request.user.id)
            work_day = WorkDay.objects.filter(employee=worker, date_day__month=month_number)
        else:
            worker = None
            work_day = WorkDay.objects.all()
        all_staff = WorkDay.objects.all()
        context = {'call': call,
                   'form': form,
                   'submit': "Zapisz",
                   'all_staff': all_staff,
                   'worker': worker,
                   'work_day': work_day,
                   'prev_month': prev_month,
                   'next_month': next_month,
                   'month_number': month_number,
                   'not_enough_worker_list': not_enough_worker_list,
                   }

        return render(request, 'WorkShedule/calendar_view.html', context)

    def post(self, request, month_number=None):
        month_number = month_number if month_number is not None else datetime.now().month
        form = WorkDayForm(request.POST)
        valid = form.is_valid()
        date_day = form.cleaned_data.get('date_day')
        if valid:
            time_start = form.cleaned_data.get('time_start')
            time_end = form.cleaned_data.get('time_end')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            employee_id = self.request.user.id
        else:
            messages.error(request, 'Podano błędne dane')
            return redirect(reverse_lazy('calendar', kwargs={'month_number': month_number}))
        new_days_update_days = self.add_range_days(request, start_date, end_date, time_start, time_end, employee_id)

        return redirect('calendar', month_number=month_number)

    def add_range_days(self, request, start_date, end_date, time_start, time_end, employee_id):
        working_day = start_date
        if end_date != None:
            while (working_day <= end_date):
                WorkDay.objects.update_or_create(
                    date_day=working_day, employee_id=employee_id, defaults={'time_start': time_start,
                                                                             'time_end': time_end})
                working_day = working_day + timedelta(days=1)
            messages.info(request, 'Zmiany wprowadzone')
        else:
            WorkDay.objects.update_or_create(date_day=working_day, employee_id=employee_id,
                                             defaults={'time_start': time_start,
                                                       'time_end': time_end,
                                                       })
            messages.info(request, 'Zmiany Wprowadzone')


class DeleteDateDay(View):
    def get(self, request, month_number):
        list_day_to_delete = []
        for key, value in request.GET.items():
            if value == "on":
                day_to_delete = WorkDay.objects.get(pk=key)
                list_day_to_delete.append(day_to_delete)
        return render(request, 'WorkShedule/workday_confirm_delete.html',
                      context={'list_day_to_delete': list_day_to_delete,
                               'month_number': month_number})

    def post(self, request, month_number):
        print('request', request.GET)
        for key, value in request.GET.items():
            if value == "on":
                day_to_delete = WorkDay.objects.filter(pk=key)
                day_to_delete.delete()
        return redirect('calendar', month_number=month_number)

class LoginUser(View):
    def get(self, request):
        form = LoginUserForm()
        context = {'form': form, 'submit': "Loguj"}
        return render(request, 'WorkShedule/form.html', context)

    def post(self, request):
        form = LoginUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('login')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse_lazy('calendar', kwargs={'month_number': datetime.now().month}))
            else:
                message = '<h3>Błędny użytkownik lub hasło</h3>'
                context = {'form': form, 'submit': "Loguj", 'message': message}
                return render(request, 'WorkShedule/form.html', context)
        else:
            context = {'form': form, 'submit': "Loguj"}
            return render(request, 'WorkShedule/form.html', context)


class Logout(View):
    def get(self, request):
        logout(request)
        return redirect('start')


class AddUser(View):
    def get(self, request):
        form = AddUserForm()
        context = {'form': form, "submit": "Dodaj"}
        return render(request, 'WorkShedule/form.html', context)

    def post(self, request):
        form = AddUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            email = form.cleaned_data.get('email')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            User.objects.create_user(username=username, email=email, password=password, last_name=last_name,
                                     first_name=first_name)
            messages.success(request, message="Dodano nowego użytownika")
            return redirect('start')
        else:
            context = {'form': form, "submit": "Dodaj"}
            return render(request, 'WorkShedule/form.html', context)


# def calendar(request, pYear, pMonth):
#     """
#     Show calendar of events for specified month and year
#     """
#     lYear = int(pYear)
#     lMonth = int(pMonth)
#     lCalendarFromMonth = datetime(lYear, lMonth, 1)
#     lCalendarToMonth = datetime(lYear, lMonth, calendar.monthrange(lYear, lMonth)[1])
#
#     lCalendar = MyCalendar.formatmonth(2019, 6)
#     lPreviousYear = lYear
#     lPreviousMonth = lMonth - 1
#     if lPreviousMonth == 0:
#         lPreviousMonth = 12
#         lPreviousYear = lYear - 1
#     lNextYear = lYear
#     lNextMonth = lMonth + 1
#     if lNextMonth == 13:
#         lNextMonth = 1
#         lNextYear = lYear + 1
#     lYearAfterThis = lYear + 1
#     lYearBeforeThis = lYear - 1
#     return render_auth(request, 'calendar/home.html', {'Calendar': mark_safe(lCalendar),
#                                                        'Month': lMonth,
#                                                        'MonthName': named_month(lMonth),
#                                                        'Year': lYear,
#                                                        'PreviousMonth': lPreviousMonth,
#                                                        'PreviousMonthName': named_month(lPreviousMonth),
#                                                        'PreviousYear': lPreviousYear,
#                                                        'NextMonth': lNextMonth,
#                                                        'NextMonthName': named_month(lNextMonth),
#                                                        'NextYear': lNextYear,
#                                                        'YearBeforeThis': lYearBeforeThis,
#                                                        'YearAfterThis': lYearAfterThis,
#                                                        })


from calendar import monthrange


def named_month(pMonthNumber):
    """
    Return the name of the month, given the month number
    """
    return date(1900, pMonthNumber, 1).strftime('%B')


def home(request):
    """
    Show calendar of events this month
    """
    lToday = datetime.now()
    return calendar(request, lToday.year, lToday.month)


def calendar(request, pYear=2019, pMonth=6):
    """
    Show calendar of events for specified month and year
    """

    lPreviousMonth = lMonth - 1
    if lPreviousMonth == 0:
        lPreviousMonth = 12
        lPreviousYear = lYear - 1
    lNextYear = lYear
    lNextMonth = lMonth + 1
    if lNextMonth == 13:
        lNextMonth = 1
        lNextYear = lYear + 1
    lYearAfterThis = lYear + 1
    lYearBeforeThis = lYear - 1

    return render(request, 'WorkShedule/home.html', {'Calendar': mark_safe(lCalendar),
                                                     'Month': lMonth,
                                                     'MonthName': named_month(lMonth),
                                                     'Year': lYear,
                                                     'PreviousMonth': lPreviousMonth,
                                                     'PreviousMonthName': named_month(lPreviousMonth),
                                                     'PreviousYear': lPreviousYear,
                                                     'NextMonth': lNextMonth,
                                                     'NextMonthName': named_month(lNextMonth),
                                                     'NextYear': lNextYear,
                                                     'YearBeforeThis': lYearBeforeThis,
                                                     'YearAfterThis': lYearAfterThis,
                                                     })
