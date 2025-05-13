# assets/services.py
import numpy as np
from decimal import Decimal
from datetime import datetime, timedelta
from .models import Portfolio, PortfolioSnapshot, RiskMetrics

class RiskAnalysisService:
    """Service for calculating portfolio risk metrics"""
    
    @classmethod
    def calculate_portfolio_risk_metrics(cls, portfolio_id):
        """Calculate and update risk metrics for a portfolio"""
        try:
            # Get the portfolio
            portfolio = Portfolio.objects.get(id=portfolio_id)
            
            # Get risk metrics object
            risk_metrics, created = RiskMetrics.objects.get_or_create(portfolio=portfolio)
            
            # Get historical data for the last 90 days
            ninety_days_ago = datetime.now() - timedelta(days=90)
            snapshots = PortfolioSnapshot.objects.filter(
                portfolio=portfolio,
                timestamp__gte=ninety_days_ago
            ).order_by('timestamp')
            
            # Need enough data for meaningful calculations
            if snapshots.count() < 7:  # Need at least a week of data
                return False, "Not enough historical data for risk calculations"
            
            # Extract values and calculate daily returns
            values = [float(snapshot.total_value_usd) for snapshot in snapshots]
            returns = []
            
            for i in range(1, len(values)):
                if values[i-1] > 0:  # Avoid division by zero
                    daily_return = (values[i] - values[i-1]) / values[i-1]
                    returns.append(daily_return)
            
            if len(returns) < 5:
                return False, "Not enough return data for risk calculations"
            
            # Convert to numpy array for calculations
            returns_array = np.array(returns)
            
            # Calculate volatility (standard deviation of returns)
            volatility_30d = np.std(returns_array[-30:] if len(returns_array) >= 30 else returns_array) * 100
            volatility_90d = np.std(returns_array) * 100
            
            # Calculate max drawdown
            rolling_max = np.maximum.accumulate(values)
            drawdowns = (rolling_max - values) / rolling_max
            max_drawdown = 100 * np.max(drawdowns)
            
            # Calculate Sharpe ratio (assuming risk-free rate of 2%)
            risk_free_rate = 0.02 / 365  # Daily risk-free rate
            mean_return = np.mean(returns_array)
            if np.std(returns_array) > 0:
                sharpe_ratio = (mean_return - risk_free_rate) / np.std(returns_array) * np.sqrt(365)
            else:
                sharpe_ratio = 0
            
            # Calculate 95% Value at Risk (VaR)
            var_95 = abs(np.percentile(returns_array, 5) * 100)
            
            # Update risk metrics
            risk_metrics.volatility_30d = Decimal(str(volatility_30d))
            risk_metrics.volatility_90d = Decimal(str(volatility_90d))
            risk_metrics.max_drawdown = Decimal(str(max_drawdown))
            risk_metrics.sharpe_ratio = Decimal(str(sharpe_ratio))
            risk_metrics.value_at_risk = Decimal(str(var_95))
            risk_metrics.save()
            
            return True, "Risk metrics updated successfully"
            
        except Portfolio.DoesNotExist:
            return False, "Portfolio not found"
        except Exception as e:
            return False, f"Error calculating risk metrics: {str(e)}"