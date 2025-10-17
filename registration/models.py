from django.contrib.auth.models import Group, User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, default=1) 
    phone = models.CharField(max_length=30, blank=True, default='')
    mobile = models.CharField(max_length=30, blank=True, default='')
    token_app_session = models.CharField(max_length = 240,null=True, blank=True, default='')
    first_session = models.CharField(max_length = 240,null=True, blank=True, default='Si')

    class Meta:
        ordering = ['user__username']

    def __str__(self):
        return f"{self.user.username} - {self.user.first_name} {self.user.last_name}"