"""
Advanced Mean Reversion Strategy with LangChain Custom Tools
"""
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from langchain_core.tools import tool, BaseTool
from ETHDenver2025.Mean_Reversion.core.api import TokenPriceAPI
from ETHDenver2025.Mean_Reversion.core.indicators import MeanReversionIndicators as MeanReversionCalculator

class MeanReversionStrategy:
    """Implements an advanced mean reversion trading strategy."""
    
    def __init__(self, lookback_period: int = 10, z_threshold: float = 2.0, 
                 rsi_overbought: int = 70, rsi_oversold: int = 30):
        """
        Initialize the mean reversion strategy.
        
        Args:
            lookback_period: Number of days to look back for calculations (default: 10)
            z_threshold: Z-score threshold for mean reversion signals
            rsi_overbought: RSI threshold for overbought condition
            rsi_oversold: RSI threshold for oversold condition
        """
        self.lookback_period = lookback_period
        self.z_threshold = z_threshold
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
        self.api = TokenPriceAPI()
        self.calculator = MeanReversionCalculator()
    
    def calculate_metrics(self, token_id: str, days: int = 10) -> Dict[str, Any]:
        """
        Calculate all metrics needed for the strategy.
        
        Args:
            token_id: The token to analyze
            days: Number of days of historical data to retrieve (default: 10)
            
        Returns:
            Dictionary of calculated metrics
        """
        # Get historical price data
        historical_data = self.api.get_historical_prices(token_id, days=days)
        timestamps = [price[0] for price in historical_data]
        prices = [price[1] for price in historical_data]
        dates = [datetime.fromtimestamp(ts/1000).strftime('%Y-%m-%d') for ts in timestamps]
        
        # Create DataFrame
        df = pd.DataFrame({
            'date': dates,
            'timestamp': timestamps,
            'price': prices
        })
        
        # Calculate moving average
        df['ma'] = df['price'].rolling(window=self.lookback_period).mean()
        
        # Calculate standard deviation
        df['std'] = df['price'].rolling(window=self.lookback_period).std()
        
        # Calculate Z-score
        df['z_score'] = (df['price'] - df['ma']) / df['std']
        
        # Calculate RSI
        delta = df['price'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=10).mean()
        avg_loss = loss.rolling(window=10).mean()
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Calculate Bollinger Bands
        df['upper_band'] = df['ma'] + (df['std'] * 2)
        df['lower_band'] = df['ma'] - (df['std'] * 2)
        df['percent_b'] = (df['price'] - df['lower_band']) / (df['upper_band'] - df['lower_band'])
        
        # Generate trading signals
        df['buy_signal'] = ((df['z_score'] < -self.z_threshold) | 
                           (df['rsi'] < self.rsi_oversold) | 
                           (df['percent_b'] < 0))
        
        df['sell_signal'] = ((df['z_score'] > self.z_threshold) | 
                            (df['rsi'] > self.rsi_overbought) | 
                            (df['percent_b'] > 1))
        
        return {
            'dataframe': df,
            'current_price': prices[-1], 
            'current_z_score': df['z_score'].iloc[-1],
            'current_rsi': df['rsi'].iloc[-1],
            'current_percent_b': df['percent_b'].iloc[-1],
            'buy_signal': df['buy_signal'].iloc[-1],
            'sell_signal': df['sell_signal'].iloc[-1]
        }
    
    def backtest_strategy(self, token_id: str, days: int = 10, 
                         initial_capital: float = 10000.0) -> Dict[str, Any]:
        """
        Backtest the mean reversion strategy.
        
        Args:
            token_id: Token to backtest
            days: Number of days to backtest (default: 10)
            initial_capital: Starting capital for the backtest
            
        Returns:
            Dictionary with backtest results
        """
        # Get metrics
        metrics = self.calculate_metrics(token_id, days=days)
        df = metrics['dataframe']
        
        # Initialize backtest variables
        df['position'] = 0  # 0: no position, 1: long
        df['capital'] = initial_capital
        df['holdings'] = 0.0
        df['portfolio_value'] = initial_capital
        
        # Run backtest simulation
        position = 0
        for i in range(self.lookback_period, len(df)):
            # Check for buy signal
            if position == 0 and df['buy_signal'].iloc[i]:
                # Buy with all capital
                position = 1
                df.loc[df.index[i], 'position'] = 1
                df.loc[df.index[i], 'holdings'] = df['capital'].iloc[i-1] / df['price'].iloc[i]
                df.loc[df.index[i], 'capital'] = 0
            
            # Check for sell signal
            elif position == 1 and df['sell_signal'].iloc[i]:
                # Sell all holdings
                position = 0
                df.loc[df.index[i], 'position'] = 0
                df.loc[df.index[i], 'capital'] = df['holdings'].iloc[i-1] * df['price'].iloc[i]
                df.loc[df.index[i], 'holdings'] = 0
            
            # Carry forward
            else:
                df.loc[df.index[i], 'position'] = df['position'].iloc[i-1]
                df.loc[df.index[i], 'capital'] = df['capital'].iloc[i-1]
                df.loc[df.index[i], 'holdings'] = df['holdings'].iloc[i-1]
            
            # Calculate portfolio value
            df.loc[df.index[i], 'portfolio_value'] = (
                df['capital'].iloc[i] + df['holdings'].iloc[i] * df['price'].iloc[i]
            )
        
        # Calculate backtest metrics
        starting_value = df['portfolio_value'].iloc[self.lookback_period]
        ending_value = df['portfolio_value'].iloc[-1]
        total_return = (ending_value / starting_value - 1) * 100
        
        # Calculate buy-and-hold return for comparison
        buy_hold_return = (df['price'].iloc[-1] / df['price'].iloc[self.lookback_period] - 1) * 100
        
        # Calculate trade statistics
        position_changes = df['position'].diff().abs()
        num_trades = position_changes[position_changes > 0].count()
        
        return {
            'dataframe': df,
            'total_return': total_return,
            'buy_hold_return': buy_hold_return,
            'num_trades': num_trades,
            'initial_capital': initial_capital,
            'ending_capital': ending_value,
            'token_id': token_id
        }

    def plot_backtest_results(self, backtest_results: Dict[str, Any], 
                             save_path: Optional[str] = None) -> None:
        """
        Plot the backtest results.
        
        Args:
            backtest_results: Dictionary with backtest results
            save_path: Path to save the plot image (optional)
        """
        df = backtest_results['dataframe']
        token_id = backtest_results['token_id']
        
        # Create figure with subplots
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(12, 16), sharex=True)
        
        # Plot price and moving average
        ax1.plot(df['date'], df['price'], label='Price')
        ax1.plot(df['date'], df['ma'], label='Moving Average')
        ax1.plot(df['date'], df['upper_band'], 'r--', label='Upper Band')
        ax1.plot(df['date'], df['lower_band'], 'g--', label='Lower Band')
        ax1.set_title(f'{token_id.upper()} Price with Bollinger Bands')
        ax1.set_ylabel('Price (USD)')
        ax1.legend()
        ax1.grid(True)
        
        # Plot Z-score
        ax2.plot(df['date'], df['z_score'])
        ax2.axhline(y=self.z_threshold, color='r', linestyle='--', label=f'Z-threshold: {self.z_threshold}')
        ax2.axhline(y=-self.z_threshold, color='g', linestyle='--', label=f'Z-threshold: -{self.z_threshold}')
        ax2.set_title('Z-Score')
        ax2.set_ylabel('Z-Score')
        ax2.legend()
        ax2.grid(True)
        
        # Plot RSI
        ax3.plot(df['date'], df['rsi'])
        ax3.axhline(y=self.rsi_overbought, color='r', linestyle='--', label=f'Overbought: {self.rsi_overbought}')
        ax3.axhline(y=self.rsi_oversold, color='g', linestyle='--', label=f'Oversold: {self.rsi_oversold}')
        ax3.set_title('RSI')
        ax3.set_ylabel('RSI')
        ax3.set_ylim(0, 100)
        ax3.legend()
        ax3.grid(True)
        
        # Plot portfolio value
        ax4.plot(df['date'], df['portfolio_value'], label='Strategy')
        
        # Calculate buy-and-hold performance for comparison
        initial_price = df['price'].iloc[self.lookback_period]
        initial_shares = backtest_results['initial_capital'] / initial_price
        df['buy_hold_value'] = initial_shares * df['price']
        
        ax4.plot(df['date'], df['buy_hold_value'], label='Buy & Hold')
        ax4.set_title('Portfolio Performance')
        ax4.set_ylabel('Portfolio Value (USD)')
        ax4.set_xlabel('Date')
        ax4.legend()
        ax4.grid(True)
        
        # Highlight buy and sell points
        buy_signals = df[df['position'].diff() > 0]
        sell_signals = df[df['position'].diff() < 0]
        
        ax1.scatter(buy_signals['date'], buy_signals['price'], 
                  marker='^', color='g', s=100, label='Buy')
        ax1.scatter(sell_signals['date'], sell_signals['price'], 
                  marker='v', color='r', s=100, label='Sell')
        
        # Format x-axis
        for ax in [ax1, ax2, ax3, ax4]:
            ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            print(f"Plot saved to {save_path}")
        else:
            plt.show()


# LangChain Tools

@tool
def get_token_mean_reversion_signal(token_id: str) -> str:
    """
    Generate a trading signal based on mean reversion strategy.
    
    Args:
        token_id: The ID of the token (e.g., 'bitcoin', 'ethereum', 'solana')
    
    Returns:
        A trading signal (BUY, SELL, or HOLD) with explanation.
    """
    try:
        # Initialize strategy with 10-day lookback
        strategy = MeanReversionStrategy(lookback_period=10)
        
        # Calculate metrics
        metrics = strategy.calculate_metrics(token_id, days=10)
        
        # Get current signals
        buy_signal = metrics['buy_signal']
        sell_signal = metrics['sell_signal']
        
        # Format the message
        current_price = metrics['current_price']
        z_score = metrics['current_z_score']
        rsi = metrics['current_rsi']
        percent_b = metrics['current_percent_b']
        
        if buy_signal:
            signal = "BUY"
            explanation = "Mean reversion indicators suggest the token is undervalued."
        elif sell_signal:
            signal = "SELL"
            explanation = "Mean reversion indicators suggest the token is overvalued."
        else:
            signal = "HOLD"
            explanation = "Mean reversion indicators are neutral."
        
        message = f"""
=== MEAN REVERSION TRADING SIGNAL FOR {token_id.upper()} ===
Based on the last 10 days of price data

SIGNAL: {signal}
{explanation}

Current Price: ${current_price:.2f}

INDICATORS:
- Z-Score: {z_score:.2f} (Threshold: ±2.0)
- RSI: {rsi:.2f} (Thresholds: 30/70)
- Bollinger %B: {percent_b:.2f} (Thresholds: 0/1)

INTERPRETATION:
- Z-Score < -2.0 or RSI < 30 or %B < 0: BUY (undervalued)
- Z-Score > 2.0 or RSI > 70 or %B > 1: SELL (overvalued)
- Otherwise: HOLD (neutral)

Note: This signal is based on mean reversion principles using 10-day historical data.
"""
        return message
    except Exception as e:
        return f"Error generating signal for {token_id}: {str(e)}"

@tool(response_format="content_and_artifact")
def backtest_mean_reversion_strategy(token_id: str, days: int = 10, 
                                   initial_capital: float = 10000.0) -> Tuple[str, Dict[str, Any]]:
    """
    Backtest a mean reversion trading strategy for a token.
    
    Args:
        token_id: The ID of the token (e.g., 'bitcoin', 'ethereum', 'solana')
        days: Number of days to backtest (default: 10)
        initial_capital: Initial capital for the backtest (default: 10000.0)
    
    Returns:
        Backtest results with performance metrics and an artifact with detailed data.
    """
    try:
        # Initialize strategy with 10-day lookback
        strategy = MeanReversionStrategy(lookback_period=10)
        
        # Run backtest
        results = strategy.backtest_strategy(token_id, days=days, initial_capital=initial_capital)
        
        # Format the message
        total_return = results['total_return']
        buy_hold_return = results['buy_hold_return']
        num_trades = results['num_trades']
        ending_capital = results['ending_capital']
        
        # Determine if strategy outperformed buy-and-hold
        comparison = "OUTPERFORMED" if total_return > buy_hold_return else "UNDERPERFORMED"
        
        message = f"""
=== MEAN REVERSION BACKTEST RESULTS FOR {token_id.upper()} ===
Based on the last {days} days of price data

PERFORMANCE SUMMARY:
- Initial Capital: ${initial_capital:.2f}
- Final Capital: ${ending_capital:.2f}
- Total Return: {total_return:.2f}%
- Buy & Hold Return: {buy_hold_return:.2f}%
- Number of Trades: {num_trades}

The mean reversion strategy {comparison} buy-and-hold by {abs(total_return - buy_hold_return):.2f}%.

STRATEGY PARAMETERS:
- Lookback Period: 10 days
- Z-Score Threshold: ±2.0
- RSI Thresholds: 30/70

Note: Past performance is not indicative of future results.
This backtest is based on historical data and does not account for trading fees or slippage.
"""
        
        # Return both the message and the artifact
        return message, {
            "token_id": token_id,
            "days": days,
            "initial_capital": initial_capital,
            "ending_capital": ending_capital,
            "total_return": total_return,
            "buy_hold_return": buy_hold_return,
            "num_trades": num_trades,
            "results": results
        }
    except Exception as e:
        error_message = f"Error backtesting strategy for {token_id}: {str(e)}"
        return error_message, {"error": error_message}

# Example usage
if __name__ == "__main__":
    # Example 1: Get mean reversion signal
    token = "bitcoin"
    signal = get_token_mean_reversion_signal.invoke({"token_id": token})
    print(signal)
    
    # Example 2: Run a backtest
    message, artifact = backtest_mean_reversion_strategy.invoke({
        "token_id": token,
        "days": 10,
        "initial_capital": 10000.0
    })
    
    print("\n" + message)
    
    # Example 3: Visualize backtest results
    strategy = MeanReversionStrategy()
    results = strategy.backtest_strategy(token, days=10, initial_capital=10000.0)
    strategy.plot_backtest_results(results)