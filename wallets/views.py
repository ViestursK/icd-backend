# wallet/views.py
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import AddWalletSerializer, WalletSerializer
from .services import MoralisService
from .models import Wallet, WalletUser
import logging

logger = logging.getLogger(__name__)

class WalletView(APIView):
    """API endpoint for wallet operations"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Add a new wallet for the authenticated user"""
        # Step 1: Validate request data
        serializer = AddWalletSerializer(
            data=request.data, 
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Step 2: Extract validated data with robust None handling
        # Define field names as variables to avoid string literal type errors
        address_field = 'address'
        chain_field = 'chain'
        chains_field = 'chains'
        balance_field = 'balance_usd'
        
        # First check if validated_data exists and is a dictionary
        if not serializer.validated_data or not isinstance(serializer.validated_data, dict):
            return Response(
                {'error': 'Validation failed - no data available'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Now extract values safely with explicit dictionary get method
        address = serializer.validated_data.get(address_field)
        chain = serializer.validated_data.get(chain_field)
        
        # Verify required data was extracted
        if not address or not chain:
            return Response(
                {'error': 'Missing required fields: address and chain must be provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Step 3: Fetch wallet data from Moralis
        success, result = MoralisService.get_wallet_net_worth(address, chain)
        
        if not success or not result or not isinstance(result, dict):
            return Response(
                {'error': result if result else 'Failed to retrieve wallet data'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Step 4: Process the wallet data
        try:
            # Safely extract chains, handling possible None or non-dict result
            chains = result.get(chains_field, [])
            if not isinstance(chains, list):
                chains = []  # Ensure chains is a list even if API returns unexpected type
            
            # Find the chain data using a loop instead of comprehension
            chain_data = None
            for c in chains:
                if isinstance(c, dict) and c.get(chain_field) == chain:
                    chain_data = c
                    break
            
            if not chain_data:
                return Response(
                    {'error': f"No data found for chain: {chain}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Safely extract balance with fallbacks
            balance_value = chain_data.get(balance_field, 0)
            if not balance_value and 'networth_usd' in chain_data:
                balance_value = chain_data.get('networth_usd', 0)
            
            # Create separate defaults dictionary to avoid type errors
            defaults_dict = {balance_field: balance_value}
            
            # Create or update the wallet
            wallet, created = Wallet.objects.update_or_create(
                address=address,
                chain=chain,
                defaults=defaults_dict
            )
            
            # Link the wallet to the user
            WalletUser.objects.get_or_create(
                user=request.user,
                wallet=wallet
            )
            
            # Return the wallet data
            return Response(
                WalletSerializer(wallet).data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.exception(f"Error processing wallet: {str(e)}")
            return Response(
                {'error': f"Failed to process wallet: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def get(self, request):
        """Get all wallets for the authenticated user"""
        # Get all wallet IDs for this user
        wallet_ids = WalletUser.objects.filter(user=request.user).values_list('wallet_id', flat=True)
        
        # Get the wallet objects
        wallets = Wallet.objects.filter(id__in=wallet_ids)
        
        # Serialize and return
        serializer = WalletSerializer(wallets, many=True)
        return Response(serializer.data)

    def sync(self, request):
        """Synchronize all wallets for the authenticated user"""
        try:
            # Get all wallets for this user
            wallet_ids = WalletUser.objects.filter(user=request.user).values_list('wallet_id', flat=True)
            wallets = Wallet.objects.filter(id__in=wallet_ids)
            
            # Track successfully synced wallets
            synced_wallets = []
            
            # Process each wallet
            for wallet in wallets:
                # Call Moralis to get updated data
                success, result = MoralisService.get_wallet_net_worth(wallet.address, wallet.chain)
                
                if not success or not isinstance(result, dict):
                    logger.warning(f"Failed to sync wallet {wallet.address} ({wallet.chain}): {result}")
                    continue
                    
                # Process the result similar to your post method
                try:
                    chains = result.get('chains', [])
                    
                    # Find the relevant chain data
                    chain_data = next((c for c in chains if isinstance(c, dict) and c.get('chain') == wallet.chain), None)
                    
                    if not chain_data:
                        logger.warning(f"No data found for wallet {wallet.address} on chain {wallet.chain}")
                        continue
                    
                    # Update the wallet balance
                    balance_value = chain_data.get('balance_usd', 0)
                    if not balance_value and 'networth_usd' in chain_data:
                        balance_value = chain_data.get('networth_usd', 0)
                    
                    # Update the wallet
                    wallet.balance_usd = balance_value
                    wallet.save()
                    
                    # Add to synced wallets list
                    synced_wallets.append({
                        'address': wallet.address,
                        'chain': wallet.chain,
                        'balance_usd': wallet.balance_usd
                    })
                    
                except Exception as e:
                    logger.exception(f"Error processing wallet update: {str(e)}")
                    continue
            
            # Return the updated wallets
            return Response({
                'wallets': synced_wallets,
                'count': len(synced_wallets)
            })
            
        except Exception as e:
            logger.exception(f"Error during wallet synchronization: {str(e)}")
            return Response(
                {'error': f"Failed to synchronize wallets: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request):
        """Remove a wallet for the authenticated user"""
        try:
            # Extract the address and chain from the request
            address = request.data.get('address')
            chain = request.data.get('chain')
            
            # Validate the input
            if not address or not chain:
                return Response(
                    {'error': 'Missing required fields: address and chain must be provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Find and delete the wallet-user relationship directly
            deleted_count, _ = WalletUser.objects.filter(
                user=request.user,
                wallet__address=address,
                wallet__chain=chain
            ).delete()
            
            # Check if any records were deleted
            if deleted_count == 0:
                return Response(
                    {'error': f"Wallet with address {address} on chain {chain} not found in your portfolio"},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            # Return success message
            return Response(
                {'message': f"Wallet {address} ({chain}) has been removed from your portfolio"},
                status=status.HTTP_200_OK
            )
                
        except Exception as e:
            logger.exception(f"Error removing wallet: {str(e)}")
            return Response(
                {'error': f"Failed to remove wallet: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['GET'])
def get_supported_chains(_request):
    """Return a list of supported blockchain networks"""
    return Response({
        'supported_chains': [
            {'id': chain_id, 'name': chain_name} 
            for chain_name, chain_id in MoralisService.CHAIN_MAPPING.items()
        ]
    })

