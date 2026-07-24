# projects/urls.py
from django.urls import path
from . import views


app_name = 'projects'
urlpatterns = [
    path('', views.ProjectListView.as_view(), name='list'),
    path('<uuid:pk>/', views.ProjectDetailView.as_view(), name='detail'),
    path('nouveau/', views.ProjectCreateView.as_view(), name='create'),
    path('<uuid:pk>/modifier/', views.ProjectUpdateView.as_view(), name='update'),
    path('<uuid:pk>/archiver/', views.ProjectArchiveView.as_view(), name='archive'),
    path('<uuid:pk>/restaurer/', views.ProjectRestoreView.as_view(), name='restore'),
    path('archives/', views.ArchivedProjectListView.as_view(), name='archived'),
    path('<uuid:pk>/chef/', views.SetManagerView.as_view(), name='set_manager'),
    path('<uuid:pk>/membres/ajouter/', views.AddMemberView.as_view(), name='add_member'),
    path('mes-projets/', views.MyProjectListView.as_view(), name='my_projects'),
]
