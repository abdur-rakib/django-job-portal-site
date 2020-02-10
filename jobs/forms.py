from django import forms
from .models import Job, Applicant

from tempus_dominus.widgets import DatePicker, TimePicker, DateTimePicker

class CreateJobForm(forms.ModelForm):
    
    class Meta:
        model = Job
        exclude = ('user', 'created_at', )

class ApplyJobForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = ('job',)