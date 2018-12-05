from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone


class ProfileManager(models.Manager):
    def get_queryset(self):
        return super(ProfileManager, self).get_queryset().select_related("user")

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    LIGHT = "light"
    DARK = "dark"
    THEME_CHOICES = (
        (LIGHT, "Light"),
        (DARK, "Dark"),
    )
    theme = models.CharField(choices=THEME_CHOICES, default=LIGHT, max_length=10)

    objects = ProfileManager()

    def __str__(self):
        return self.user.email

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        p = Profile.objects.create(user=instance)
        p.save()
