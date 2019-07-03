from datetime import timezone, datetime

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class WorkDay(models.Model):
    date_day = models.DateField(null=True, blank=True)
    time_start = models.TimeField(null=True, blank=True)
    time_end = models.TimeField(null=True, blank=True)
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    date_free = models.BooleanField(default=False)

    class Meta:
        unique_together = ('date_day', 'employee',)

    def __str__(self):
        return f"time_start : {self.time_start}  time_end: {self.time_end}  employee: {self.employee} date_day: {self.date_day} date_free: {self.date_free}"
