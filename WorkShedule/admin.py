from django.contrib import admin

# Register your models here.
from WorkShedule.models import WorkDay

class WordDayAdmin(admin.ModelAdmin):
    list_display = ('date_day','employee')
    list_filter = ('employee','date_day','date_free')

admin.site.register(WorkDay,WordDayAdmin)