# assets/views.py
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from wallets.models import Wallet, WalletUser
from .models import Token, WalletToken, Transaction, Portfolio, RiskMetrics
from .serializers import (
    TokenSerializer, WalletTokenSerializer, TransactionSerializer,
    PortfolioSerializer, RiskMetricsSerializer
)
from wallets.services import MoralisService
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PortfolioView(APIView):
    """API endpoint for portfolio overview"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get portfolio overview for the authenticated user"""
        try:
            # Get or create the portfolio for this user
            portfolio, created = Portfolio.objects.get_or_create(user=request.user)
            
            # Get all wallet IDs for this user
            wallet_ids = WalletUser.objects.filter(user=request.user).values_list('wallet_id', flat=True)
            
            # Get the wallet objects
            wallets = Wallet.objects.filter(id__in=wallet_ids)
            
            # Get token balances for all wallets
            wallet_tokens = WalletToken.objects.filter(wallet__in=wallets)
            
            # Calculate current portfolio value
            total_value = sum(wt.balance_usd or 0 for wt in wallet_tokens)
            portfolio.total_value_usd = total_value
            portfolio.save()
            
            # Calculate asset allocation
            token_values = {}
            for wt in wallet_tokens:
                if wt.token.symbol in token_values:
                    token_values[wt.token.symbol] += wt.balance_usd or 0
                else:
                    token_values[wt.token.symbol] = wt.balance_usd or 0
            
            # Convert to percentage
            asset_allocation = []
            for symbol, value in token_values.items():
                if total_value > 0:
                    percentage = (value / total_value) * 100
                else:
                    percentage = 0
                asset_allocation.append({
                    'symbol': symbol,
                    'value_usd': value,
                    'percentage': percentage
                })
            
            # Sort by value (highest first)
            asset_allocation.sort(key=lambda x: x['value_usd'], reverse=True)
            
            # Fetch risk metrics
            risk_metrics, _ = RiskMetrics.objects.get_or_create(portfolio=portfolio)
            
            # Fetch historical data for charts
            thirty_days_ago = datetime.now() - timedelta(days=30)
            historical_data = list(portfolio.snapshots.filter(
                timestamp__gte=thirty_days_ago
            ).order_by('timestamp').values('timestamp', 'total_value_usd'))
            
            # Calculate performance metrics
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            # Daily change
            daily_change_pct = 0
            if portfolio.previous_day_value_usd and portfolio.previous_day_value_usd > 0:
                daily_change_pct = ((total_value - portfolio.previous_day_value_usd) / portfolio.previous_day_value_usd) * 100
            
            # Weekly change
            weekly_change_pct = 0
            if portfolio.previous_week_value_usd and portfolio.previous_week_value_usd > 0:
                weekly_change_pct = ((total_value - portfolio.previous_week_value_usd) / portfolio.previous_week_value_usd) * 100
            
            # Monthly change
            monthly_change_pct = 0
            if portfolio.previous_month_value_usd and portfolio.previous_month_value_usd > 0:
                monthly_change_pct = ((total_value - portfolio.previous_month_value_usd) / portfolio.previous_month_value_usd) * 100
            
            # Return the portfolio overview
            return Response({
                'total_value_usd': total_value,
                'asset_allocation': asset_allocation,
                'performance': {
                    'daily_change_pct': daily_change_pct,
                    'weekly_change_pct': weekly_change_pct,
                    'monthly_change_pct': monthly_change_pct,
                },
                'risk_metrics': {
                    'volatility_30d': risk_metrics.volatility_30d,
                    'max_drawdown': risk_metrics.max_drawdown,
                    'sharpe_ratio': risk_metrics.sharpe_ratio,
                    'value_at_risk': risk_metrics.value_at_risk,
                    'concentration_risk': risk_metrics.concentration_risk,
                },
                'historical_data': historical_data
            })
            
        except Exception as e:
            logger.exception(f"Error fetching portfolio overview: {str(e)}")
            return Response(
                {'error': f"Failed to fetch portfolio overview: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TransactionHistoryView(APIView):
    """API endpoint for transaction history"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get transaction history for the authenticated user"""
        try:
            # Get wallet IDs for this user
            wallet_ids = WalletUser.objects.filter(user=request.user).values_list('wallet_id', flat=True)
            
            # Get transactions for these wallets
            transactions = Transaction.objects.filter(wallet_id__in=wallet_ids).order_by('-timestamp')
            
            # Pagination parameters
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 20))
            
            # Apply pagination
            start = (page - 1) * page_size
            end = start + page_size
            paginated_transactions = transactions[start:end]
            
            # Serialize and return
            serializer = TransactionSerializer(paginated_transactions, many=True)
            
            return Response({
                'transactions': serializer.data,
                'total': transactions.count(),
                'page': page,
                'page_size': page_size,
                'total_pages': (transactions.count() + page_size - 1) // page_size
            })
            
        except Exception as e:
            logger.exception(f"Error fetching transaction history: {str(e)}")
            return Response(
                {'error': f"Failed to fetch transaction history: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SyncWalletDataView(APIView):
    """API endpoint for syncing all wallet data"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Synchronize all wallet data for the authenticated user"""
        try:
            # Get all wallet IDs for this user
            wallet_ids = WalletUser.objects.filter(user=request.user).values_list('wallet_id', flat=True)
            wallets = Wallet.objects.filter(id__in=wallet_ids)
            
            # Track successfully synced wallets
            results = {
                'wallets_synced': 0,
                'tokens_synced': 0,
                'transactions_synced': 0,
                'failed_syncs': []
            }
            
            # Process each wallet
            for wallet in wallets:
                # Sync wallet balance (using existing method)
                try:
                    success, result = MoralisService.get_wallet_net_worth(wallet.address, wallet.chain)
                    if success and isinstance(result, dict):
                        chains = result.get('chains', [])
                        chain_data = next((c for c in chains if c.get('chain') == wallet.chain), None)
                        
                        if chain_data:
                            balance_value = chain_data.get('balance_usd', 0)
                            if not balance_value and 'networth_usd' in chain_data:
                                balance_value = chain_data.get('networth_usd', 0)
                            
                            wallet.balance_usd = balance_value
                            wallet.save()
                            results['wallets_synced'] += 1
                except Exception as e:
                    logger.exception(f"Error syncing wallet balance: {str(e)}")
                    results['failed_syncs'].append(f"Balance for {wallet.address}: {str(e)}")
                
                # Sync tokens
                try:
                    success, token_data = MoralisService.get_wallet_tokens(wallet.address, wallet.chain)
                    if success and isinstance(token_data, dict) and 'tokens' in token_data:
                        for token_info in token_data['tokens']:
                            # Create or update token
                            token, created = Token.objects.update_or_create(
                                symbol=token_info.get('symbol', 'UNKNOWN'),
                                chain=wallet.chain,
                                contract_address=token_info.get('token_address'),
                                defaults={
                                    'name': token_info.get('name', token_info.get('symbol', 'Unknown Token')),
                                    'logo_url': token_info.get('logo') or None,
                                    'current_price_usd': token_info.get('usd_price', None),
                                }
                            )
                            
                            # Create or update wallet token balance
                            decimals = int(token_info.get('decimals', 18))
                            balance_raw = int(token_info.get('balance', 0))
                            balance = balance_raw / (10 ** decimals)
                            balance_usd = balance * (float(token_info.get('usd_price', 0)) or 0)
                            
                            WalletToken.objects.update_or_create(
                                wallet=wallet,
                                token=token,
                                defaults={
                                    'balance': balance,
                                    'balance_usd': balance_usd
                                }
                            )
                            
                            results['tokens_synced'] += 1
                except Exception as e:
                    logger.exception(f"Error syncing tokens: {str(e)}")
                    results['failed_syncs'].append(f"Tokens for {wallet.address}: {str(e)}")
                
                # Sync transactions (limited to recent ones)
                try:
                    success, tx_data = MoralisService.get_wallet_transactions(wallet.address, wallet.chain, limit=100)
                    if success and isinstance(tx_data, dict) and 'result' in tx_data:
                        for tx_info in tx_data['result']:
                            try:
                                # Determine transaction type
                                tx_type = 'unknown'
                                if tx_info.get('from_address') == wallet.address.lower():
                                    tx_type = 'send'
                                elif tx_info.get('to_address') == wallet.address.lower():
                                    tx_type = 'receive'
                                
                                # Create or update transaction
                                timestamp = datetime.fromtimestamp(int(tx_info.get('block_timestamp', 0)))
                                Transaction.objects.update_or_create(
                                    wallet=wallet,
                                    transaction_hash=tx_info.get('hash'),
                                    defaults={
                                        'block_number': int(tx_info.get('block_number', 0)),
                                        'timestamp': timestamp,
                                        'from_address': tx_info.get('from_address', ''),
                                        'to_address': tx_info.get('to_address', ''),
                                        'value': int(tx_info.get('value', 0)) / (10**18),  # Convert from wei to ether
                                        'gas_price': int(tx_info.get('gas_price', 0)),
                                        'gas_used': int(tx_info.get('receipt_gas_used', 0)),
                                        'transaction_fee': int(tx_info.get('receipt_gas_used', 0)) * int(tx_info.get('gas_price', 0)) / (10**18),
                                        'transaction_type': tx_type,
                                        'status': tx_info.get('receipt_status') == '1'
                                    }
                                )
                                results['transactions_synced'] += 1
                            except Exception as e:
                                logger.exception(f"Error processing transaction {tx_info.get('hash')}: {str(e)}")
                                continue
                except Exception as e:
                    logger.exception(f"Error syncing transactions: {str(e)}")
                    results['failed_syncs'].append(f"Transactions for {wallet.address}: {str(e)}")
            
            # Update portfolio data
            try:
                portfolio, created = Portfolio.objects.get_or_create(user=request.user)
                
                # Calculate current portfolio value
                wallet_tokens = WalletToken.objects.filter(wallet__in=wallets)
                total_value = sum(wt.balance_usd or 0 for wt in wallet_tokens)
                
                # Update portfolio with the new value
                today = datetime.now().date()
                if not created:
                    # Set previous values if this isn't a new portfolio
                    if not portfolio.previous_day_value_usd:
                        portfolio.previous_day_value_usd = total_value
                    if not portfolio.previous_week_value_usd:
                        portfolio.previous_week_value_usd = total_value
                    if not portfolio.previous_month_value_usd:
                        portfolio.previous_month_value_usd = total_value
                    
                    # Update ATH/ATL if needed
                    if portfolio.all_time_high_usd is None or total_value > portfolio.all_time_high_usd:
                        portfolio.all_time_high_usd = total_value
                        portfolio.all_time_high_date = today
                    
                    if portfolio.all_time_low_usd is None or total_value < portfolio.all_time_low_usd:
                        portfolio.all_time_low_usd = total_value
                        portfolio.all_time_low_date = today
                else:
                    # Initialize all values for a new portfolio
                    portfolio.previous_day_value_usd = total_value
                    portfolio.previous_week_value_usd = total_value
                    portfolio.previous_month_value_usd = total_value
                    portfolio.all_time_high_usd = total_value
                    portfolio.all_time_high_date = today
                    portfolio.all_time_low_usd = total_value
                    portfolio.all_time_low_date = today
                
                portfolio.total_value_usd = total_value
                portfolio.save()
                
                # Create portfolio snapshot
                PortfolioSnapshot.objects.create(
                    portfolio=portfolio,
                    total_value_usd=total_value
                )
                
                # Update risk metrics (calculate on sync)
                risk_metrics, _ = RiskMetrics.objects.get_or_create(portfolio=portfolio)
                
                # Calculate concentration risk (% in top asset)
                wallet_tokens = WalletToken.objects.filter(wallet__in=wallets)
                if wallet_tokens.exists() and total_value > 0:
                    # Group by token and sum balance_usd
                    token_values = {}
                    for wt in wallet_tokens:
                        token_symbol = wt.token.symbol
                        if token_symbol in token_values:
                            token_values[token_symbol] += wt.balance_usd or 0
                        else:
                            token_values[token_symbol] = wt.balance_usd or 0
                    
                    # Find the largest token position
                    largest_position = max(token_values.values())
                    concentration_risk = (largest_position / total_value) * 100
                    risk_metrics.concentration_risk = concentration_risk
                
                # Save risk metrics
                risk_metrics.save()
                
            except Exception as e:
                logger.exception(f"Error updating portfolio data: {str(e)}")
                results['failed_syncs'].append(f"Portfolio update: {str(e)}")
            
            return Response(results)
            
        except Exception as e:
            logger.exception(f"Error in sync operation: {str(e)}")
            return Response(
                {'error': f"Failed to sync wallet data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )