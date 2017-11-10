from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    # show_explicit = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('profile', args='self.user.username')

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        p = Profile.objects.create(user=instance)
        p.save()
