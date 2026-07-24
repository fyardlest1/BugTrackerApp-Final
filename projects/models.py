# project/models/py
from django.db import models, transaction
from accounts.models import BaseModel


class CompanyQuerySet(models.QuerySet):
    def for_company(self, company_id):
        return self.filter(company_id=company_id)
    
    def active(self):
        return self.filter(archived=False)
    
    def archived_only(self):
        return self.filter(archived=True)


class Project(BaseModel):
    company = models.ForeignKey('accounts.Company', on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    manager = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_projects')
    members = models.ManyToManyField('accounts.CustomUser', blank=True, related_name='projects')
    archived = models.BooleanField(default=False)
    archived_by_project = models.BooleanField(default=False)
    objects = CompanyQuerySet.as_manager()
    
    @transaction.atomic
    def archive(self):
        self.archived = True
        self.save()
        self.tickets.filter(archived=False).update(
            archived=True, archived_by_project=True)

    @transaction.atomic
    def restore(self):
        self.archived = False
        self.save()
        self.tickets.filter(archived_by_project=True).update(
            archived=False, archived_by_project=False)

    def __str__(self):
        return self.name

