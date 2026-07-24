# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views
from .forms import StyledAuthenticationForm, StyledPasswordChangeForm


urlpatterns = [
        path('login/', auth_views.LoginView.as_view(
                authentication_form=StyledAuthenticationForm), name='login'),
        path('logout/', auth_views.LogoutView.as_view(), name='logout'),
        path('register/', views.RegisterView.as_view(), name='register'),
        # Company routes
        path('entreprise/', views.CompanyDetailView.as_view(), name='company'),
        path('entreprise/modifier/', views.CompanyUpdateView.as_view(),
                name='company_edit'),
        # Member routes
        path('membres/<uuid:pk>/role/', views.ChangeRoleView.as_view(), name='change_role'),
        # Demo account
        path('demo/', views.DemoLoginView.as_view(), name='demo_login'),
        # email token
        path('inviter/', views.CreateInviteView.as_view(), name='create_invite'),
        path('inscription/invitation/', views.RegisterByInviteView.as_view(), name='register_invite'),
        # modifier le profil utilisateur
        path('profil/', views.ProfileUpdateView.as_view(), name='profile'),
        path('profil/mot-de-passe/', auth_views.PasswordChangeView.as_view(
                form_class=StyledPasswordChangeForm,
                template_name='registration/password_change_form.html',
                success_url=reverse_lazy('password_change_done')),
                name='password_change'),
        path('profil/mot-de-passe/ok/',
                auth_views.PasswordChangeDoneView.as_view(
                template_name='registration/password_change_done.html'),
                name='password_change_done'),

]
