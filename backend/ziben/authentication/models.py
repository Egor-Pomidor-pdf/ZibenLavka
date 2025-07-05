from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from ziben.settings import DEFAULT_MONEY

# Create your models here.


class CustomUser(AbstractUser):
    email = models.EmailField("email address", unique=True)
    money = models.CharField(default=str(DEFAULT_MONEY))
    time_money_last_earn = models.DateTimeField(auto_now_add=True)
    last_shop_update_date = models.DateTimeField(default=None, null=True)
    is_active = models.BooleanField(default=False)
    money_per_click = models.BigIntegerField(default=1)
    money_per_second = models.BigIntegerField(default=0)
    email_verification_token = models.CharField(null=True)
    email_verfication_token_date = models.DateTimeField(null=True, auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "password"]

    def get_current_money(self) -> int:
        now = timezone.now()
        seconds = int((now - self.time_money_last_earn).total_seconds())
        return int(self.money) + seconds * self.money_per_second

    def update_money(self):
        """Doesn't save it to the DB"""
        self.money = str(self.get_current_money())
        self.time_money_last_earn = timezone.now()
