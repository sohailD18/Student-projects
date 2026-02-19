from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Sum

class Transaction(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_transactions'
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_transactions'
    )
    amount = models.IntegerField(help_text='Amount of time credits transferred')
    task = models.ForeignKey(
        'tasks.Task',
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}: {self.amount} credits"

    def clean(self):
        """Validate that sender has sufficient credits"""
        if self.sender_id == self.receiver_id:
            raise ValidationError("Cannot send credits to yourself")

        sender_balance = self.sender.profile.time_credits_balance
        if sender_balance < self.amount:
            raise ValidationError(
                f"Insufficient credits. Available: {sender_balance}, Required: {self.amount}"
            )

    def save(self, *args, **kwargs):
        """Override save to update user credit balances"""
        self.full_clean()

        # Update balances
        sender_profile = self.sender.profile
        receiver_profile = self.receiver.profile

        sender_profile.time_credits_balance -= self.amount
        receiver_profile.time_credits_balance += self.amount

        sender_profile.save()
        receiver_profile.save()

        super().save(*args, **kwargs)
