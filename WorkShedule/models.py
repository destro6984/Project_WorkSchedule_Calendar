from datetime import timezone, datetime

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User


# Create your models here.



class WorkDay(models.Model):
    date_day = models.DateField(default=datetime.now)
    time_start = models.TimeField()
    time_end = models.TimeField()
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    # start_date = models.DateField(blank=True)
    # end_date = models.DateField(blank=True)

    def __str__(self):
        return f"time_start : {self.time_start}  time_end: {self.time_end}  employee: {self.employee} date_day: {self.date_day} "
