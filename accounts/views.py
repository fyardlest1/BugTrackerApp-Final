# accounts/views.py
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction
from django.db.models import Count
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.contrib import messages
from django.core import signing
from django.core.mail import send_mail
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView, TemplateView, UpdateView
from django.urls import reverse_lazy, reverse
from django.views import View

from .forms import RegisterForm, CompanyForm, CompanyRegisterForm, ProfileForm
from notifications.services import notify_many
from notifications.email_service import send_html_email
from .models import Company, Roles
from .services import change_user_role
from .invites import make_invite_token, read_invite_token


# class RegisterView(CreateView):
#     form_class = RegisterForm
#     template_name = 'registration/register.html'
#     success_url = reverse_lazy('login')
    
class RegisterView(CreateView):
    form_class = CompanyRegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        with transaction.atomic():
            company = Company.objects.create(
                name=form.cleaned_data['company_name'])
            user = form.save(commit=False)
            user.company = company
            user.save()
            user.groups.add(Group.objects.get(name=Roles.ADMIN))
        return redirect(self.success_url)


class CompanyDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/company_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.request.user.company
        context['roles'] = Roles.choices
        context['company'] = company
        # context['members'] = company.members.all()
        context['members'] = get_user_model().objects.filter(
            company=self.request.user.company).annotate(
            nb_projets=Count('projects', distinct=True))
        context['projects'] = company.projects.all()[:5]
        
        return context


class CompanyUpdateView(LoginRequiredMixin, UserPassesTestMixin,
                        UpdateView):
    form_class = CompanyForm
    template_name = 'accounts/company_form.html'
    success_url = reverse_lazy('company')

    def test_func(self):
        return self.request.user.role == Roles.ADMIN

    def get_object(self):
        return self.request.user.company


class ChangeRoleView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.role == Roles.ADMIN

    def post(self, request, pk):
        target = get_object_or_404(
            get_user_model(), pk=pk, company=request.user.company)
        change_user_role(request.user, target, request.POST['role'])
        return redirect('company')


# pour le compte demo

DEMO_USERNAMES = {
    'Admin': 'demo.admin', 'ProjectManager': 'demo.pm',
    'Developer': 'demo.dev', 'Submitter': 'demo.submitter',
}

class DemoLoginView(View):
    def post(self, request):
        role = request.POST.get('role')
        username = DEMO_USERNAMES.get(role)
        if not username:
            return redirect('login')
        user = get_object_or_404(get_user_model(), username=username)
        login(request, user)
        return redirect('home')


class CreateInviteView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.role == Roles.ADMIN

    def post(self, request):
        email = request.POST['email']
        token = make_invite_token(request.user.company_id, email)
        
        lien = request.build_absolute_uri(
            reverse('register_invite') + f'?token={token}')
        
        # print("Lien d'invitation :", lien)   # pratique en dev, à retirer ensuite pour la production
        # send_mail(
        #     'Invitation à rejoindre BugTracker',
        #     f'Vous êtes invité. Inscrivez-vous ici : {lien}',
        #     None, [email])
        
        send_html_email(
            'Invitation à rejoindre BugTracker',
            [email],
            'emails/invitation.html',
            {'lien': lien}
        )        
        messages.success(request, f'Invitation envoyée à {email}.')
        return redirect('company')


class RegisterByInviteView(View):
    template_name = 'registration/register_invite.html'

    def get(self, request):
        token = request.GET.get('token', '')
        try:
            read_invite_token(token)
        except signing.BadSignature:
            return render(request, 'registration/invite_invalid.html')
        return render(request, self.template_name, {'form': RegisterForm(), 'token': token})

    def post(self, request):
        token = request.POST.get('token', '')
        try:
            data = read_invite_token(token)
        except signing.BadSignature:
            return render(request, 'registration/invite_invalid.html')
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.company_id = data['company_id']
            user.save()
            
            admins = get_user_model().objects.filter(
                company_id=data['company_id'], groups__name=Roles.ADMIN)
            notify_many(admins,
                f'{user.username} a rejoint votre entreprise.',
                reverse('company'))

            user.groups.add(Group.objects.get(name=Roles.SUBMITTER))
            return redirect('login')
        
        context = {'form': form, 'token': token}
        return render(request, self.template_name, context)


class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin,
                        UpdateView):
    form_class = ProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('profile')
    success_message = 'Profil mis à jour.'

    def get_object(self):
        return self.request.user