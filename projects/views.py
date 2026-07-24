# projects/views.py
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth import get_user_model

from .models import Project
from .forms import ProjectForm
from .services import assign_project_manager, add_member

from accounts.mixins import CompanyScopedMixin
from accounts.permissions import can_create_project, can_manage_project


class ProjectListView(CompanyScopedMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        return super().get_queryset().active()


class ProjectDetailView(CompanyScopedMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.object.company
        context['project_managers'] = company.members_in_role('ProjectManager')
        context['assignables'] = company.members.exclude(
            groups__name='ProjectManager')
        return context


class ProjectCreateView(CompanyScopedMixin, UserPassesTestMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('projects:list')

    def form_valid(self, form):
        form.instance.company = self.request.user.company
        return super().form_valid(form)
    
    def test_func(self):
        return can_create_project(self.request.user)


class ProjectUpdateView(CompanyScopedMixin, UserPassesTestMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'

    def get_success_url(self):
        return reverse_lazy('projects:detail', kwargs={'pk': self.object.pk})

    def test_func(self):
        return can_manage_project(self.request.user, self.get_object())


class ProjectArchiveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk, company=request.user.company)
        
        if not can_manage_project(request.user, project):
            raise PermissionDenied
        
        project.archive()
        return redirect('projects:list')


class ProjectRestoreView(LoginRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk, company=request.user.company)
        
        if not can_manage_project(request.user, project):
            raise PermissionDenied
        
        project.restore()
        return redirect('projects:archived')


class ArchivedProjectListView(CompanyScopedMixin, ListView):
    model = Project
    template_name = 'projects/project_archived.html'
    context_object_name = 'projects'

    def get_queryset(self):
        return super().get_queryset().archived_only()


class SetManagerView(LoginRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(
            Project, pk=pk, company=request.user.company)
        pm = get_object_or_404(
            get_user_model(), pk=request.POST['pm'],
            company=request.user.company)
        assign_project_manager(request.user, project, pm)
        return redirect('projects:detail', pk=pk)


class AddMemberView(LoginRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(
            Project, pk=pk, company=request.user.company)
        member = get_object_or_404(
            get_user_model(), pk=request.POST['member'],
            company=request.user.company)
        add_member(request.user, project, member)
        return redirect('projects:detail', pk=pk)


class MyProjectListView(LoginRequiredMixin, ListView):
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        return user.projects.filter(company=user.company, archived=False)


