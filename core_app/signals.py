from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile
from django.db import transaction

User = get_user_model()

@receiver(post_save, sender=User)
def handle_user_profile(sender, instance, created, **kwargs):
    """
    Signal to handle user profile creation/update.
    Uses transaction.on_commit to ensure it runs after the main transaction completes.
    """
    if created:
        # Use get_or_create to prevent duplicates
        transaction.on_commit(
            lambda: UserProfile.objects.get_or_create(
                user=instance,
                defaults={'user_type': 'student'}  # Default to student
            )
        )