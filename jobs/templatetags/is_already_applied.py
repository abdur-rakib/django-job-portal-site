from django import template
register = template.Library()

from ..models import Applicant


@register.simple_tag(name='is_applied')
def is_already_applied(job, user):
    applied = Applicant.objects.filter(job=job, user=user)
    if applied:
        return True
    else:
        return False
