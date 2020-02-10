from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView

from .models import *
from .forms import *


class HomeView(ListView):
    model = Job
    template_name = 'home.html'
    context_object_name = 'jobs'

    extra_context = {
        'home_page': 'active'
    }

    def get_queryset(self):
        return self.model.objects.all()[:6]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trendings'] = self.model.objects.filter(
            created_at__month=timezone.now().month)[:3]
        return context


class SearchView(ListView):
    model = Job
    template_name = 'jobs/search.html'
    context_object_name = 'jobs'

    def get_queryset(self):
        return self.model.objects.filter(
            location__icontains=self.request.GET['location'],
            title__icontains=self.request.GET['position']
        )


class JobListView(ListView):
    model = Job
    context_object_name = 'jobs'
    template_name = 'jobs/jobs.html'
    paginate_by = 5


class JobDetailView(DetailView):
    model = Job
    template_name = 'jobs/details.html'
    context_object_name = 'job'
    pk_url_kwarg = 'id'

    def get_object(self, queryset=None):
        return super(JobDetailView, self).get_object(queryset=queryset)
        if obj is None:
            raise Http404('Job does not exists')
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class Dashboard(ListView):
    model = Job
    template_name = 'jobs/employer/dashboard.html'
    context_object_name = 'jobs'

    @method_decorator(login_required(login_url=reverse_lazy('accounts:login')))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(self.request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.filter(user_id=self.request.user.id)


class JobCreateView(CreateView):
    # model = Job
    # template_name = 'jobs/create.html'
    # form_class = CreateJobForm
    # extra_context = {
    #     'title': 'Post New Job'
    # }

    # @method_decorator(login_required(login_url=reverse_lazy('accounts:login')))
    # def dispatch(self, request, *args, **kwargs):
    #     if not self.request.user.is_authenticated:
    #         return reverse_lazy('accounts:login')
    #     if self.request.user.is_authenticated and self.request.user.role != 'employer':
    #         return reverse_lazy('accounts:login')
    #     return super().dispatch(self.request, *args, **kwargs)

    # def post(self, request, *args, **kwargs):
    #     form = self.form_class(data=request.POST)

    #     if form.is_valid():
    #         job = form.save(commit=False)
    #         job.user = self.request.user
    #         job.company_name = self.request.user.first_name
    #         job.save()
    #         return redirect(reverse_lazy('jobs:employer-dashboard'))
    #     else:
    #         form = self.form_class()
    #     return render(request, 'jobs/create.html', {'form': form})

    @method_decorator(login_required(login_url=reverse_lazy('accounts:login')))
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return reverse_lazy('accounts:login')
        if self.request.user.is_authenticated and self.request.user.role != 'employer':
            return reverse_lazy('accounts:login')
        return super().dispatch(self.request, *args, **kwargs)


    def get(self, request, *args, **kwargs):
        context = {'form': CreateJobForm()}
        return render(request, 'jobs/create.html', context)
    
    def post(self, request, *args, **kwargs):
        form = CreateJobForm(request.POST)

        if form.is_valid():
            job = form.save(commit=False)
            job.user = self.request.user
            job.company_name = self.request.user.first_name
            job.save()
            messages.success(request, 'Job posted successflly')
            return HttpResponseRedirect(reverse_lazy('jobs:employer-dashboard'))
        return render(request, 'jobs/create.html', {'form': form})


class ApplyJobView(CreateView):
    model = Applicant
    form_class = ApplyJobForm
    slug_field = 'job_id'
    slug_url_kwarg = 'job_id'

    @method_decorator(login_required(login_url=reverse_lazy('accounts:login')))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(self.request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            messages.info(self.request, 'Successfully applied for the job!')
            return self.form_valid(form)
        else:
            return HttpResponseRedirect(reverse_lazy('jobs:home'))

    def get_success_url(self):
        return reverse_lazy('jobs:jobs-detail', kwargs={'id': self.kwargs['job_id']})

    # def get_form_kwargs(self):
    #     kwargs = super(ApplyJobView, self).get_form_kwargs()
    #     print(kwargs)
    #     kwargs['job'] = 1
    #     return kwargs

    def form_valid(self, form):
        # check if user already applied
        applicant = Applicant.objects.filter(user_id=self.request.user.id, job_id=self.kwargs['job_id'])
        if applicant:
            messages.info(self.request, 'You already applied for this job')
            return HttpResponseRedirect(self.get_success_url())
        # save applicant
        form.instance.user = self.request.user
        form.save()
        return super().form_valid(form)


class ApplicantsListView(ListView):
    model = Applicant
    template_name = 'jobs/employer/all-applicants.html'
    context_object_name = 'applicants'

    def get_queryset(self):
        # jobs = Job.objects.filter(user_id=self.request.user.id)
        return self.model.objects.filter(job__user_id=self.request.user.id)

@login_required(login_url=reverse_lazy('accounts:login'))
def filled(request, job_id=None):
    try:
        job = Job.objects.get(user_id=request.user.id, id=job_id)
        job.filled = True
        job.save()
    except IntegrityError as e:
        print(e.message)
        return HttpResponseRedirect(reverse_lazy('jobs:employer-dashboard'))
    return HttpResponseRedirect(reverse_lazy('jobs:employer-dashboard'))

@login_required(login_url=reverse_lazy('accounts:login'))
def delete(request, job_id=None):
    try:
        job = Job.objects.get(user_id=request.user.id, id=job_id)
        job.delete()
    except IntegrityError as e:
        print(e.message)
        return HttpResponseRedirect(reverse_lazy('jobs:employer-dashboard'))
    return HttpResponseRedirect(reverse_lazy('jobs:employer-dashboard'))
