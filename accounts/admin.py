# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Company


# CustomUserAdmin est une classe qui hérite de UserAdmin pour personnaliser 
# l'affichage et la gestion du modèle CustomUser dans l'interface d'administration Django.
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'company']
    fieldsets = UserAdmin.fieldsets + (
        ("Entreprise", {'fields': ('company', 'avatar')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Entreprise", {'fields': ('company', 'avatar')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Company)
