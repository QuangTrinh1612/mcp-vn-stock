import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
from typing import Literal, Optional, Tuple, Dict
from datetime import datetime

import pandas as pd
from pyrate_limiter import Duration, RequestRate, Limiter
from requests import Session
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin, MemoryQueueBucket

import yfinance as yf

logger = logging.getLogger(__name__)

class YahooFinanceSession:
    """Session manager for Yahoo Finance API requests with caching and rate limiting."""
    
    def __init__(self, requests_per_second: int = 5, cache_expiry: int = 3600, cache_name: str = "yfinance.cache"):
        """
        Initialize a rate-limited, cached session for Yahoo Finance requests.
        
        Args:
            requests_per_second: Maximum number of requests per second
            cache_expiry: Cache expiry time in seconds
            cache_name: Name of the SQLite cache file
        """
        # Create a session class that combines caching and rate limiting
        class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
            pass
            
        # Create and store the session
        self.session = CachedLimiterSession(
            limiter=Limiter(RequestRate(requests_per_second, Duration.SECOND)),
            bucket_class=MemoryQueueBucket,
            backend=SQLiteCache(cache_name, expire_after=cache_expiry),
        )


class YahooFinanceAgent:
    """Agent for retrieving various financial data from Yahoo Finance."""
    
    def __init__(self, session_manager: Optional[YahooFinanceSession] = None):
        """
        Initialize a Yahoo Finance agent.
        
        Args:
            session_manager: Optional session manager. If None, a new session manager will be created.
        """
        self.session_manager = session_manager or YahooFinanceSession()
        self.session = self.session_manager.session
    
    def _get_ticker(self, ticker: str) -> yf.Ticker:
        """Get a yfinance Ticker object with the configured session."""
        return yf.Ticker(ticker, session=self.session)
    
    def get_ticker_info(self, ticker: str) -> Optional[Dict]:
        """
        Get general information about a ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary of ticker information or None if an error occurred
        """
        try:
            return self._get_ticker(ticker).get_info()
        except Exception as e:
            logger.error(f"Error retrieving ticker info for {ticker}: {e}", exc_info=True)
            return None
    
    def get_calendar(self, ticker: str) -> Optional[Dict]:
        """
        Get calendar events including earnings and dividend dates.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary of calendar events or None if an error occurred
        """
        try:
            return self._get_ticker(ticker).get_calendar()
        except Exception as e:
            logger.error(f"Error retrieving calendar for {ticker}: {e}", exc_info=True)
            return None
    
    def get_recommendations(self, ticker: str, limit: int = 5) -> Optional[pd.DataFrame]:
        """
        Get analyst recommendations.
        
        Args:
            ticker: Stock ticker symbol
            limit: Number of most recent recommendations to return
            
        Returns:
            DataFrame with columns: Firm, To Grade, From Grade, Action or None if an error occurred
        """
        try:
            df = self._get_ticker(ticker).get_recommendations()
            return df.head(limit) if df is not None else None
        except Exception as e:
            logger.error(f"Error retrieving recommendations for {ticker}: {e}")
            return None
    
    def get_upgrades_downgrades(self, ticker: str, limit: int = 5) -> Optional[pd.DataFrame]:
        """
        Get upgrades/downgrades history.
        
        Args:
            ticker: Stock ticker symbol
            limit: Number of most recent upgrades/downgrades to return
            
        Returns:
            DataFrame with columns: firm, toGrade, fromGrade, action or None if an error occurred
        """
        try:
            df = self._get_ticker(ticker).get_upgrades_downgrades()
            return df.sort_index(ascending=False).head(limit) if df is not None else None
        except Exception as e:
            logger.error(f"Error retrieving upgrades/downgrades for {ticker}: {e}")
            return None
    
    def get_price_history(
        self, 
        ticker: str,
        period: Literal["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"] = "1mo"
    ) -> Optional[pd.DataFrame]:
        """
        Get historical price data.
        
        Args:
            ticker: Stock ticker symbol
            period: Time period of data to retrieve
            
        Returns:
            DataFrame of historical price data or None if an error occurred
        """
        try:
            return self._get_ticker(ticker).history(period=period)
        except Exception as e:
            logger.error(f"Error retrieving price history for {ticker}: {e}")
            return None
    
    def get_financial_statements(
        self,
        ticker: str,
        statement_type: Literal["income", "balance", "cash"] = "income",
        frequency: Literal["quarterly", "annual"] = "quarterly"
    ) -> Optional[pd.DataFrame]:
        """
        Get financial statements.
        
        Args:
            ticker: Stock ticker symbol
            statement_type: Type of financial statement to retrieve
            frequency: Frequency of financial statements to retrieve
            
        Returns:
            DataFrame of financial statement data or None if an error occurred
        """
        try:
            t = self._get_ticker(ticker)
            statements = {
                "income": {"annual": t.income_stmt, "quarterly": t.quarterly_income_stmt},
                "balance": {"annual": t.balance_sheet, "quarterly": t.quarterly_balance_sheet},
                "cash": {"annual": t.cashflow, "quarterly": t.quarterly_cashflow}
            }
            return statements[statement_type][frequency]
        except Exception as e:
            logger.error(f"Error retrieving {frequency} {statement_type} statement for {ticker}: {e}")
            return None
    
    def get_institutional_holders(
        self, 
        ticker: str, 
        top_n: int = 20
    ) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """
        Get institutional and mutual fund holdings.
        
        Args:
            ticker: Stock ticker symbol
            top_n: Number of top holders to return
            
        Returns:
            Tuple of (institutional holders DataFrame, mutual fund holders DataFrame)
            Either or both may be None if an error occurred
        """
        try:
            t = self._get_ticker(ticker)
            inst = t.get_institutional_holders()
            fund = t.get_mutualfund_holders()
            return (inst.head(top_n) if inst is not None else None,
                    fund.head(top_n) if fund is not None else None)
        except Exception as e:
            logger.error(f"Error retrieving institutional holders for {ticker}: {e}")
            return None, None
    
    def get_earnings_history(self, ticker: str, limit: int = 12) -> Optional[pd.DataFrame]:
        """
        Get earnings history data.
        
        Args:
            ticker: Stock ticker symbol
            limit: Number of earnings reports to return (default 12 shows 3 years of quarterly earnings)
            
        Returns:
            DataFrame of earnings history or None if an error occurred
        """
        try:
            df = self._get_ticker(ticker).get_earnings_history()
            return df.head(limit) if df is not None else None
        except Exception as e:
            logger.error(f"Error retrieving earnings history for {ticker}: {e}")
            return None
    
    def get_insider_trades(self, ticker: str, limit: int = 30) -> Optional[pd.DataFrame]:
        """
        Get insider transactions.
        
        Args:
            ticker: Stock ticker symbol
            limit: Number of insider transactions to return
            
        Returns:
            DataFrame of insider transactions or None if an error occurred
        """
        try:
            df = self._get_ticker(ticker).get_insider_transactions()
            return df.head(limit) if df is not None else None
        except Exception as e:
            logger.error(f"Error retrieving insider trades for {ticker}: {e}")
            return None
    
    def get_options_chain(
        self,
        ticker: str,
        expiry: Optional[str] = None,
        option_type: Optional[Literal["C", "P"]] = None
    ) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """
        Get options chain data for a specific expiry.
        
        Args:
            ticker: Stock ticker symbol
            expiry: Expiration date
            option_type: "C" for calls, "P" for puts, None for both
            
        Returns:
            Tuple of (options chain DataFrame, error message)
            DataFrame is None if an error occurred, in which case error message is not None
        """
        try:
            if not expiry:
                return None, "No expiry date provided"

            chain = self._get_ticker(ticker).option_chain(expiry)

            if option_type == "C":
                return chain.calls, None
            elif option_type == "P":
                return chain.puts, None
            return pd.concat([chain.calls, chain.puts]), None

        except Exception as e:
            logger.error(f"Error retrieving options chain for {ticker}: {e}")
            return None, str(e)
    
    def get_filtered_options(
        self,
        ticker: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        strike_lower: Optional[float] = None,
        strike_upper: Optional[float] = None,
        option_type: Optional[Literal["C", "P"]] = None,
    ) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """
        Get filtered options data efficiently.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Filter options with expiry >= this date (format: YYYY-MM-DD)
            end_date: Filter options with expiry <= this date (format: YYYY-MM-DD)
            strike_lower: Filter options with strike >= this value
            strike_upper: Filter options with strike <= this value
            option_type: "C" for calls, "P" for puts, None for both
            
        Returns:
            Tuple of (filtered options DataFrame, error message)
            DataFrame is None if an error occurred, in which case error message is not None
        """
        try:
            # Validate date formats before processing
            if start_date:
                try:
                    datetime.strptime(start_date, "%Y-%m-%d")
                except ValueError:
                    return None, f"Invalid start_date format. Use YYYY-MM-DD"
                    
            if end_date:
                try:
                    datetime.strptime(end_date, "%Y-%m-%d")
                except ValueError:
                    return None, f"Invalid end_date format. Use YYYY-MM-DD"

            t = self._get_ticker(ticker)
            expirations = t.options

            if not expirations:
                return None, f"No options available for {ticker}"

            # Convert date strings to datetime objects once
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

            # Filter expiration dates before making API calls
            valid_expirations = []
            for exp in expirations:
                exp_date = datetime.strptime(exp, "%Y-%m-%d").date()
                if ((not start_date_obj or exp_date >= start_date_obj) and
                    (not end_date_obj or exp_date <= end_date_obj)):
                    valid_expirations.append(exp)

            if not valid_expirations:
                return None, f"No options found for {ticker} within specified date range"

            # Parallel fetch options using ThreadPoolExecutor
            filtered_option_chains = []
            with ThreadPoolExecutor() as executor:
                options_results = list(executor.map(
                    lambda exp: self.get_options_chain(ticker, exp, option_type),
                    valid_expirations
                ))

            for (chain, error), expiry in zip(options_results, valid_expirations):
                if error:
                    logger.warning(f"Error fetching options for expiry {expiry}: {error}")
                    continue
                if chain is not None:
                    filtered_option_chains.append(chain.assign(expiryDate=expiry))

            if not filtered_option_chains:
                return None, f"No options found for {ticker} matching criteria"

            df = pd.concat(filtered_option_chains, ignore_index=True)

            # Apply strike price filters
            if strike_lower is not None or strike_upper is not None:
                mask = pd.Series(True, index=df.index)
                if strike_lower is not None:
                    mask &= df['strike'] >= strike_lower
                if strike_upper is not None:
                    mask &= df['strike'] <= strike_upper
                df = df[mask]

            return df.sort_values(['openInterest', 'volume'], ascending=[False, False]), None

        except Exception as e:
            logger.error(f"Error in get_filtered_options: {str(e)}", exc_info=True)
            return None, f"Failed to retrieve options data: {str(e)}"