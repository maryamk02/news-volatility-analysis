"""
News Event Impact on Stock Volatility Analysis
Inspired by Permutable AI's LLM-driven news analytics

This script analyzes how major news events affect stock price volatility
by comparing volatility in windows before and after significant announcements.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# ============================================================================
# STEP 1: Define News Events (manually tagged)
# ============================================================================

# Format: 'Event Description': 'YYYY-MM-DD'
events_data = {
    'AAPL': {
        'iPhone 15 Launch': '2023-09-12',
        'Q1 2024 Earnings Beat': '2024-02-01',
        'Services Revenue Record': '2024-05-02',
        'Vision Pro Announcement': '2023-06-05',
        'Q3 2023 Earnings Miss': '2023-08-03'
    },
    'TSLA': {
        'Cybertruck Delivery Event': '2023-11-30',
        'Q4 2023 Earnings Beat': '2024-01-24',
        'Price Cuts Announced': '2024-04-05',
        'Musk Twitter Controversy': '2023-07-17',
        'Model 3 Highland Launch': '2023-09-01'
    },
    'META': {
        'Q1 2023 Earnings Surprise': '2023-04-26',
        'Threads App Launch': '2023-07-05',
        'AI Investment Announcement': '2024-02-02',
        'Q4 2023 Strong Guidance': '2024-02-01',
        'Reality Labs Loss Report': '2023-10-25'
    }
}

# ============================================================================
# STEP 2: Fetch Stock Data Using yfinance API
# ============================================================================

def get_stock_data(ticker, start_date='2023-01-01', end_date='2024-12-31'):
    """Download historical stock data from Yahoo Finance"""
    print(f"Fetching data for {ticker}...")
    data = yf.download(ticker, start=start_date, end=end_date, progress=False)
    return data

# ============================================================================
# STEP 3: Calculate Volatility Around Events
# ============================================================================

def calculate_event_volatility(stock_data, event_date, window=5):
    """
    Calculate volatility before and after an event
    
    Parameters:
    - stock_data: DataFrame with stock prices
    - event_date: Date of the news event
    - window: Number of trading days to analyze (default 5)
    
    Returns:
    - Tuple of (before_volatility, after_volatility)
    """
    event_date = pd.to_datetime(event_date)
    
    # Calculate daily returns
    stock_data['Returns'] = stock_data['Close'].pct_change()
    
    # Get trading days around the event
    event_idx = stock_data.index.searchsorted(event_date)
    
    # Before event window
    before_start = max(0, event_idx - window - 1)
    before_end = event_idx
    before_returns = stock_data['Returns'].iloc[before_start:before_end]
    
    # After event window
    after_start = event_idx
    after_end = min(len(stock_data), event_idx + window)
    after_returns = stock_data['Returns'].iloc[after_start:after_end]
    
    # Calculate volatility (standard deviation of returns)
    before_vol = before_returns.std()
    after_vol = after_returns.std()
    
    return before_vol, after_vol

# ============================================================================
# STEP 4: Analyze All Events
# ============================================================================

def analyze_all_events(events_dict):
    """Analyze volatility changes for all events across all tickers"""
    results = []
    
    for ticker, events in events_dict.items():
        # Get stock data
        stock_data = get_stock_data(ticker)
        
        print(f"\nAnalyzing {ticker} events:")
        
        for event_name, event_date in events.items():
            # Calculate volatility
            before_vol, after_vol = calculate_event_volatility(stock_data, event_date)
            
            # Handle pandas Series/scalar conversion
            before_vol_value = float(before_vol) if not pd.isna(before_vol) else 0
            after_vol_value = float(after_vol) if not pd.isna(after_vol) else 0
            
            if before_vol_value > 0 and after_vol_value > 0:
                vol_change = after_vol_value - before_vol_value
                vol_change_pct = (vol_change / before_vol_value) * 100
                
                results.append({
                    'Ticker': ticker,
                    'Event': event_name,
                    'Date': event_date,
                    'Before_Volatility': before_vol_value,
                    'After_Volatility': after_vol_value,
                    'Volatility_Change': vol_change,
                    'Volatility_Change_Pct': vol_change_pct
                })
                
                print(f"  ✓ {event_name}: {vol_change_pct:+.1f}% volatility change")
    
    return pd.DataFrame(results)

# ============================================================================
# STEP 5: Create Visualizations
# ============================================================================

def create_visualizations(results_df):
    """Create charts showing volatility impact"""
    
    # Chart 1: Volatility change by event
    plt.figure(figsize=(14, 8))
    colors = {'AAPL': '#007AFF', 'TSLA': '#E31937', 'META': '#0668E1'}
    
    for ticker in results_df['Ticker'].unique():
        ticker_data = results_df[results_df['Ticker'] == ticker]
        plt.barh(
            ticker_data['Event'], 
            ticker_data['Volatility_Change_Pct'],
            color=colors.get(ticker, '#333333'),
            label=ticker,
            alpha=0.8
        )
    
    plt.xlabel('Volatility Change (%)', fontsize=12)
    plt.ylabel('Event', fontsize=12)
    plt.title('News Event Impact on Stock Volatility (5-Day Windows)', fontsize=14, fontweight='bold')
    plt.axvline(x=0, color='black', linestyle='--', linewidth=0.8)
    plt.legend()
    plt.tight_layout()
    plt.savefig('news_volatility_impact.png', dpi=300, bbox_inches='tight')
    print("\n✓ Saved: news_volatility_impact.png")
    
    # Chart 2: Average impact by company
    plt.figure(figsize=(10, 6))
    avg_by_ticker = results_df.groupby('Ticker')['Volatility_Change_Pct'].mean()
    bars = plt.bar(avg_by_ticker.index, avg_by_ticker.values, 
                   color=[colors.get(t, '#333333') for t in avg_by_ticker.index],
                   alpha=0.8)
    
    plt.xlabel('Company', fontsize=12)
    plt.ylabel('Average Volatility Change (%)', fontsize=12)
    plt.title('Average News Impact on Volatility by Company', fontsize=14, fontweight='bold')
    plt.axhline(y=0, color='black', linestyle='--', linewidth=0.8)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('volatility_by_company.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: volatility_by_company.png")

# ============================================================================
# STEP 6: Summary Statistics
# ============================================================================

def print_summary_stats(results_df):
    """Print summary statistics"""
    print("\n" + "="*70)
    print("SUMMARY STATISTICS")
    print("="*70 + "\n")
    
    print(f"Total events analyzed: {len(results_df)}\n")
    
    print(f"Average volatility change: {results_df['Volatility_Change_Pct'].mean():+.1f}%")
    print(f"Median volatility change: {results_df['Volatility_Change_Pct'].median():+.1f}%\n")
    
    increased = len(results_df[results_df['Volatility_Change_Pct'] > 0])
    decreased = len(results_df[results_df['Volatility_Change_Pct'] < 0])
    
    print(f"Events with increased volatility: {increased} ({increased/len(results_df)*100:.1f}%)")
    print(f"Events with decreased volatility: {decreased} ({decreased/len(results_df)*100:.1f}%)\n")
    
    # Top 3 largest increases
    top_increases = results_df.nlargest(3, 'Volatility_Change_Pct')
    print("Largest volatility increases:")
    for _, row in top_increases.iterrows():
        print(f"  • {row['Ticker']}: {row['Event']} ({row['Volatility_Change_Pct']:+.1f}%)")
    
    # By company
    print("\nBy company:")
    for ticker in results_df['Ticker'].unique():
        ticker_avg = results_df[results_df['Ticker'] == ticker]['Volatility_Change_Pct'].mean()
        print(f"  {ticker}: {ticker_avg:+.1f}% average change")
    
    print("\n" + "="*70 + "\n")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("NEWS EVENT VOLATILITY IMPACT ANALYSIS")
    print("Inspired by Permutable AI's LLM-driven news analytics")
    print("="*70)
    
    # Run analysis
    results_df = analyze_all_events(events_data)
    
    # Save results
    results_df.to_csv('volatility_results.csv', index=False)
    print("\n✓ Saved: volatility_results.csv")
    
    # Create visualizations
    create_visualizations(results_df)
    
    # Print summary
    print_summary_stats(results_df)
    
    print("✓ Analysis complete! Check the output files:")
    print("  - volatility_results.csv")
    print("  - news_volatility_impact.png")
    print("  - volatility_by_company.png")
