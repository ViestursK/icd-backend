# wallets/urls.py
from os import name
from django.urls import path
from .views import WalletView, get_supported_chains

class WalletSyncView(WalletView):
    """API endpoint specifically for wallet synchronization"""
    def get(self, request):
        """Override get method to call sync"""
        return self.sync(request)

class WalletDeleteView(WalletView):
    """API endpoint specifically for wallet deletion"""
    def post(self, request):
        """Override post method to call delete"""
        return self.delete(request)

urlpatterns = [
    # Endpoint for adding a new wallet (POST) and listing wallets (GET)
    path('add/', WalletView.as_view(), name='add-wallet'),
    
    # Endpoint for synchronizing wallets (GET)
    path('sync/', WalletSyncView.as_view(), name='sync-wallets'),
    
    # Endpoint for supported chains (GET)
    path('supported_chains/', get_supported_chains, name='supported-chains'),

    # Endpoint for deleting a wallet (PUT)
    path('remove/', WalletDeleteView.as_view(), name='remove-wallet'),
]
