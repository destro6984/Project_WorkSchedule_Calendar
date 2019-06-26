# Tutaj napisze clase która mi dziedziczy po clasie wbudowanej w python modul calandar , to mi stworzy html calanedarz

import calendar
from calendar import HTMLCalendar
from datetime import date, timedelta

from .models import *
from django.contrib.auth.models import User

import locale

locale.setlocale(locale.LC_TIME, 'pl_PL.utf8')


# class MyCalendar(HTMLCalendar):
#     def __init__(self, workdays=None):
#         super(MyCalendar, self).__init__()
#         self.workdays = workdays
#
#     def formatday(self, day, weekday, workdays):
#
#         workdays = workdays.filter(date_day__day=day)
#         print(workdays)
#
#         now = datetime.now()
#         employee_work_that_day = WorkDay.objects.filter(date_day__day=day, date_day__month=now.month,
#                                                         date_day__year=now.year)
#         employee_that_day = ''
#         for employee in employee_work_that_day:
#             employee_that_day += f'<span>{employee.employee}<br>{employee.time_start}-{employee.time_end}<br></span>'
#
#         if day != 0:
#             return f"<td width='120'' height='120' ><span class='date'>{day}</span><ul>{employee_that_day}</ul></td>"
#         return '<td></td>'
#
#     def formatweek(self, theweek, workdays):
#         """
#         Return a complete week as a table row.
#         """
#         s = ''.join(self.formatday(d, wd, workdays) for (d, wd) in theweek)
#         return '<tr>%s</tr>' % s
#
#     def formatmonth(self, theyear, themonth, withyear=True):
#         """
#         Return a formatted month as a table.
#         """
#
#         workdays = WorkDay.objects.filter(date_day__month=themonth)
#         v = []
#         a = v.append
#         a('<table border="2" cellpadding="0" cellspacing="0" class="month">')
#         a('\n')
#         a(self.formatmonthname(theyear, themonth, withyear=withyear))
#         a('\n')
#         a(self.formatweekheader())
#         a('\n')
#         for week in self.monthdays2calendar(theyear, themonth):
#             a(self.formatweek(week, workdays))
#             a('\n')
#         a('</table>')
#         a('\n')
#         return ''.join(v)


class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        super(Calendar, self).__init__()

    def formatday(self, day, workday):

        employee_that_day = workday.filter(date_day__day=day)
        d = ''
        for worker in employee_that_day:
            d += f'<p class=""> {worker.employee}:{worker.time_start}-{worker.time_end}<br> </p>'

        if day != 0:
            return f"<td width='100'' height='90'><span class='date mb-10'>{day}</span><p>{d}</p></td>"
        return '<td></td>'

    # formats a week as a t
    def formatweek(self, theweek, workday):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, workday)
        return f'<tr> {week} </tr>'

    # formats a month as a table
    # filter events by year and month
    def formatweekday(self, day):
        """
        Return a weekday name as a table header.
        """
        return '<th class="%s text-center">%s</th>' % (self.cssclasses[day], calendar.day_abbr[day])

    def formatweekheader(self):
        """
        Return a header for a week as a table row.
        """
        s = ''.join(self.formatweekday(i) for i in self.iterweekdays())
        return '<tr>%s</tr>' % s

    def formatmonthname(self, theyear, themonth, withyear=True):
        """
        Return a month name as a table row.
        """
        if withyear:
            s = '%s %s' % (calendar.month_name[themonth], theyear)
        else:
            s = '%s' % calendar.month_name[themonth]
        return '<tr><th colspan="7" class="month text-center">%s</th></tr>' % s



    def formatmonth(self, withyear=True):
        workdays = WorkDay.objects.filter(date_day__year=self.year,date_day__month=self.month)

        cal = f'<table border="2" cellpadding="0" cellspacing="0" class="calendar col-8 mr-1">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, workdays)}\n'

        return cal
