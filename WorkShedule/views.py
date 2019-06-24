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


class Homepage(View):
    def get(self, request):
        return render(request, 'WorkShedule/base.html')



class TestView(View):
    def get(self,request, day=datetime.now()):
        cal = Calendar(day.year, day.month)

        html_cal = cal.formatmonth(withyear=True)
        return render(request, 'WorkShedule/home.html', context={'html_cal':html_cal})


# start_time, end_time
# this_date = start_date
# while (this_date<end_date):
#     Calendar.objects.create()
#     this_date = this_date + timedelta(days=1)


class CalendarView(LoginRequiredMixin,View):

    def get(self, request, day=datetime.now(),month_number=datetime.now().month):
        mycall = Calendar(day.year, int(month_number))
        prev_month = (int(month_number) - 1)
        if prev_month == 0:
            prev_month = 12
        next_month = (int(month_number) + 1)
        if next_month == 13:
            next_month = 1
        call = mycall.formatmonth(withyear=True)
        form = WorkDayForm()
        worker = User.objects.get(id=request.user.id)
        work_day = WorkDay.objects.filter(employee=worker)
        all_staff = WorkDay.objects.all()
        context = {'call': call,
                   'form': form,
                   'submit': "Zapisz",
                   'all_staff': all_staff,
                   'worker': worker,
                   'work_day': work_day,
                   'prev_month': prev_month,
                   'next_month': next_month,
                   }

        return render(request, 'WorkShedule/calendar_view.html', context)

    def post(self, request, month_number=datetime.now().month):
        form = WorkDayForm(request.POST)
        valid = form.is_valid()
        date_day = form.cleaned_data.get('date_day')
        if valid:
            time_start = form.cleaned_data.get('time_start')
            time_end = form.cleaned_data.get('time_end')
            # start_date = form.cleaned_data.get('start_date')
            # end_date = form.cleaned_data.get('end_date')

            employee_id = self.request.user.id
        else:
            messages.error(request, 'Podano błędne dane')
            return redirect(reverse_lazy('calendar',kwargs={'month_number': date_day.month}))


        if WorkDay.objects.filter(employee_id =employee_id, date_day=date_day):
            WorkDay.objects.filter(date_day=date_day, employee_id=employee_id).update(date_day=date_day,
                                                                                          time_start=time_start,
                                                                                          time_end=time_end)
            messages.success(request, 'Dzień poprawiony')
            return redirect('calendar',month_number=datetime.now().month)
        else:
            WorkDay.objects.create(date_day=date_day, time_start=time_start, time_end=time_end,
                                   employee_id=employee_id)
            messages.info(request, 'Dzień Dodany')
            return redirect('calendar', month_number=date_day.month)



# class CalendarView(View):
#
#     def get(self, request, day=datetime.now(),month_number=datetime.now().month):
#         mycall = MyCalendar()
#         call = mycall.formatmonth(day.year, int(month_number))
#         prev_month = (int(month_number) - 1)
#         if prev_month == 0:
#             prev_month = 12
#         next_month = (int(month_number) + 1)
#         if next_month == 13:
#             next_month = 1
#         form = WorkDayForm()
#         worker = User.objects.get(id=request.user.id)
#         work_day = WorkDay.objects.filter(employee=worker)
#         all_staff = WorkDay.objects.all()
#         context = {'call': call,
#                    'form': form,
#                    'submit': "Zapisz",
#                    'all_staff': all_staff,
#                    'worker': worker,
#                    'work_day': work_day,
#                    'previous_month':prev_month,
#                    'next_month':next_month,
#                    }
#
#         return render(request, 'WorkShedule/calendar_view.html', context)
#
#     def post(self, request,month_number=datetime.now().month):
#         form = WorkDayForm(request.POST)
#         if form.is_valid():
#             time_start = form.cleaned_data.get('time_start')
#             time_end = form.cleaned_data.get('time_end')
#             date_day = form.cleaned_data.get('date_day')
#             if WorkDay.objects.filter(employee_id=request.user.id) and WorkDay.objects.filter(date_day=date_day):
#                 WorkDay.objects.filter(date_day=date_day, employee_id=request.user.id).update(date_day=date_day,
#                                                                                               time_start=time_start,
#                                                                                               time_end=time_end)
#                 messages.success(request, 'Dzień poprawiony')
#                 return redirect('calendar',month_number=datetime.now().month)
#             else:
#                 WorkDay.objects.create(date_day=date_day, time_start=time_start, time_end=time_end,
#                                        employee_id=request.user.id)
#                 messages.info(request, 'Dzień Dodany')
#                 return redirect('calendar', month_number=datetime.now().month)




class DeleteDateDay(DeleteView):
    model = WorkDay
    success_url = reverse_lazy('calendar')
    def get_success_url(self):
        return reverse_lazy('calendar', kwargs={'month_number': datetime.now().month})





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
                return redirect(reverse_lazy('calendar',kwargs={'month_number': datetime.now().month}))
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

    return render(request, 'WorkShedule/home.html', {'Calendar' : mark_safe(lCalendar),
                                                       'Month' : lMonth,
                                                       'MonthName' : named_month(lMonth),
                                                       'Year' : lYear,
                                                       'PreviousMonth' : lPreviousMonth,
                                                       'PreviousMonthName' : named_month(lPreviousMonth),
                                                       'PreviousYear' : lPreviousYear,
                                                       'NextMonth' : lNextMonth,
                                                       'NextMonthName' : named_month(lNextMonth),
                                                       'NextYear' : lNextYear,
                                                       'YearBeforeThis' : lYearBeforeThis,
                                                       'YearAfterThis' : lYearAfterThis,
                                                   })