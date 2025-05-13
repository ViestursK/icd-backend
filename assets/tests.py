# assets/models.py
from django.db import models
from wallets.models import Wallet
from django.utils import timezone
from django.conf import settings


class Token(models.Model):
    """Model for tracking crypto tokens/coins"""
    symbol = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    logo_url = models.URLField(null=True, blank=True)
    contract_address = models.CharField(max_length=255, null=True, blank=True)
    chain = models.CharField(max_length=50)
    coingecko_id = models.CharField(max_length=100, null=True, blank=True)
    
    # Current price data
    current_price_usd = models.DecimalField(max_digits=24, decimal_places=12, null=True, blank=True)
    price_updated_at = models.DateTimeField(auto_now=True)
    market_cap = models.DecimalField(max_digits=36, decimal_places=2, null=True, blank=True)
    
    # 24h change metrics
    price_change_24h = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    volume_24h = models.DecimalField(max_digits=36, decimal_places=2, null=True, blank=True)
    
    class Meta:
        unique_together = ('symbol', 'chain', 'contract_address')
    
    def __str__(self):
        return f"{self.symbol} ({self.chain})"

class WalletToken(models.Model):
    """Model for tracking token balances within wallets"""
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='tokens')
    token = models.ForeignKey(Token, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=36, decimal_places=18)
    balance_usd = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    last_synced = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('wallet', 'token')
    
    def __str__(self):
        return f"{self.wallet} - {self.token}: {self.balance}"

class TokenPrice(models.Model):
    """Model for tracking historical token prices"""
    token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name='price_history')
    price_usd = models.DecimalField(max_digits=24, decimal_places=12)
    timestamp = models.DateTimeField()
    
    class Meta:
        unique_together = ('token', 'timestamp')
        indexes = [
            models.Index(fields=['token', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.token} - ${self.price_usd} at {self.timestamp}"

class Portfolio(models.Model):
    """Model for tracking portfolio performance metrics"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='portfolio')
    total_value_usd = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    previous_day_value_usd = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    previous_week_value_usd = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    previous_month_value_usd = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    all_time_high_usd = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    all_time_high_date = models.DateField(null=True, blank=True)
    all_time_low_usd = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    all_time_low_date = models.DateField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Portfolio for {self.user.email}"

class PortfolioSnapshot(models.Model):
    """Model for tracking historical portfolio values"""
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='snapshots')
    total_value_usd = models.DecimalField(max_digits=18, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        indexes = [
            models.Index(fields=['portfolio', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.portfolio} - ${self.total_value_usd} at {self.timestamp}"

class TransactionType(models.TextChoices):
    RECEIVE = 'receive', 'Receive'
    SEND = 'send', 'Send'
    SWAP = 'swap', 'Swap'
    LIQUIDITY = 'liquidity', 'Liquidity'
    STAKE = 'stake', 'Stake'
    UNSTAKE = 'unstake', 'Unstake'
    EARN = 'earn', 'Earn Rewards'
    FEE = 'fee', 'Fee'
    UNKNOWN = 'unknown', 'Unknown'

class Transaction(models.Model):
    """Model for tracking blockchain transactions"""
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_hash = models.CharField(max_length=255)
    block_number = models.PositiveBigIntegerField()
    timestamp = models.DateTimeField()
    from_address = models.CharField(max_length=255)
    to_address = models.CharField(max_length=255)
    value = models.DecimalField(max_digits=36, decimal_places=18, default=0)
    gas_price = models.DecimalField(max_digits=36, decimal_places=18, default=0)
    gas_used = models.PositiveBigIntegerField(default=0)
    transaction_fee = models.DecimalField(max_digits=36, decimal_places=18, default=0)
    transaction_type = models.CharField(
        max_length=20, 
        choices=TransactionType.choices,
        default=TransactionType.UNKNOWN
    )
    status = models.BooleanField(default=True)  # True if successful
    
    class Meta:
        unique_together = ('wallet', 'transaction_hash')
        indexes = [
            models.Index(fields=['wallet', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.transaction_hash} ({self.transaction_type})"

class TokenTransfer(models.Model):
    """Model for tracking token transfers within transactions"""
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='token_transfers')
    token = models.ForeignKey(Token, on_delete=models.CASCADE)
    from_address = models.CharField(max_length=255)
    to_address = models.CharField(max_length=255)
    value = models.DecimalField(max_digits=36, decimal_places=18)
    value_usd = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"{self.token.symbol}: {self.value} from {self.from_address} to {self.to_address}"

class RiskMetrics(models.Model):
    """Model for tracking portfolio risk metrics"""
    portfolio = models.OneToOneField(Portfolio, on_delete=models.CASCADE, related_name='risk_metrics')
    volatility_30d = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)  # % 
    volatility_90d = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)  # %
    max_drawdown = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)  # %
    sharpe_ratio = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    value_at_risk = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)  # % 95% VaR
    concentration_risk = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)  # % in top asset
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Risk Metrics for {self.portfolio}"