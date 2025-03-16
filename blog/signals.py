from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile  # Adjust the import according to your app's structure

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, **kwargs):
    if created:
        # Ensure that the profile is created when the user is created
        Profile.objects.create(user=instance)
    else:
        # If the profile already exists, update it if necessary
        try:
            instance.profile.save()
        except Profile.DoesNotExist:
            # In case the user has no profile yet, create one
            Profile.objects.create(user=instance)
