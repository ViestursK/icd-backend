from django.db import models
from django.conf import settings

class Wallet(models.Model):
    """
    Simple model to store wallet information and balance
    """
    address = models.CharField(max_length=255)
    chain = models.CharField(max_length=50)  
    balance_usd = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    synced_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # Ensure each wallet address is unique per chain
        unique_together = ('address', 'chain')
    
    def __str__(self):
        return f"{self.address} ({self.chain})"

class WalletUser(models.Model):
    """
    Simple association between users and wallets
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    
    class Meta:
        # Each user can have a wallet address only once
        unique_together = ('user', 'wallet')
