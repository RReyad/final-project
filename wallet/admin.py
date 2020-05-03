from django.contrib import admin
from .models import User, Wallet, Transaction

admin.site.register(User)
admin.site.register(Wallet)
admin.site.register(Transaction)
# Register your models here.
