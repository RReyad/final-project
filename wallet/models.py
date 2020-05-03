from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    pass


class Wallet(models.Model):
    balance = models.FloatField(default=0)
    owner = models.OneToOneField("User", unique = True,on_delete=models.CASCADE, related_name="wallet")

class Transaction(models.Model):
    from_user =  models.ForeignKey("User", on_delete=models.CASCADE, related_name="debituser")
    to_user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="credituser")
    transaction_value = models.FloatField()
    transaction_timestamp =  models.DateTimeField(auto_now_add=True)
    transaction_description = models.TextField(max_length=250)
    transaction_category = models.TextField()
    transaction_type =  models.TextField()
    transaction_relevant_user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="referenceuser")

    def serialize(self):
        return {
            "id": self.id,
            "From": self.from_user.username,
            "To": self.to_user.username,
            "Value": self.transaction_value,
            "Description": self.transaction_description,
            "Timestamp": self.transaction_timestamp.strftime("%b %d %Y, %I:%M %p"),
            "Type": self.transaction_type,
            "Category": self.transaction_category,
            "Reference": self.transaction_relevant_user.username,
            
            }

