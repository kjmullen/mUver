from django.contrib import admin
from muver_api.models import UserProfile, Job, Strike


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'in_progress', 'mover', 'banned',
                    'customer_id', 'stripe_account_id')


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'pickup_for', 'price',
                    'complete', 'conflict', 'destination_a', 'destination_b',
                    'distance', 'phone_number', 'charge_id', 'mover_profile',
                    'image_url', 'created_at', 'modified_at', 'status',
                    'confirmation_user', 'confirmation_mover')


@admin.register(Strike)
class StrikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'profile', 'job', 'comment', 'created_at')
