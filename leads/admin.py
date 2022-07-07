from django.contrib import admin

from .models import User, Lead, Agent, UserProfile, Category, FollowUp, LeadsSheet
from . import models


class LeadAdmin(admin.ModelAdmin):
    # fields = (
    #     'first_name',
    #     'last_name',
    # )

    list_display = ["first_name", "last_name", "source", "email"]
    list_display_links = ["first_name"]
    list_editable = ["last_name"]
    list_filter = ["category"]
    search_fields = ["first_name", "last_name", "email"]

class AgentAdmin(admin.ModelAdmin):
    fields = ['user', 'organisation', 'permissions']
    filter_horizontal = ['permissions']

class CategoryAdmin(admin.ModelAdmin):
    filter_horizontal = ['organisation']

admin.site.register(Category, CategoryAdmin)
admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(Lead, LeadAdmin)
admin.site.register(Agent, AgentAdmin)
admin.site.register(FollowUp)
admin.site.register(LeadsSheet)
admin.site.register(models.SalesReport)
