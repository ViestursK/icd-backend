# assets/serializers.py
from rest_framework import serializers
from .models import (
    Token, WalletToken, Transaction, TokenTransfer,
    Portfolio, PortfolioSnapshot, RiskMetrics
)

class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = [
            'id', 'symbol', 'name', 'logo_url', 'contract_address', 'chain',
            'current_price_usd', 'price_change_24h', 'market_cap', 'volume_24h'
        ]

class WalletTokenSerializer(serializers.ModelSerializer):
    token = TokenSerializer(read_only=True)
    
    class Meta:
        model = WalletToken
        fields = ['id', 'wallet', 'token', 'balance', 'balance_usd', 'last_synced']

class TokenTransferSerializer(serializers.ModelSerializer):
    token = TokenSerializer(read_only=True)
    
    class Meta:
        model = TokenTransfer
        fields = ['id', 'token', 'from_address', 'to_address', 'value', 'value_usd']

class TransactionSerializer(serializers.ModelSerializer):
    token_transfers = TokenTransferSerializer(many=True, read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'wallet', 'transaction_hash', 'block_number', 'timestamp',
            'from_address', 'to_address', 'value', 'gas_price', 'gas_used',
            'transaction_fee', 'transaction_type', 'status', 'token_transfers'
        ]

class PortfolioSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioSnapshot
        fields = ['id', 'total_value_usd', 'timestamp']

class RiskMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskMetrics
        fields = [
            'id', 'volatility_30d', 'volatility_90d', 'max_drawdown',
            'sharpe_ratio', 'value_at_risk', 'concentration_risk', 'last_updated'
        ]

class PortfolioSerializer(serializers.ModelSerializer):
    snapshots = PortfolioSnapshotSerializer(many=True, read_only=True)
    risk_metrics = RiskMetricsSerializer(read_only=True)
    
    class Meta:
        model = Portfolio
        fields = [
            'id', 'total_value_usd', 'previous_day_value_usd',
            'previous_week_value_usd', 'previous_month_value_usd',
            'all_time_high_usd', 'all_time_high_date',
            'all_time_low_usd', 'all_time_low_date',
            'last_updated', 'snapshots', 'risk_metrics'
        ]