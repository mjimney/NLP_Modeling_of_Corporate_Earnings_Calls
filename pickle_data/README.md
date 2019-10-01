## Pickle File Inventory

1. **all_urls.pkl** - URL's of all earnings call transcripts
2. **all_pages.pkl** - Raw HTML of all earnings call transcripts
3. **all_tags.pkl** - Metadata for each earning call including stock ticker, date, time, fiscal quarter, fiscal year
4. **all_tickers.pkl** - Unique list of all stock tickers in scope for analysis
5. **all_dates.pkl** - Unique list of all dates in scope for analysis
6. **all_text.pkl** - The parsed earning call transcripts including speakers and part of call
7. **ticker_betas.pkl** - Tickers and corresponding 3 month betas

8. **prices.pkl** - Historical stock prices and price changes
9. **prices_adj.pkl** - Historical stock prices, historical S&P 500 prices, stock returns for each call, and correlation adjusted S&P 500 returns

| ID | Name | Description | Where it is Created |
| -- | ---- | ----------- | ------------------- |
| 01 | all_urls.pkl | URL's of all earnings call transcripts | 01_scrape_earnings_urls.py |
| 02 | all_pages.pkl | Raw HTML of all earnings call transcripts | 02_scrape_earnings_transcripts.py |
| 03 | all_tags.pkl | Metadata for each earning call including stock ticker, date, time, fiscal quarter, fiscal year | 03_transcript_processing.py |
| 04 | all_tickers.pkl | Unique list of all stock tickers in scope for analysis | 03_transcript_processing.py |
| 05 | all_dates.pkl | Unique list of all dates in scope for analysis | 03_transcript_processing.py |
| 06 | all_text.pkl | The parsed earning call transcripts including speakers and part of call | 03_transcript_processing.py |
| 07 | ticker_betas.pkl | Tickers and corresponding 3 month betas | 04_scrape_yahoo_betas.py |
| 08 | prices.pkl | Historical stock prices and price changes | 05_load_quandl_data.py |
| 09 | prices_adj.pkl | Historical stock prices, historical S&P 500 prices, stock returns for each call, and correlation adjusted S&P 500 returns | 06_snp500_adjustment.py |

