from django.contrib import admin
from muver_api.models import UserProfile, Job


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'mover', 'billing_saved')


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'description', 'price',
                    'complete', 'charge_id', 'mover_profile', 'image_url')
