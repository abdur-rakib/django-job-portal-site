from django import forms
from .models import Job

from tempus_dominus.widgets import DatePicker, TimePicker, DateTimePicker

class CreateJobForm(forms.ModelForm):
    
    class Meta:
        model = Job
        exclude = ('user', 'created_at', )
