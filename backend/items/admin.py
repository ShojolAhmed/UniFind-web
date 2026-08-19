from django.contrib import admin

from .models import Item, Claim, Notification


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'item_type',
        'location',
        'owner',
        'claimed',
        'claimed_by',
        'created_at',
    )
    list_filter = ('item_type', 'claimed', 'created_at')
    search_fields = ('title', 'description', 'location', 'owner__username')
    raw_id_fields = ('owner', 'claimed_by')
    date_hierarchy = 'created_at'


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'item',
        'claimant',
        'status',
        'created_at',
        'reviewed_at',
    )
    list_filter = ('status', 'created_at')
    search_fields = ('item__title', 'claimant__username')
    raw_id_fields = ('item', 'claimant')
    date_hierarchy = 'created_at'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'recipient',
        'message',
        'is_read',
        'created_at',
    )
    list_filter = ('is_read', 'created_at')
    search_fields = ('recipient__username', 'message')
    raw_id_fields = ('recipient', 'claim')
    date_hierarchy = 'created_at'
