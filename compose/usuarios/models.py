# usuarios/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserSecurityProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="security")
    must_change_password = models.BooleanField(default=False)

    def __str__(self):
        return f"Security profile for {self.user.username}"


@receiver(post_save, sender=User)
def create_user_security_profile(sender, instance, created, **kwargs):
    if created:
        UserSecurityProfile.objects.create(user=instance)