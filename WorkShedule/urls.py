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
from django.contrib import admin
from django.urls import path, include

from WorkShedule.views import Homepage, CalendarView, LoginUser, Logout, DeleteDateDay, calendar, TestView

urlpatterns = [
    url(r'^$', Homepage.as_view(), name='start'),
    url(r'^calendar/(?P<month_number>\d+)$', CalendarView.as_view(), name='calendar'),
    url(r'^login/$', LoginUser.as_view(), name='login'),
    url(r'^logout/$', Logout.as_view(), name='logout'),
    url(r'^home/$', TestView.as_view(), name='TestView'),

    url(r'^delete_day/(?P<month_number>\d+)$', DeleteDateDay.as_view(), name='delete_day'),





]

