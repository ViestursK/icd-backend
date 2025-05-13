# wallet/services.py
import requests
import logging
from decimal import Decimal
from django.conf import settings

logger = logging.getLogger(__name__)

class MoralisService:
    """Service for interacting with Moralis API"""
    
    # Define the mapping between user-friendly chain names and Moralis chain identifiers
    CHAIN_MAPPING = {
        'eth': 'eth',
        'bsc': 'bsc', 
        'polygon': 'polygon',
        'avalanche': 'avalanche',
        'fantom': 'fantom',
        'arbitrum': 'arbitrum',
        'optimism': 'optimism'
    }
    
    @classmethod
    def get_wallet_net_worth(cls, address, chain=None):
        """
        Fetch wallet net worth from Moralis API
        If chain is provided, will filter results for that specific chain
        Returns tuple: (success_bool, data_or_error_message)
        """
        try:
            # Prepare the API call
            api_url = f"https://deep-index.moralis.io/api/v2.2/wallets/{address}/net-worth"
            headers = {
                'accept': 'application/json',
                'X-API-Key': settings.MORALIS_API_KEY
            }
            
            # Add chain parameter if specified
            params = {}
            if chain:
                # Convert chain name to Moralis chain ID if needed
                moralis_chain = cls.CHAIN_MAPPING.get(chain.lower(), chain)
                params['chains'] = [moralis_chain]
                logger.info(f"Querying Moralis for wallet {address} on chain {moralis_chain}")
            else:
                logger.info(f"Querying Moralis for wallet {address} across all chains")
            
            # Make the API call
            response = requests.get(api_url, headers=headers, params=params)
            
            # Log the full response for debugging
            logger.debug(f"Moralis API response: {response.text}")
            
            # Handle response
            if response.status_code == 200:
                data = response.json()
                
                # If a specific chain was requested, filter the results
                if chain and 'chains' in data:
                    moralis_chain = cls.CHAIN_MAPPING.get(chain.lower(), chain)
                    # Find the chain data in the response
                    chain_data = None
                    for c in data['chains']:
                        if c.get('chain') == moralis_chain:
                            chain_data = c
                            break
                    
                    # If we couldn't find data for this chain, return an error
                    if not chain_data:
                        return False, f"No data found for chain: {chain} (Moralis chain ID: {moralis_chain})"
                
                return True, data
            else:
                error_msg = f"Moralis API error: {response.status_code}, {response.text}"
                logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Error fetching wallet net worth: {str(e)}"
            logger.exception(error_msg)
            return False, error_msg

    
    @classmethod
    def get_wallet_tokens(cls, address, chain):
        """
        Fetch token balances for a wallet from Moralis API
        Returns tuple: (success_bool, data_or_error_message)
        """
        try:
            # Prepare the API call
            api_url = f"https://deep-index.moralis.io/api/v2.2/{address}/erc20"
            headers = {
                'accept': 'application/json',
                'X-API-Key': settings.MORALIS_API_KEY
            }
            
            # Convert chain name to Moralis chain ID if needed
            moralis_chain = cls.CHAIN_MAPPING.get(chain.lower(), chain)
            params = {'chain': moralis_chain}
            
            # Make the API call
            response = requests.get(api_url, headers=headers, params=params)
            
            # Handle response
            if response.status_code == 200:
                return True, response.json()
            else:
                error_msg = f"Moralis API error: {response.status_code}, {response.text}"
                logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Error fetching token balances: {str(e)}"
            logger.exception(error_msg)
            return False, error_msg
    
    @classmethod
    def get_wallet_transactions(cls, address, chain, limit=100):
        """
        Fetch transaction history for a wallet from Moralis API
        Returns tuple: (success_bool, data_or_error_message)
        """
        try:
            # Prepare the API call
            api_url = f"https://deep-index.moralis.io/api/v2.2/{address}"
            headers = {
                'accept': 'application/json',
                'X-API-Key': settings.MORALIS_API_KEY
            }
            
            # Convert chain name to Moralis chain ID if needed
            moralis_chain = cls.CHAIN_MAPPING.get(chain.lower(), chain)
            params = {'chain': moralis_chain, 'limit': limit}
            
            # Make the API call
            response = requests.get(api_url, headers=headers, params=params)
            
            # Handle response
            if response.status_code == 200:
                return True, response.json()
            else:
                error_msg = f"Moralis API error: {response.status_code}, {response.text}"
                logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Error fetching transactions: {str(e)}"
            logger.exception(error_msg)
            return False, error_msg
    
    @classmethod
    def get_token_transfers(cls, address, chain, token_address=None, limit=100):
        """
        Fetch token transfers for a wallet from Moralis API
        Returns tuple: (success_bool, data_or_error_message)
        """
        try:
            # Prepare the API call
            api_url = f"https://deep-index.moralis.io/api/v2.2/{address}/erc20/transfers"
            headers = {
                'accept': 'application/json',
                'X-API-Key': settings.MORALIS_API_KEY
            }
            
            # Convert chain name to Moralis chain ID if needed
            moralis_chain = cls.CHAIN_MAPPING.get(chain.lower(), chain)
            params = {'chain': moralis_chain, 'limit': limit}
            
            if token_address:
                params['token_addresses'] = token_address
            
            # Make the API call
            response = requests.get(api_url, headers=headers, params=params)
            
            # Handle response
            if response.status_code == 200:
                return True, response.json()
            else:
                error_msg = f"Moralis API error: {response.status_code}, {response.text}"
                logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Error fetching token transfers: {str(e)}"
            logger.exception(error_msg)
            return False, error_msg
    
    @classmethod
    def get_defi_positions(cls, address, chain):
        """
        Fetch DeFi positions for a wallet from Moralis API (protocols, farming, staking, etc.)
        Returns tuple: (success_bool, data_or_error_message)
        """
        try:
            # The endpoint may vary depending on what's available in Moralis
            api_url = f"https://deep-index.moralis.io/api/v2.2/wallets/{address}/positions"
            headers = {
                'accept': 'application/json',
                'X-API-Key': settings.MORALIS_API_KEY
            }
            
            # Convert chain name to Moralis chain ID if needed
            moralis_chain = cls.CHAIN_MAPPING.get(chain.lower(), chain)
            params = {'chain': moralis_chain}
            
            # Make the API call
            response = requests.get(api_url, headers=headers, params=params)
            
            # Handle response
            if response.status_code == 200:
                return True, response.json()
            else:
                error_msg = f"Moralis API error: {response.status_code}, {response.text}"
                logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Error fetching DeFi positions: {str(e)}"
            logger.exception(error_msg)
            return False, error_msg