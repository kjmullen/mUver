from django.contrib import admin
from muver_api.models import UserProfile, Job


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'in_progress', 'mover', 'customer_id',
                    'stripe_account_id')


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'description', 'price',
                    'complete', 'destination_a', 'destination_b', 'distance',
                    'phone_number', 'charge_id', 'mover_profile', 'image_url',
                    'created_at', 'modified_at', 'confirmation_user',
                    'confirmation_mover')
