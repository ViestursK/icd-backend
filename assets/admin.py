# assets/admin.py
from django.contrib import admin
from .models import (
    Token, WalletToken, Transaction, TokenTransfer, 
    Portfolio, PortfolioSnapshot, RiskMetrics
)

@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'chain', 'current_price_usd', 'price_updated_at')
    search_fields = ('symbol', 'name', 'contract_address')
    list_filter = ('chain',)

@admin.register(WalletToken)
class WalletTokenAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'token', 'balance', 'balance_usd', 'last_synced')
    search_fields = ('wallet__address', 'token__symbol')
    list_filter = ('token__chain', 'last_synced')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_hash', 'wallet', 'transaction_type', 'timestamp', 'status')
    search_fields = ('transaction_hash', 'wallet__address', 'from_address', 'to_address')
    list_filter = ('transaction_type', 'status', 'timestamp')

@admin.register(TokenTransfer)
class TokenTransferAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'token', 'value', 'value_usd')
    search_fields = ('transaction__transaction_hash', 'token__symbol')

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_value_usd', 'last_updated')
    search_fields = ('user__email',)

@admin.register(PortfolioSnapshot)
class PortfolioSnapshotAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'total_value_usd', 'timestamp')
    search_fields = ('portfolio__user__email',)
    list_filter = ('timestamp',)

@admin.register(RiskMetrics)
class RiskMetricsAdmin(admin.ModelAdmin):
    list_display = (
        'portfolio', 'volatility_30d', 'max_drawdown', 
        'sharpe_ratio', 'concentration_risk', 'last_updated'
    )
    search_fields = ('portfolio__user__email',)