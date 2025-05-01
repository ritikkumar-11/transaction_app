from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta

class Friend(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    nickname = models.CharField(max_length=50)

    def __str__(self):
        return self.nickname


class Transction(models.Model):
    payer = models.ForeignKey(Friend, on_delete=models.CASCADE, related_name='paid_transction')
    receiver = models.ForeignKey(Friend, on_delete=models.CASCADE, related_name='recieved_transction')
    amount  = models.IntegerField()
    date = models.DateField(auto_now_add=True)
    repay_within_days = models.IntegerField()

    def repayment_date(self):
        return self.date + timedelta(days=self.repay_within_days)

