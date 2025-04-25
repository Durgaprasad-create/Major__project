"""
URL configuration for job_adver project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from job_app import views
from job_app .views import employer_register, employee_register,register,login_view,logout_view,post_job
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('', include('job_app.jurls')),
    path('register/', register, name='register'),
    path('register/employer/', employer_register, name='employer_register'),
    path('register/employee/', employee_register, name='employee_register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('post-job/', post_job, name='post_job'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('category/<str:category>/', views.job_category, name='job_category'),
    path('jobs/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('job/<int:job_id>/view-applicants/', views.view_applicants, name='view_applicants'),
    path('delete-job/<int:job_id>/', views.delete_job, name='delete_job'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
