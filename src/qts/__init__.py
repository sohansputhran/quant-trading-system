# Re-export public API for convenient imports
from .app_utils import (
    set_page_config,
    inject_css,
    generate_sample_price_data,
    generate_sample_strategy_data,
)
from .fred_utils import (
    FRED_PRESETS,
    fred_fetch_many,
    fred_transform,
    fred_key_loaded,
)

__all__ = [
    # app_utils
    "set_page_config",
    "inject_css",
    "generate_sample_price_data",
    "generate_sample_strategy_data",
    # fred_utils
    "FRED_PRESETS",
    "fred_fetch_many",
    "fred_transform",
    "fred_key_loaded",
]
