# assets/urls.py
from django.urls import path
from .views import (
    PortfolioView, TransactionHistoryView, SyncWalletDataView
)

urlpatterns = [
    # Portfolio overview
    path('portfolio/', PortfolioView.as_view(), name='portfolio-overview'),
    
    # Transaction history
    path('transactions/', TransactionHistoryView.as_view(), name='transaction-history'),
    
    # Sync wallet data (all data)
    path('sync/', SyncWalletDataView.as_view(), name='sync-wallet-data'),
]