from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    USER_TYPES = (
        ('student', 'Student'),
        ('educator', 'Educator'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='student')

    def __str__(self):
        return f"{self.user.username} ({self.user_type})"

# Automatically create UserProfile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

# Automatically save UserProfile when User is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
