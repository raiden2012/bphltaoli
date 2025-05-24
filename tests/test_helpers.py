#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for the helpers module

Tests all utility functions in funding_arbitrage_bot.utils.helpers
"""

import os
import sys
import tempfile
import yaml
import logging
from decimal import Decimal
from datetime import datetime
from unittest.mock import patch, mock_open

import pytest

# Add the project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from funding_arbitrage_bot.utils.helpers import (
    get_backpack_symbol,
    get_hyperliquid_symbol,
    decimal_adjust,
    safe_get,
    load_config,
    calculate_funding_diff,
    get_symbol_from_exchange_symbol,
    convert_exchange_positions_to_local,
    configure_logging,
    round_to_tick,
    format_number
)


class TestSymbolConversion:
    """Test symbol conversion functions"""
    
    def test_get_backpack_symbol(self):
        """Test Backpack symbol formatting"""
        assert get_backpack_symbol("BTC") == "BTC_USDC_PERP"
        assert get_backpack_symbol("ETH") == "ETH_USDC_PERP"
        assert get_backpack_symbol("SOL") == "SOL_USDC_PERP"
        assert get_backpack_symbol("") == "_USDC_PERP"
    
    def test_get_hyperliquid_symbol(self):
        """Test Hyperliquid symbol formatting"""
        assert get_hyperliquid_symbol("BTC") == "BTC"
        assert get_hyperliquid_symbol("ETH") == "ETH"
        assert get_hyperliquid_symbol("SOL") == "SOL"
        assert get_hyperliquid_symbol("") == ""
    
    def test_get_symbol_from_exchange_symbol_backpack(self):
        """Test extracting base symbol from Backpack format"""
        assert get_symbol_from_exchange_symbol("BTC_USDC_PERP", "backpack") == "BTC"
        assert get_symbol_from_exchange_symbol("ETH_USDC_PERP", "backpack") == "ETH"
        assert get_symbol_from_exchange_symbol("SOL_USDC_PERP", "backpack") == "SOL"
        assert get_symbol_from_exchange_symbol("", "backpack") is None
        # For backpack, if no underscore, it falls through to default behavior
        assert get_symbol_from_exchange_symbol("BTC", "backpack") == "BTC"
    
    def test_get_symbol_from_exchange_symbol_hyperliquid(self):
        """Test extracting base symbol from Hyperliquid format"""
        assert get_symbol_from_exchange_symbol("BTC", "hyperliquid") == "BTC"
        assert get_symbol_from_exchange_symbol("ETH", "hyperliquid") == "ETH"
        assert get_symbol_from_exchange_symbol("SOL", "hyperliquid") == "SOL"
        # Empty string returns None due to the initial check
        assert get_symbol_from_exchange_symbol("", "hyperliquid") is None
    
    def test_get_symbol_from_exchange_symbol_unknown_exchange(self):
        """Test with unknown exchange type"""
        assert get_symbol_from_exchange_symbol("BTC", "unknown") == "BTC"
        assert get_symbol_from_exchange_symbol("BTC_USDC_PERP", "unknown") == "BTC_USDC_PERP"


class TestDecimalAdjust:
    """Test decimal adjustment function"""
    
    def test_decimal_adjust_round_down(self):
        """Test decimal adjustment with ROUND_DOWN"""
        assert decimal_adjust(1.23456, 2, 'ROUND_DOWN') == 1.23
        assert decimal_adjust(1.23956, 2, 'ROUND_DOWN') == 1.23
        assert decimal_adjust(1.0, 2, 'ROUND_DOWN') == 1.0
        assert decimal_adjust(0.999, 2, 'ROUND_DOWN') == 0.99
    
    def test_decimal_adjust_round_up(self):
        """Test decimal adjustment with ROUND_UP"""
        assert decimal_adjust(1.23456, 2, 'ROUND_UP') == 1.24
        assert decimal_adjust(1.23056, 2, 'ROUND_UP') == 1.24
        assert decimal_adjust(1.0, 2, 'ROUND_UP') == 1.0
    
    def test_decimal_adjust_round_half_up(self):
        """Test decimal adjustment with ROUND_HALF_UP"""
        assert decimal_adjust(1.235, 2, 'ROUND_HALF_UP') == 1.24
        assert decimal_adjust(1.234, 2, 'ROUND_HALF_UP') == 1.23
        assert decimal_adjust(1.225, 2, 'ROUND_HALF_UP') == 1.23  # Banker's rounding
    
    def test_decimal_adjust_different_precisions(self):
        """Test decimal adjustment with different precisions"""
        assert decimal_adjust(1.23456, 0, 'ROUND_DOWN') == 1.0
        assert decimal_adjust(1.23456, 1, 'ROUND_DOWN') == 1.2
        assert decimal_adjust(1.23456, 3, 'ROUND_DOWN') == 1.234
        assert decimal_adjust(1.23456, 4, 'ROUND_DOWN') == 1.2345
    
    def test_decimal_adjust_invalid_rounding_mode(self):
        """Test decimal adjustment with invalid rounding mode"""
        with pytest.raises(ValueError, match="无效的舍入模式"):
            decimal_adjust(1.23456, 2, 'INVALID_MODE')


class TestSafeGet:
    """Test safe dictionary access function"""
    
    def test_safe_get_simple(self):
        """Test safe_get with simple dictionary"""
        data = {"a": 1, "b": 2}
        assert safe_get(data, ["a"]) == 1
        assert safe_get(data, ["b"]) == 2
        assert safe_get(data, ["c"]) is None
        assert safe_get(data, ["c"], "default") == "default"
    
    def test_safe_get_nested(self):
        """Test safe_get with nested dictionary"""
        data = {
            "level1": {
                "level2": {
                    "level3": "value"
                }
            }
        }
        assert safe_get(data, ["level1", "level2", "level3"]) == "value"
        assert safe_get(data, ["level1", "level2"]) == {"level3": "value"}
        assert safe_get(data, ["level1", "missing"]) is None
        assert safe_get(data, ["missing", "level2", "level3"]) is None
    
    def test_safe_get_with_non_dict(self):
        """Test safe_get when intermediate value is not a dict"""
        data = {"a": "string_value"}
        assert safe_get(data, ["a", "b"]) is None
        assert safe_get(data, ["a", "b"], "default") == "default"
    
    def test_safe_get_empty_keys(self):
        """Test safe_get with empty key list"""
        data = {"a": 1}
        assert safe_get(data, []) == data


class TestLoadConfig:
    """Test configuration loading function"""
    
    def test_load_config_valid_file(self):
        """Test loading a valid YAML config file"""
        config_data = {
            "strategy": {
                "min_funding_diff": 0.01,
                "trade_size_usd": 100
            },
            "exchanges": {
                "backpack": {"api_key": "test_key"}
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name
        
        try:
            loaded_config = load_config(temp_path)
            assert loaded_config == config_data
        finally:
            os.unlink(temp_path)
    
    def test_load_config_file_not_found(self):
        """Test loading non-existent config file"""
        with pytest.raises(FileNotFoundError, match="配置文件不存在"):
            load_config("/non/existent/path.yaml")
    
    def test_load_config_invalid_yaml(self):
        """Test loading invalid YAML file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            temp_path = f.name
        
        try:
            with pytest.raises(yaml.YAMLError):
                load_config(temp_path)
        finally:
            os.unlink(temp_path)


class TestCalculateFundingDiff:
    """Test funding rate difference calculation"""
    
    def test_calculate_funding_diff_positive(self):
        """Test funding diff calculation with positive difference"""
        bp_funding = 0.01  # 1% for 8 hours
        hl_funding = 0.001  # 0.1% for 1 hour (0.8% for 8 hours)
        
        diff, sign = calculate_funding_diff(bp_funding, hl_funding)
        expected_diff = abs(0.01 - (0.001 * 8))  # 0.01 - 0.008 = 0.002
        
        assert abs(diff - expected_diff) < 1e-10
        assert sign == 1  # Backpack > Hyperliquid
    
    def test_calculate_funding_diff_negative(self):
        """Test funding diff calculation with negative difference"""
        bp_funding = 0.005  # 0.5% for 8 hours
        hl_funding = 0.001  # 0.1% for 1 hour (0.8% for 8 hours)
        
        diff, sign = calculate_funding_diff(bp_funding, hl_funding)
        expected_diff = abs(0.005 - (0.001 * 8))  # 0.005 - 0.008 = -0.003
        
        assert abs(diff - 0.003) < 1e-10
        assert sign == -1  # Backpack < Hyperliquid
    
    def test_calculate_funding_diff_zero(self):
        """Test funding diff calculation with zero difference"""
        bp_funding = 0.008  # 0.8% for 8 hours
        hl_funding = 0.001  # 0.1% for 1 hour (0.8% for 8 hours)
        
        diff, sign = calculate_funding_diff(bp_funding, hl_funding)
        
        assert abs(diff) < 1e-10
        assert sign == 0
    
    def test_calculate_funding_diff_negative_rates(self):
        """Test funding diff calculation with negative rates"""
        bp_funding = -0.005  # -0.5% for 8 hours
        hl_funding = -0.001  # -0.1% for 1 hour (-0.8% for 8 hours)
        
        diff, sign = calculate_funding_diff(bp_funding, hl_funding)
        expected_diff = abs(-0.005 - (-0.001 * 8))  # -0.005 - (-0.008) = 0.003
        
        assert abs(diff - 0.003) < 1e-10
        assert sign == 1  # -0.005 > -0.008


class TestConvertExchangePositions:
    """Test exchange position conversion function"""
    
    def test_convert_positions_both_exchanges(self):
        """Test converting positions from both exchanges"""
        bp_positions = {
            "BTC_USDC_PERP": {"size": 0.1, "side": "BUY"},
            "ETH_USDC_PERP": {"size": 1.0, "side": "SELL"}
        }
        hl_positions = {
            "BTC": {"size": 0.1, "side": "SELL"},
            "SOL": {"size": 10.0, "side": "BUY"}
        }
        
        result = convert_exchange_positions_to_local(bp_positions, hl_positions)
        
        # Check BTC position (exists in both exchanges)
        assert "BTC" in result
        assert result["BTC"]["bp_symbol"] == "BTC_USDC_PERP"
        assert result["BTC"]["bp_side"] == "BUY"
        assert result["BTC"]["bp_size"] == 0.1
        assert result["BTC"]["hl_symbol"] == "BTC"
        assert result["BTC"]["hl_side"] == "SELL"
        assert result["BTC"]["hl_size"] == 0.1
        
        # Check ETH position (only in Backpack)
        assert "ETH" in result
        assert result["ETH"]["bp_symbol"] == "ETH_USDC_PERP"
        assert result["ETH"]["bp_side"] == "SELL"
        assert result["ETH"]["bp_size"] == 1.0
        assert "hl_symbol" not in result["ETH"]
        
        # Check SOL position (only in Hyperliquid)
        assert "SOL" in result
        assert result["SOL"]["hl_symbol"] == "SOL"
        assert result["SOL"]["hl_side"] == "BUY"
        assert result["SOL"]["hl_size"] == 10.0
        assert "bp_symbol" not in result["SOL"]
        
        # Check that funding rate defaults are set
        for symbol in result:
            assert "entry_bp_funding" in result[symbol]
            assert "entry_hl_funding" in result[symbol]
            assert "entry_funding_diff_sign" in result[symbol]
            assert "entry_time" in result[symbol]
    
    def test_convert_positions_empty(self):
        """Test converting empty positions"""
        result = convert_exchange_positions_to_local({}, {})
        assert result == {}
    
    def test_convert_positions_invalid_symbols(self):
        """Test converting positions with invalid symbols"""
        bp_positions = {"INVALID": {"size": 0.1, "side": "BUY"}}
        hl_positions = {}
        
        result = convert_exchange_positions_to_local(bp_positions, hl_positions)
        # The function doesn't filter invalid symbols, it processes them as-is
        assert "INVALID" in result
        assert result["INVALID"]["bp_symbol"] == "INVALID"
        assert result["INVALID"]["bp_side"] == "BUY"
        assert result["INVALID"]["bp_size"] == 0.1


class TestConfigureLogging:
    """Test logging configuration function"""
    
    def test_configure_logging_basic(self):
        """Test basic logging configuration"""
        logger = configure_logging("test_logger", "INFO")
        
        assert logger.name == "test_logger"
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 1  # Console handler
        assert isinstance(logger.handlers[0], logging.StreamHandler)
    
    def test_configure_logging_with_file(self):
        """Test logging configuration with file output"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            log_file = f.name
        
        try:
            logger = configure_logging("test_logger", "DEBUG", log_file)
            
            assert logger.level == logging.DEBUG
            assert len(logger.handlers) == 2  # Console + File handlers
            
            # Test that we can write to the log
            logger.info("Test message")
            
            # Check that log file was created and contains content
            assert os.path.exists(log_file)
            with open(log_file, 'r') as f:
                content = f.read()
                assert "Test message" in content
        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)
    
    def test_configure_logging_quiet_loggers(self):
        """Test logging configuration with quiet loggers"""
        quiet_loggers = ["noisy_logger1", "noisy_logger2"]
        configure_logging("test_logger", "INFO", quiet_loggers=quiet_loggers)
        
        for logger_name in quiet_loggers:
            quiet_logger = logging.getLogger(logger_name)
            assert quiet_logger.level == logging.ERROR


class TestRoundToTick:
    """Test tick rounding function"""
    
    def test_round_to_tick_basic(self):
        """Test basic tick rounding"""
        assert round_to_tick(1.234, 0.01) == 1.23
        assert round_to_tick(1.236, 0.01) == 1.24
        assert round_to_tick(1.235, 0.01) == 1.24  # Round half up
    
    def test_round_to_tick_different_sizes(self):
        """Test tick rounding with different tick sizes"""
        assert abs(round_to_tick(1.234, 0.1) - 1.2) < 1e-10
        assert round_to_tick(1.234, 0.001) == 1.234
        assert round_to_tick(1.2345, 0.001) == 1.234  # Banker's rounding: round half to even
        assert round_to_tick(1.2355, 0.001) == 1.236  # This should round up
        assert round_to_tick(123.456, 1.0) == 123.0
        assert round_to_tick(123.6, 1.0) == 124.0
    
    def test_round_to_tick_zero_value(self):
        """Test tick rounding with zero value"""
        assert round_to_tick(0.0, 0.01) == 0.0
        assert round_to_tick(0.0, 1.0) == 0.0
    
    def test_round_to_tick_negative_value(self):
        """Test tick rounding with negative values"""
        assert round_to_tick(-1.234, 0.01) == -1.23
        assert round_to_tick(-1.236, 0.01) == -1.24


class TestFormatNumber:
    """Test number formatting function"""
    
    def test_format_number_basic(self):
        """Test basic number formatting"""
        assert format_number(1.23456, 2) == "1.23"
        assert format_number(1.23956, 2) == "1.24"
        assert format_number(1.0, 2) == "1.00"
    
    def test_format_number_different_precisions(self):
        """Test number formatting with different precisions"""
        value = 1.23456789
        assert format_number(value, 0) == "1"
        assert format_number(value, 1) == "1.2"
        assert format_number(value, 3) == "1.235"
        assert format_number(value, 6) == "1.234568"
    
    def test_format_number_zero(self):
        """Test formatting zero"""
        assert format_number(0.0, 2) == "0.00"
        assert format_number(0.0, 0) == "0"
    
    def test_format_number_negative(self):
        """Test formatting negative numbers"""
        assert format_number(-1.23456, 2) == "-1.23"
        assert format_number(-0.001, 3) == "-0.001"


if __name__ == "__main__":
    pytest.main([__file__])