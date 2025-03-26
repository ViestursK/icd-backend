# wallet/serializers.py
from rest_framework import serializers
from .models import Wallet, WalletUser

class AddWalletSerializer(serializers.Serializer):
    """Serializer for adding a new wallet"""
    address = serializers.CharField(
        max_length=255, 
        min_length=26,  # Basic length validation
    )
    chain = serializers.CharField(max_length=50)
    
    def validate(self, attrs):
        """Validate that this wallet doesn't already exist for this user"""
        request = self.context.get('request')
        
        # Check if request exists in context
        if not request or not hasattr(request, 'user'):
            raise serializers.ValidationError("Authentication required")
            
        user = request.user
        
        # Check if wallet exists
        try:
            wallet = Wallet.objects.get(
                address=attrs['address'],
                chain=attrs['chain']
            )
            
            # Check if user already has this wallet
            if WalletUser.objects.filter(user=user, wallet=wallet).exists():
                raise serializers.ValidationError(
                    "You have already added this wallet address for this blockchain."
                )
        except Wallet.DoesNotExist:
            # This is fine - it means the wallet doesn't exist yet
            pass
            
        return attrs

class WalletSerializer(serializers.ModelSerializer):
    """Serializer for wallet data"""
    class Meta:
        model = Wallet
        fields = ['address', 'balance_usd', 'chain']
