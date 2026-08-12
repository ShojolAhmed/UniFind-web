from django.db import models
from django.contrib.auth.models import User


class Item(models.Model):
    TYPE = [
        ('Lost', 'Lost'),
        ('Found', 'Found')
    ]

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posted_items'
    )

    claimed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='claimed_items'
    )

    title = models.CharField(max_length=100)

    item_type = models.CharField(
        max_length=20,
        choices=TYPE
    )

    description = models.TextField()

    location = models.CharField(
        max_length=100
    )

    image = models.ImageField(
        upload_to='items/'
    )

    contact = models.CharField(
        max_length=30
    )

    claimed = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.title


class Claim(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='claims'
    )

    claimant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='claims'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.claimant.username} - {self.item.title}"


class Notification(models.Model):

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    claim = models.ForeignKey(
        Claim,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )

    message = models.CharField(
        max_length=255
    )

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.recipient.username}: {self.message}"