from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('JobRole', 'company', 'location', 'category', 'posted_by', 'posted_on')
    search_fields = ('JobRole', 'company', 'location', 'category')
    list_filter = ('category', 'posted_on')
