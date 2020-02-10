from django.db import models
from django.urls import reverse

from django.contrib.auth import get_user_model

JOB_TYPE = (
    ('1', "Full time"),
    ('2', "Part time"),
    ('3', "Internship"),
)

class Job(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    description = models.TextField()
    location = models.CharField(max_length=300)
    job_type = models.CharField(choices=JOB_TYPE, max_length=10)
    category = models.CharField(max_length=100)
    last_date = models.DateTimeField()
    company_name = models.CharField(max_length=100)
    company_description = models.CharField(max_length=300)
    website = models.CharField(max_length=100, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    filled = models.BooleanField(default=False)
    salary = models.IntegerField(default=0, blank=True)

    class Meta:
        ordering = ('-created_at', )

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('jobs:jobs-detail',
                       kwargs={
                           'id': self.id,
                       })

class Applicant(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applicants')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name()
    
class About(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=60)
    messages = models.TextField()

    def __str__(self):
        return self.name
