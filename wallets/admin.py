# wallet/admin.py
from django.contrib import admin
from .models import Wallet, WalletUser

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    """Admin configuration for Wallet model"""
    list_display = ('address', 'chain', 'balance_usd', 'synced_at')
    search_fields = ('address', 'chain')
    list_filter = ('chain', 'synced_at')
    readonly_fields = ('synced_at',)

@admin.register(WalletUser)
class WalletUserAdmin(admin.ModelAdmin):
    """Admin configuration for WalletUser model"""
    list_display = ('user', 'wallet_address', 'wallet_chain')
    search_fields = ('user__username', 'wallet__address')
    list_filter = ('wallet__chain',)
    
    # Using differently named properties without short_description attributes
    @admin.display(description='Wallet Address')
    def wallet_address(self, obj):
        return obj.wallet.address
    
    @admin.display(description='Chain')
    def wallet_chain(self, obj):
        return obj.wallet.chain
