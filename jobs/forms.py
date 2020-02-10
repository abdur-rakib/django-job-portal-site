from django import forms
from .models import Job, Applicant, About

from tempus_dominus.widgets import DatePicker, TimePicker, DateTimePicker

class CreateJobForm(forms.ModelForm):
    
    class Meta:
        model = Job
        exclude = ('user', 'created_at', )

class ApplyJobForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = ('job',)

class AboutForm(forms.ModelForm):
    class Meta:
        model = About
        fields = ('name', 'email', 'messages', )