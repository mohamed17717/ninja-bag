from django.contrib import admin
from .models import Profile, WebRequest
# Register your models here.
# admin.site.register(WebRequest)
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
  def has_add_permission(self, request, obj=None):
    return False

  # This will help you to disable delete functionaliyt
  def has_delete_permission(self, request, obj=None):
    return False

  # This will help you to disable change functionality
  def has_change_permission(self, request, obj=None):
    return False

@admin.register(WebRequest)
class TwtAdmin(admin.ModelAdmin):
  list_display = ('__str__',)
  actions = ['download_csv']

  def has_add_permission(self, request, obj=None):
    return False

  # This will help you to disable delete functionaliyt
  def has_delete_permission(self, request, obj=None):
    return False

  # This will help you to disable change functionality
  def has_change_permission(self, request, obj=None):
    return False

  def download_csv(self, request, queryset):
    import csv
    from django.http import HttpResponse
    from io import StringIO

    f = StringIO()
    writer = csv.writer(f)
    writer.writerow(["data"])

    for s in queryset:
      writer.writerow([str(s)])

    f.seek(0)
    response = HttpResponse(f, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=stat-info.csv'
    return response