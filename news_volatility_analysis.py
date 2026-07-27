"""
News Event Impact on Stock Volatility Analysis
Analyses how major news events affect stock price volatility
by comparing volatility in windows before and after significant announcements.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# STEP 1: Define News Events (manually tagged)
# ============================================================
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

# ============================================================
# STEP 2: Fetch Stock Data
# ============================================================
def get_stock_data(ticker, start_date='2023-01-01', end_date='2024-12-31'):
    print(f"Fetching data for {ticker}...")
    return yf.download(ticker, start=start_date, end=end_date,
                       progress=False, auto_adjust=True)

# ============================================================
# STEP 3: Calculate Volatility Around Events
# ============================================================
def calculate_event_volatility(stock_data, event_date, window=5):
    event_date = pd.to_datetime(event_date)
    stock_data['Returns'] = stock_data['Close'].pct_change()
    event_idx = stock_data.index.searchsorted(event_date)

    before_returns = stock_data['Returns'].iloc[max(0, event_idx - window - 1):event_idx]
    after_returns = stock_data['Returns'].iloc[event_idx:min(len(stock_data), event_idx + window)]

    return before_returns.std(), after_returns.std()

# ============================================================
# STEP 4: Analyse All Events
# ============================================================
def analyse_all_events(events_dict):
    results = []
    for ticker, events in events_dict.items():
        stock_data = get_stock_data(ticker)
        print(f"\nAnalysing {ticker} events:")
        for event_name, event_date in events.items():
            before_vol, after_vol = calculate_event_volatility(stock_data, event_date)
            before_vol = float(before_vol) if not pd.isna(before_vol) else 0
            after_vol = float(after_vol) if not pd.isna(after_vol) else 0
            if before_vol > 0 and after_vol > 0:
                vol_change = after_vol - before_vol
                vol_change_pct = (vol_change / before_vol) * 100
                results.append({
                    'Ticker': ticker,
                    'Event': event_name,
                    'Date': event_date,
                    'Before_Volatility': before_vol,
                    'After_Volatility': after_vol,
                    'Volatility_Change': vol_change,
                    'Volatility_Change_Pct': vol_change_pct
                })
                print(f"  + {event_name}: {vol_change_pct:+.1f}% volatility change")
    return pd.DataFrame(results)

# ============================================================
# STEP 5: Create Visualisations
# ============================================================
def create_visualisations(results_df):
    colors = {'AAPL': '#007AFF', 'TSLA': '#E31937', 'META': '#0668E1'}

    plt.figure(figsize=(14, 8))
    for ticker in results_df['Ticker'].unique():
        d = results_df[results_df['Ticker'] == ticker]
        plt.barh(d['Event'], d['Volatility_Change_Pct'],
                 color=colors.get(ticker, '#333333'), label=ticker, alpha=0.8)
    plt.xlabel('Volatility Change (%)', fontsize=12)
    plt.ylabel('Event', fontsize=12)
    plt.title('News Event Impact on Stock Volatility (5-Day Windows)', fontsize=14, fontweight='bold')
    plt.axvline(x=0, color='black', linestyle='--', linewidth=0.8)
    plt.legend()
    plt.tight_layout()
    plt.savefig('news_volatility_impact.png', dpi=300, bbox_inches='tight')
    print("\n+ Saved: news_volatility_impact.png")

    plt.figure(figsize=(10, 6))
    avg = results_df.groupby('Ticker')['Volatility_Change_Pct'].mean()
    bars = plt.bar(avg.index, avg.values,
                   color=[colors.get(t, '#333333') for t in avg.index], alpha=0.8)
    plt.xlabel('Company', fontsize=12)
    plt.ylabel('Average Volatility Change (%)', fontsize=12)
    plt.title('Average News Impact on Volatility by Company', fontsize=14, fontweight='bold')
    plt.axhline(y=0, color='black', linestyle='--', linewidth=0.8)
    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., h, f'{h:.1f}%',
                 ha='center', va='bottom', fontsize=10)
    plt.tight_layout()
    plt.savefig('volatility_by_company.png', dpi=300, bbox_inches='tight')
    print("+ Saved: volatility_by_company.png")

# ============================================================
# STEP 6: Summary Statistics
# ============================================================
def print_summary_stats(results_df):
    print("\n" + "="*70)
    print("SUMMARY STATISTICS")
    print("="*70 + "\n")
    print(f"Total events analysed: {len(results_df)}\n")
    print(f"Average volatility change: {results_df['Volatility_Change_Pct'].mean():+.1f}%")
    print(f"Median volatility change: {results_df['Volatility_Change_Pct'].median():+.1f}%\n")
    inc = len(results_df[results_df['Volatility_Change_Pct'] > 0])
    dec = len(results_df[results_df['Volatility_Change_Pct'] < 0])
    print(f"Events with increased volatility: {inc} ({inc/len(results_df)*100:.0f}%)")
    print(f"Events with decreased volatility: {dec} ({dec/len(results_df)*100:.0f}%)\n")
    print("Largest volatility increases:")
    for _, r in results_df.nlargest(3, 'Volatility_Change_Pct').iterrows():
        print(f"  - {r['Ticker']}: {r['Event']} ({r['Volatility_Change_Pct']:+.1f}%)")
    print("\nLargest volatility decreases:")
    for _, r in results_df.nsmallest(3, 'Volatility_Change_Pct').iterrows():
        print(f"  - {r['Ticker']}: {r['Event']} ({r['Volatility_Change_Pct']:+.1f}%)")
    print("\nBy company:")
    for ticker in results_df['Ticker'].unique():
        avg = results_df[results_df['Ticker'] == ticker]['Volatility_Change_Pct'].mean()
        print(f"  {ticker}: {avg:+.1f}% average change")
    print("\n" + "="*70 + "\n")

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("="*70)
    print("NEWS EVENT VOLATILITY IMPACT ANALYSIS")
    print("="*70)
    results_df = analyse_all_events(events_data)
    results_df.to_csv('volatility_results.csv', index=False)
    print("\n+ Saved: volatility_results.csv")
    create_visualisations(results_df)
    print_summary_stats(results_df) 
