from django.contrib import admin

from .models import Category, Tool, UpcomingTool, SuggestedTool, ToolIssueReport, ToolViewsFunctions

admin.site.register(Category)
admin.site.register(Tool)
admin.site.register(UpcomingTool)
admin.site.register(SuggestedTool)
admin.site.register(ToolIssueReport)
# admin.site.register(ToolViewsFunctions)
