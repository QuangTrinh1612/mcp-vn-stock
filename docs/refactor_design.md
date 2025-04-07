# vnstock Modern Component Portfolio (MCP)

## Project Overview

vnstock is a Python library for Vietnamese stock market data analysis and visualization. This MCP refactors the existing project structure to improve modularity, maintainability, testability, and extensibility.

## Core Design Principles

1. **Separation of Concerns**: Clearly separate data fetching, processing, analysis, and visualization
2. **Modularity**: Components should be independent and reusable
3. **Extensibility**: Easy to add new data sources, analysis methods, or visualization types
4. **Configurability**: Centralized configuration management
5. **Error Handling**: Consistent error handling throughout the codebase
6. **Documentation**: Comprehensive documentation using docstrings and type hints
7. **Testing**: Comprehensive test coverage

## Refactored Folder Structure

```
vnstock/
├── pyproject.toml                # Modern Python packaging
├── setup.py                      # Backward compatibility for setuptools
├── requirements.txt              # Development dependencies
├── README.md                     # Project documentation
├── CHANGELOG.md                  # Version history
├── LICENSE                       # License information
├── .github/                      # GitHub workflows and templates
│   └── workflows/
│       ├── ci.yml                # Continuous integration
│       └── publish.yml           # Package publishing
├── docs/                         # Documentation
│   ├── index.md                  # Main documentation page
│   ├── installation.md           # Installation guide
│   ├── api/                      # API documentation
│   ├── tutorials/                # Usage tutorials
│   └── examples/                 # Example notebooks
├── tests/                        # Test suite
│   ├── conftest.py               # Test configuration
│   ├── test_data/                # Test data
│   ├── test_fetchers/            # Tests for data fetchers
│   ├── test_analysis/            # Tests for analysis modules
│   ├── test_visualization/       # Tests for visualization modules
│   └── test_portfolio/           # Tests for portfolio modules
└── vnstock/                      # Main package
    ├── __init__.py               # Package initialization
    ├── version.py                # Version information
    ├── config/                   # Configuration management
    │   ├── __init__.py
    │   ├── settings.py           # Global settings
    │   └── endpoints.py          # API endpoint configuration
    ├── core/                     # Core functionality
    │   ├── __init__.py
    │   ├── exceptions.py         # Custom exceptions
    │   ├── cache.py              # Cache management
    │   ├── validators.py         # Input validation
    │   └── utils.py              # Utility functions
    ├── fetchers/                 # Data fetching modules
    │   ├── __init__.py
    │   ├── base.py               # Base fetcher class
    │   ├── stock.py              # Stock price fetcher
    │   ├── financial.py          # Financial statement fetcher
    │   ├── company.py            # Company information fetcher
    │   └── market.py             # Market data fetcher
    ├── analysis/                 # Analysis modules
    │   ├── __init__.py
    │   ├── technical/            # Technical analysis
    │   │   ├── __init__.py
    │   │   ├── momentum.py       # Momentum indicators (RSI, MACD)
    │   │   ├── trend.py          # Trend indicators (Moving Averages)
    │   │   ├── volatility.py     # Volatility indicators (Bollinger Bands)
    │   │   └── volume.py         # Volume indicators (OBV)
    │   └── fundamental/          # Fundamental analysis
    │       ├── __init__.py
    │       ├── ratios.py         # Financial ratios
    │       ├── valuation.py      # Valuation models
    │       └── comparison.py     # Peer comparison
    ├── portfolio/                # Portfolio management
    │   ├── __init__.py
    │   ├── construction.py       # Portfolio construction
    │   ├── optimization.py       # Portfolio optimization
    │   ├── risk.py               # Risk analysis
    │   └── performance.py        # Performance metrics
    ├── visualization/            # Data visualization
    │   ├── __init__.py
    │   ├── charts/               # Chart plotting
    │   │   ├── __init__.py
    │   │   ├── candlestick.py    # Candlestick charts
    │   │   ├── line.py           # Line charts
    │   │   ├── bar.py            # Bar charts
    │   │   └── heatmap.py        # Heatmaps
    │   └── dashboard/            # Dashboard components
    │       ├── __init__.py
    │       ├── components.py     # Reusable components
    │       └── layouts.py        # Dashboard layouts
    └── cli/                      # Command line interface
        ├── __init__.py
        ├── commands.py           # CLI commands
        └── formatters.py         # Output formatting
```

## Key Components

### 1. Configuration Management

The `config` module centralizes all configuration settings:

- **settings.py**: Global settings like default cache duration, timeout values
- **endpoints.py**: API endpoints for different data sources

### 2. Core

The `core` module contains fundamental utilities:

- **exceptions.py**: Custom exception classes for better error handling
- **cache.py**: Caching mechanism to reduce API calls
- **validators.py**: Input validation functions
- **utils.py**: General utility functions

### 3. Data Fetchers

The `fetchers` module includes components for retrieving data:

- **base.py**: Base fetcher class with common functionality
- **stock.py**: Stock price data fetcher
- **financial.py**: Financial statement fetcher
- **company.py**: Company information fetcher
- **market.py**: Market data fetcher

### 4. Analysis

The `analysis` module contains analytical components:

- **technical/**: Technical analysis indicators
- **fundamental/**: Fundamental analysis tools

### 5. Portfolio Management

The `portfolio` module handles portfolio-related functions:

- **construction.py**: Portfolio construction
- **optimization.py**: Portfolio optimization
- **risk.py**: Risk analysis
- **performance.py**: Performance metrics

### 6. Visualization

The `visualization` module provides data visualization tools:

- **charts/**: Various chart types
- **dashboard/**: Dashboard components and layouts

### 7. CLI

The `cli` module offers command-line functionality:

- **commands.py**: CLI commands
- **formatters.py**: Output formatting

## Implementation Details

### 1. Base Fetcher Class

```python
from abc import ABC, abstractmethod
import requests
from typing import Dict, Any, Optional, Union
import pandas as pd
from ..core.exceptions import APIError, DataNotFoundError
from ..config.settings import DEFAULT_TIMEOUT

class BaseFetcher(ABC):
    """Base class for all data fetchers."""
    
    def __init__(self, timeout: Optional[int] = None):
        """
        Initialize the fetcher.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout or DEFAULT_TIMEOUT
    
    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make an HTTP request to the specified URL.
        
        Args:
            url: API endpoint URL
            params: Query parameters
            
        Returns:
            Response data as dictionary
            
        Raises:
            APIError: If the request fails
        """
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise APIError(f"API request failed: {str(e)}")
    
    def _process_response(self, response_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Process the API response into a pandas DataFrame.
        
        Args:
            response_data: Response data from API
            
        Returns:
            Processed data as pandas DataFrame
        """
        if not response_data:
            raise DataNotFoundError("No data returned from API")
        
        return self._convert_to_dataframe(response_data)
    
    @abstractmethod
    def _convert_to_dataframe(self, data: Dict[str, Any]) -> pd.DataFrame:
        """
        Convert the API response to a pandas DataFrame.
        
        Must be implemented by subclasses.
        
        Args:
            data: Data from API response
            
        Returns:
            Data as pandas DataFrame
        """
        pass
    
    @abstractmethod
    def fetch(self, *args, **kwargs) -> pd.DataFrame:
        """
        Fetch data from the API.
        
        Must be implemented by subclasses.
        
        Returns:
            Fetched data as pandas DataFrame
        """
        pass
```

### 2. Stock Price Fetcher

```python
from typing import Optional, Dict, Any
import pandas as pd
from datetime import datetime, date
from .base import BaseFetcher
from ..config.endpoints import STOCK_PRICE_ENDPOINT
from ..core.validators import validate_ticker, validate_date_range, validate_resolution

class StockPriceFetcher(BaseFetcher):
    """Fetcher for stock price data."""
    
    def _convert_to_dataframe(self, data: Dict[str, Any]) -> pd.DataFrame:
        """
        Convert stock price data to DataFrame.
        
        Args:
            data: Stock price data from API
            
        Returns:
            Stock price data as DataFrame
        """
        df = pd.DataFrame(data.get('data', []))
        if not df.empty:
            # Convert date string to datetime
            df['time'] = pd.to_datetime(df['time'])
            # Set date as index
            df.set_index('time', inplace=True)
            # Convert numeric columns
            numeric_cols = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col])
        return df
    
    def fetch(
        self, 
        symbol: str, 
        start_date: Optional[Union[str, date, datetime]] = None,
        end_date: Optional[Union[str, date, datetime]] = None,
        resolution: str = "1D"
    ) -> pd.DataFrame:
        """
        Fetch historical stock price data.
        
        Args:
            symbol: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            resolution: Data resolution (1D, 1W, 1M)
            
        Returns:
            Historical stock price data as DataFrame
            
        Raises:
            ValueError: If input parameters are invalid
        """
        # Validate inputs
        symbol = validate_ticker(symbol)
        start_date, end_date = validate_date_range(start_date, end_date)
        resolution = validate_resolution(resolution)
        
        # Prepare request parameters
        params = {
            'symbol': symbol,
            'from': start_date.strftime('%Y-%m-%d'),
            'to': end_date.strftime('%Y-%m-%d'),
            'resolution': resolution
        }
        
        # Make request
        response_data = self._make_request(STOCK_PRICE_ENDPOINT, params)
        
        # Process response
        return self._process_response(response_data)
```

### 3. Example Usage

```python
# Old way
from vnstock import *
df = stock_historical_data("TCB", "2022-01-01", "2022-03-31", "1D")

# New way
from vnstock.fetchers import StockPriceFetcher
fetcher = StockPriceFetcher()
df = fetcher.fetch("TCB", "2022-01-01", "2022-03-31", "1D")

# Or using a factory pattern
from vnstock import get_fetcher
stock_fetcher = get_fetcher('stock_price')
df = stock_fetcher.fetch("TCB", "2022-01-01", "2022-03-31", "1D")

# For backward compatibility
from vnstock import stock_historical_data
df = stock_historical_data("TCB", "2022-01-01", "2022-03-31", "1D")
```

## Key Improvements

1. **Modular Architecture**:
   - Clear separation between data fetching, analysis, and visualization
   - Each component has a single responsibility

2. **Extensibility**:
   - Easy to add new data sources, indicators, or visualization types
   - Base classes provide common functionality

3. **Error Handling**:
   - Custom exception classes for different error types
   - Consistent error handling throughout the codebase

4. **Performance**:
   - Caching mechanism to reduce API calls
   - Efficient data processing with pandas

5. **Maintainability**:
   - Clear folder structure
   - Comprehensive documentation
   - Type hints for better IDE support

6. **Testing**:
   - Dedicated test directory with test data
   - Separate test files for each module

7. **Documentation**:
   - Comprehensive API documentation
   - Usage examples and tutorials

## Migration Strategy

1. **Phase 1: Core Infrastructure**
   - Set up project structure
   - Implement base classes and core utilities
   - Create configuration management

2. **Phase 2: Data Fetchers**
   - Implement data fetchers with new architecture
   - Add backward compatibility layer

3. **Phase 3: Analysis Components**
   - Refactor technical and fundamental analysis
   - Implement new analysis tools

4. **Phase 4: Portfolio & Visualization**
   - Refactor portfolio management
   - Implement visualization components

5. **Phase 5: CLI & Documentation**
   - Implement command-line interface
   - Create comprehensive documentation

## Backward Compatibility

To maintain backward compatibility, the top-level `__init__.py` will expose familiar functions that internally use the new architecture:

```python
# vnstock/__init__.py
from .version import __version__
from .fetchers.stock import StockPriceFetcher
from .fetchers.financial import FinancialStatementFetcher
# ... other imports

# Factory function to get fetchers
def get_fetcher(fetcher_type):
    fetchers = {
        'stock_price': StockPriceFetcher(),
        'financial': FinancialStatementFetcher(),
        # ... other fetchers
    }
    return fetchers.get(fetcher_type)

# Backward compatibility functions
def stock_historical_data(symbol, start_date=None, end_date=None, resolution="1D"):
    """Get historical stock price data."""
    fetcher = StockPriceFetcher()
    return fetcher.fetch(symbol, start_date, end_date, resolution)

def financial_statement(symbol, report_type, report_frequency, start_year, end_year):
    """Get financial statement data."""
    fetcher = FinancialStatementFetcher()
    return fetcher.fetch(symbol, report_type, report_frequency, start_year, end_year)

# ... other backward compatibility functions
```

## Conclusion

This Modern Component Portfolio for vnstock significantly improves the project's architecture while maintaining backward compatibility. The new structure enhances modularity, maintainability, and extensibility, making it easier to add new features and fix bugs. The comprehensive documentation and testing strategy ensure that the library remains robust and user-friendly.