"""Projekt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib.auth import views

from WorkShedule.views import Homepage, CalendarView, LoginUser, Logout, DeleteDateDay, TestView, AddDefault, \
    PersonalScheduleView, AddHoliday, RegisterUser

urlpatterns = [
    url(r'^$', Homepage.as_view(), name='start'),
    url(r'^calendar/(?P<month_number>\d+)/(?P<year>\d{4})$', CalendarView.as_view(), name='calendar'),
    url(r'^login/$', LoginUser.as_view(), name='login'),
    url(r'^logout/$', Logout.as_view(), name='logout'),
    url(r'^home/$', TestView.as_view(), name='TestView'),
    url(r'^add_default/(?P<month_number>\d+)/(?P<year>\d{4})$', AddDefault.as_view(), name='add_default'),
    url(r'^personal_schedule/(?P<month_number>\d+)/(?P<year>\d{4})$', PersonalScheduleView.as_view(), name='personal_schedule'),
    url(r'^add_holiday/(?P<month_number>\d+)/(?P<year>\d{4})$', AddHoliday.as_view(), name='add_holiday'),
    url(r'^delete_day/(?P<month_number>\d+)/(?P<year>\d{4})$', DeleteDateDay.as_view(), name='delete_day'),
    url(r'^register/$', RegisterUser.as_view(), name='register'),
    url(r'^password-reset/$', views.PasswordResetView.as_view(template_name="WorkShedule/password_reset.html"), name='password_reset'),
    url(r'^password-reset/done/$', views.PasswordResetDoneView.as_view(template_name="WorkShedule/password_reset_done.html"), name='password_reset_done'),
    url(r'^password-reset-confirm/(?P<uidb64>.+)/(?P<token>.+)/$', views.PasswordResetConfirmView.as_view(template_name="WorkShedule/password_reset_confirm.html"), name='password_reset_confirm'),
    url(r'^password-reset-complete/$', views.PasswordResetCompleteView.as_view(template_name="WorkShedule/password_reset_complete.html"), name='password_reset_complete'),





]

