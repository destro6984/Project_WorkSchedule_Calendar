# Tutaj napisze clase która mi dziedziczy po clasie wbudowanej w python modul calandar , to mi stworzy html calanedarz

import calendar
from calendar import HTMLCalendar
from datetime import date, timedelta

from .models import *
from django.contrib.auth.models import User

import locale

# locale.setlocale(locale.LC_TIME, 'pl_PL.utf8')
locale.setlocale(locale.LC_TIME, 'en_US.utf8')



class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None, free_day=None, workers=None):
        self.year = int(year)
        self.month = month
        self.free_day = free_day
        self.workers= workers
        super(Calendar, self).__init__()

    def formatday(self, day, workday, workers=0):

        employee_that_day = workday.filter(date_day__day=day, date_free=False)

        holiday = workday.filter(date_day__day=day, date_free=True)
        d = ''


        for worker in employee_that_day:
            d += f"<li> {worker.employee}:{worker.time_start.strftime('%H:%M')}-{worker.time_end.strftime('%H:%M')}<br></li>"
            workers = workday.filter(date_day__day=day, date_free=False).count()
        for worker in holiday:
            d += f'<li class="holiday"> {worker.employee}:Holiday <br></li>'

        if day != 0:
            return f"<td>{day}<br><div class='dropdown'><button class='dropdown-toggle' type='button' data-toggle='dropdown'>Number of workers:{workers}</button> <ul class='dropdown-menu' style='padding-left: 0;'>{d}</ul></div></td>"
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
        return '<tr><th colspan=7 class=" month text-center" style="text-transform: uppercase;">%s</th></tr>' % s

    def formatmonth(self, withyear=True):
        workdays = WorkDay.objects.filter(date_day__year=self.year, date_day__month=self.month)

        cal = f"<table border='0' cellpadding='0' cellspacing='0' class='container calendar' style='width: 100%; word-wrap:break-word'>\n"
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, workdays)}\n'

        return cal


class CalendarForUser(Calendar):
    def __init__(self, year=None, month=None, user=None):
        self.user = user
        super().__init__(year, month)

    def formatday(self, day, workday):

        employee_that_day = workday.filter(date_day__day=day, employee=self.user, date_free=False)
        holiday = workday.filter(date_day__day=day,employee=self.user, date_free=True)
        d = ''
        for worker in employee_that_day:
            d += f'<a> {worker.employee}:{worker.time_start}-{worker.time_end}<br></a>'
        for worker in holiday:
            d += f'<a class="holiday"> {worker.employee}:holiday <br></a>'

        if day != 0:
            return f"<td><span class='date'>{day}<br></span><a>{d}</a></td>"
        return '<td></td>'
