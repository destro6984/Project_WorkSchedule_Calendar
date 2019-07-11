import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.checks import messages
from django.core.exceptions import ObjectDoesNotExist

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views import View
from django.contrib import messages
from django.core.mail import EmailMessage
from WorkShedule.forms import LoginUserForm, AddUserForm, WorkDayForm, HolidayForm, UserRegisterForm
from WorkShedule.utils import *
from .models import *


def is_enough_worker(month_number):
    """
    function to check is 3 or 2 worker per day

    list is printed at Alert button

    :param month_number:
    :return: list of days
    """
    date = datetime.today()
    current_day = date.replace(day=1, month=month_number)
    days_not_enough_worker = []
    while current_day.month == month_number:
        if (current_day.weekday() in range(0, 5)) and (
                WorkDay.objects.filter(date_day=current_day, date_free=False).count()) < 3 or \
                (current_day.weekday() in range(5, 7)) and (
                WorkDay.objects.filter(date_day=current_day, date_free=False).count()) < 2:
            days_not_enough_worker.append(current_day)
        current_day = current_day + timedelta(days=1)
    return days_not_enough_worker


def not_to_many_holiday(month_number, request):
    """
    function to check how many worker is on holiday per day

    list is printed at Alert Button
    If too many workers has free day they got the email to change their plans


    :param month_number:
    :param request:
    :return: list of days
    """
    date = datetime.today()
    current_day = date.replace(day=1, month=month_number)
    days_too_many_holiday = []
    while current_day.month == month_number:
        qs = WorkDay.objects.filter(date_day=current_day, date_free=True)
        if qs.count() > 2:
            days_too_many_holiday.append(current_day.strftime('%Y-%m-%d'))
            if request.GET.get('send'):
                emails = [workday.employee.email for workday in qs]
                email = EmailMessage(
                    "Your Holiday','Hey, there is too many people out during the time you've choosen, please wonder about another date",
                    to=emails)
                email.send()
                messages.success(request, "Warning Send")
                return days_too_many_holiday, redirect('calendar', month_number=datetime.now().month,
                                                       year=datetime.now().year)
        current_day = current_day + timedelta(days=1)
    return days_too_many_holiday

def about(request):
    return render(request,'WorkShedule/about.html')

class CalendarView(View):
    """
    Show the month with all workers per month with they holidays

    calendar is taken from utils.py form built-in python module calendar/HTML
    """

    def get(self, request, month_number=None, year=None):
        month_number = month_number if month_number is not None else datetime.now().month
        year = year if year is not None else datetime.now().year
        prev_month = (int(month_number) - 1)
        next_month = ((int(month_number) + 1))
        next_year = year
        previous_year = year
        if prev_month == 0:
            prev_month = 12
            previous_year = int(year) - 1
        if next_month == 13:
            next_month = 1
            next_year = int(year) + 1

        mycall = Calendar(year, int(month_number))
        call = mycall.formatmonth(withyear=True)
        not_enough_worker_list = is_enough_worker(int(month_number))
        not_to_many_holiday_list = not_to_many_holiday(int(month_number), request)

        if request.user.is_authenticated:
            worker = User.objects.get(id=request.user.id)
            work_day = WorkDay.objects.filter(employee=worker, date_day__month=month_number)
        else:
            worker = None
            work_day = WorkDay.objects.all()
        all_staff = WorkDay.objects.filter(date_day__month=month_number)
        workers_for_current_day = WorkDay.objects.filter(date_day=datetime.today().strftime('%Y-%m-%d'))
        context = {'call': call,
                   'submit': "Save",
                   'all_staff': all_staff,
                   'worker': worker,
                   'work_day': work_day,
                   'prev_month': prev_month,
                   'next_month': next_month,
                   'month_number': month_number,
                   'next_year': next_year,
                   'previous_year': previous_year,
                   'workers_for_current_day': workers_for_current_day,
                   'year': year,
                   'not_enough_worker_list': not_enough_worker_list,
                   'not_to_many_holiday_list': not_to_many_holiday_list,
                   }

        return render(request, 'WorkShedule/calendar_view.html', context)


class AddDefault(View):
    """
    Allows to set default schedule for worker depending on what days worker choose,
    form is on PersonalView
    """

    def post(self, request, month_number, year):
        month_number = int(month_number)
        date = datetime.today()
        current_day = date.replace(day=1, month=(int(month_number)))
        is_saturdays = request.POST.get('sat', False)
        is_sundays = request.POST.get('sun', False)
        only_workdays = request.POST.get('workdays', False)
        all_days = request.POST.get('all_days', False)
        start_time_valid = request.POST.get('start_time', False)
        type_of_days=any(key in ['workdays','sun','sat','all_days'] for key in request.POST.keys())
        if start_time_valid ==False or type_of_days == False:
            messages.warning(request, "Choose Start Time and type of days")
            return redirect('personal_schedule', month_number=month_number, year=year)
        while current_day.month == month_number:
            time_start = date.replace(hour=int(request.POST['start_time']), minute=0, second=0, microsecond=0)
            time_end = time_start + timedelta(hours=8)
            if current_day.weekday() in range(0, 5) and only_workdays or \
                    (current_day.weekday() == 5 and is_saturdays) or \
                    (current_day.weekday() == 6 and is_sundays) or \
                    all_days:
                try:
                    WorkDay.objects.get(date_day=current_day, employee=request.user, date_free=True)
                except ObjectDoesNotExist:

                    WorkDay.objects.update_or_create(
                        date_day=current_day, employee_id=request.user.id, date_free=False,
                        defaults={'time_start': time_start,
                                  'time_end': time_end})
            current_day = current_day + timedelta(days=1)
        messages.success(request, "Added")
        return redirect('personal_schedule', month_number=month_number, year=year)


class PersonalScheduleView(LoginRequiredMixin, View):
    """
    Shows personal Schedule for worker,
    allows: adding days-single/range
    adding holiday
    """

    def get(self, request, month_number, year=None):
        year = year if year is not None else datetime.now().year
        calendar = CalendarForUser(year, int(month_number), user=request.user)
        prev_month = (int(month_number) - 1)
        next_month = ((int(month_number) + 1))
        next_year = year
        previous_year = year
        if prev_month == 0:
            prev_month = 12
            previous_year = int(year) - 1
        if next_month == 13:
            next_month = 1
            next_year = int(year) + 1

        calendar_for_user = calendar.formatmonth(withyear=True)
        form = WorkDayForm()
        form_holiday = HolidayForm()
        if request.user.is_authenticated:
            worker = User.objects.get(id=request.user.id)
            work_day = WorkDay.objects.filter(employee=worker, date_day__month=month_number)
        else:
            worker = None
            work_day = WorkDay.objects.all()
        all_staff = WorkDay.objects.all()
        number_of_avaiable_holiday_days = 26 - WorkDay.objects.filter(employee=worker, date_free=True).count()

        return render(request, 'WorkShedule/personal_schedule.html', context={'calendar_for_user': calendar_for_user,
                                                                              'next_month': next_month,
                                                                              'prev_month': prev_month,
                                                                              'form': form,
                                                                              'form_holiday': form_holiday,
                                                                              'submit': 'Save',
                                                                              'month_number': month_number,
                                                                              'worker': worker,
                                                                              'all_staff': all_staff,
                                                                              'work_day': work_day,
                                                                              'number_of_avaiable_holiday_days': number_of_avaiable_holiday_days,
                                                                              'next_year': next_year,
                                                                              'previous_year': previous_year,
                                                                              'year': year,
                                                                              })

    def post(self, request, month_number=None, year=None):
        year = year if year is not None else datetime.now().year
        month_number = month_number if month_number is not None else datetime.now().month
        form = WorkDayForm(request.POST)
        valid = form.is_valid()
        if valid:
            time_start = form.cleaned_data.get('time_start')
            time_end = form.cleaned_data.get('time_end')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            employee_id = self.request.user.id
        else:
            messages.error(request, 'Error Data')
            return redirect(reverse_lazy('personal_schedule', kwargs={'month_number': month_number, 'year': year}))

        new_days_update_days = self.add_range_days(request, start_date, end_date, time_start, time_end, employee_id)

        return redirect('personal_schedule', month_number=month_number, year=year)

    def add_range_days(self, request, start_date, end_date, time_start, time_end, employee_id):
        """
        funtion to add one or range of days

        :param request:
        :param start_date:
        :param end_date:
        :param time_start:
        :param time_end:
        :param employee_id:
        :return: Add days/range/single
        """
        working_day = start_date
        if end_date != None:
            while (working_day <= end_date):
                try:
                    WorkDay.objects.get(date_day=working_day, employee=request.user, date_free=True)
                except ObjectDoesNotExist:
                    WorkDay.objects.update_or_create(
                        date_day=working_day, employee_id=employee_id, date_free=False,
                        defaults={'time_start': time_start,
                                  'time_end': time_end})
                working_day = working_day + timedelta(days=1)
            messages.success(request, 'Added')
        else:
            try:
                WorkDay.objects.get(date_day=working_day, employee=request.user, date_free=True)
            except ObjectDoesNotExist:
                WorkDay.objects.update_or_create(date_day=working_day, employee_id=employee_id, date_free=False,
                                                 defaults={'time_start': time_start,
                                                           'time_end': time_end,
                                                           })
            messages.success(request, 'Added')


class AddHoliday(View):
    """
    adding holidays, check the number of day which can taken as holidays
    """

    def post(self, request, month_number, year):
        form = HolidayForm(request.POST)

        if form.is_valid():
            start_date_free = form.cleaned_data.get('start_date_free', False)
            end_date_free = form.cleaned_data.get('end_date_free', False)
            date_free = form.cleaned_data.get('date_free')
            free_day = start_date_free
            number_of_avaiable_holiday_days = 26 - WorkDay.objects.filter(employee=request.user.id,
                                                                          date_free=True).count()
            try:
                counter = (end_date_free - start_date_free).days
            except:
                counter = 1
            if (number_of_avaiable_holiday_days > 0 and WorkDay.objects.filter(employee_id=request.user.id,
                                                                               date_free=True).count() <= 26) and 0 < counter <= number_of_avaiable_holiday_days:
                if end_date_free != None:
                    while (free_day <= end_date_free):
                        WorkDay.objects.update_or_create(
                            date_day=free_day, employee_id=request.user.id, defaults={'date_day': free_day,
                                                                                      'date_free': date_free,
                                                                                      'time_start': None,
                                                                                      'time_end': None})
                        free_day = free_day + timedelta(days=1)
                    messages.info(request, 'Holiday Added')
                else:
                    WorkDay.objects.update_or_create(date_day=free_day, employee_id=request.user.id,
                                                     defaults={'date_day': free_day,
                                                               'date_free': date_free,
                                                               'time_start': None,
                                                               'time_end': None,
                                                               })
                    messages.info(request, 'Holiday Added')
            else:
                messages.error(request, 'Not enough Days')
                return redirect(reverse_lazy('personal_schedule', kwargs={'month_number': month_number, 'year': year}))

        return redirect('personal_schedule', month_number=month_number, year=year)


class DeleteDateDay(View):
    """
    allows to delete days, form list, with checkbox
    GET redirect from PersonalView, confirmation to delete
    """

    def get(self, request, month_number, year):
        year = year if year is not None else datetime.now().year
        list_day_to_delete = []
        for key, value in request.GET.items():
            if value == "on":
                day_to_delete = WorkDay.objects.get(pk=key)
                list_day_to_delete.append(day_to_delete)
        return render(request, 'WorkShedule/workday_confirm_delete.html',
                      context={'list_day_to_delete': list_day_to_delete,
                               'month_number': month_number,
                               'year': year})

    def post(self, request, month_number, year):
        for key, value in request.GET.items():
            if value == "on":
                day_to_delete = WorkDay.objects.filter(pk=key)
                day_to_delete.delete()
        messages.warning(request, "Deleted")
        return redirect('personal_schedule', month_number=month_number, year=year)


class LoginUser(View):
    """
    login module
    """

    def get(self, request):
        form = LoginUserForm()
        context = {'form': form, 'submit': "Log in"}
        return render(request, 'WorkShedule/login.html', context)

    def post(self, request):
        form = LoginUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('login')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse_lazy('calendar', kwargs={'month_number': datetime.now().month,
                                                                 'year': datetime.now().year}))
            else:
                message = "<h3 class='text-center'>Wrong user or password</h3>"
                context = {'form': form, 'submit': "Log in", 'message': message}
                return render(request, 'WorkShedule/login.html', context)
        else:
            context = {'form': form, 'submit': "Log in"}
            return render(request, 'WorkShedule/login.html', context)


class Logout(View):
    """
    logout module
    """

    def get(self, request):
        logout(request)
        messages.info(request, "Logged Out")
        return redirect('start')


class RegisterUser(View):
    """
    registration module
    """

    def get(self, request):
        form = UserRegisterForm()
        return render(request, 'WorkShedule/register.html', context={'form': form})

    def post(self, request):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'{username} Your Account has been created, You are now able to login')
            return redirect('login')
        else:
            form = UserRegisterForm(request.POST)
        return render(request, 'WorkShedule/register.html', context={'form': form})


class AddUser(View):
    """
    register user manually validation/not used just to practise/
    """

    def get(self, request):
        form = AddUserForm()
        context = {'form': form, "submit": "Add"}
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
            messages.success(request, message="New user Added")
            return redirect('start')
        else:
            messages.warning(request, "Error")
            context = {'form': form, "submit": "Add"}
            return render(request, 'WorkShedule/form.html', context)


def EmailWarrning():
    # test/rubish
    email = EmailMessage('title', 'body', to=['a.m.@gmail.com'])
    email.send()
    return


class Homepage(View):
    # test/rubish
    def get(self, request):
        return render(request, 'WorkShedule/base.html')


class TestView(View):
    # test/rubish
    def get(self, request, day=datetime.now()):
        cal = CalendarForUser(day.year, day.month, user=request.user)

        html_cal = cal.formatmonth(withyear=True)
        return render(request, 'WorkShedule/home.html', context={'html_cal': html_cal})

# test/rubish
# def get_context(self,request,month_number):
#     day = datetime.now()
#     cal = Calendar(day.year, day.month)
#     html_cal = cal.formatmonth(withyear=True)
#     return {'html_cal': html_cal}
