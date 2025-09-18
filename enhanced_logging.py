# enhanced_logging.py
"""
Enhanced Logging and Error Handling Module
Provides comprehensive logging, error tracking, and monitoring capabilities
"""

import logging
import json
import os
import sys
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from functools import wraps
from enum import Enum
import csv


class LogLevel(Enum):
    """Log levels for different types of operations"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ScrapingOperation(Enum):
    """Types of scraping operations for categorized logging"""
    URL_FETCH = "url_fetch"
    PRICE_EXTRACTION = "price_extraction"
    DIMENSION_EXTRACTION = "dimension_extraction"
    MANUAL_ASSISTANCE = "manual_assistance"
    DATA_VALIDATION = "data_validation"
    EXPORT = "export"
    SEARCH = "search"


class EnhancedLogger:
    """
    Enhanced logging system for the scraper with detailed error tracking
    """
    
    def __init__(self, name: str = "oak_scraper", log_dir: str = "logs"):
        """
        Initialize enhanced logger
        
        Args:
            name: Logger name
            log_dir: Directory to store log files
        """
        self.name = name
        self.log_dir = log_dir
        self.error_log: List[Dict] = []
        self.session_stats: Dict[str, Any] = {
            'start_time': datetime.now(),
            'operations': {},
            'errors_by_type': {},
            'successful_operations': 0,
            'failed_operations': 0
        }
        
        # Create log directory
        os.makedirs(log_dir, exist_ok=True)
        
        # Setup loggers
        self.setup_loggers()
        
    def setup_loggers(self):
        """Setup multiple loggers for different purposes"""
        # Main logger
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler for all logs
        log_file = os.path.join(self.log_dir, f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Error-only file handler
        error_file = os.path.join(self.log_dir, f"{self.name}_errors_{datetime.now().strftime('%Y%m%d')}.log")
        error_handler = logging.FileHandler(error_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        self.logger.addHandler(error_handler)
        
    def log_operation(self, operation: ScrapingOperation, message: str, 
                     level: LogLevel = LogLevel.INFO, url: str = None, 
                     additional_data: Dict = None):
        """
        Log a scraping operation with categorization
        
        Args:
            operation: Type of operation
            message: Log message
            level: Log level
            url: URL being processed (if applicable)
            additional_data: Additional context data
        """
        # Update session stats
        op_key = operation.value
        if op_key not in self.session_stats['operations']:
            self.session_stats['operations'][op_key] = {'count': 0, 'errors': 0}
        
        self.session_stats['operations'][op_key]['count'] += 1
        
        # Create log entry
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation.value,
            'level': level.value,
            'message': message,
            'url': url
        }
        
        if additional_data:
            log_entry.update(additional_data)
        
        # Log to appropriate level
        log_message = f"[{operation.value.upper()}] {message}"
        if url:
            log_message += f" (URL: {url})"
            
        if level == LogLevel.DEBUG:
            self.logger.debug(log_message)
        elif level == LogLevel.INFO:
            self.logger.info(log_message)
        elif level == LogLevel.WARNING:
            self.logger.warning(log_message)
        elif level == LogLevel.ERROR:
            self.logger.error(log_message)
            self._track_error(operation, message, url, additional_data)
        elif level == LogLevel.CRITICAL:
            self.logger.critical(log_message)
            self._track_error(operation, message, url, additional_data)
            
    def _track_error(self, operation: ScrapingOperation, message: str, 
                    url: str = None, additional_data: Dict = None):
        """Track errors for analysis"""
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation.value,
            'message': message,
            'url': url,
            'traceback': traceback.format_exc() if sys.exc_info()[0] else None
        }
        
        if additional_data:
            error_entry.update(additional_data)
            
        self.error_log.append(error_entry)
        
        # Update stats
        self.session_stats['failed_operations'] += 1
        op_key = operation.value
        if op_key in self.session_stats['operations']:
            self.session_stats['operations'][op_key]['errors'] += 1
            
        error_type = additional_data.get('error_type', 'unknown') if additional_data else 'unknown'
        if error_type not in self.session_stats['errors_by_type']:
            self.session_stats['errors_by_type'][error_type] = 0
        self.session_stats['errors_by_type'][error_type] += 1
        
    def log_success(self, operation: ScrapingOperation, message: str, 
                   url: str = None, additional_data: Dict = None):
        """Log successful operation"""
        self.session_stats['successful_operations'] += 1
        self.log_operation(operation, message, LogLevel.INFO, url, additional_data)
        
    def log_manual_intervention(self, operation: ScrapingOperation, url: str, 
                              reason: str, user_input: str = None):
        """Log manual intervention cases"""
        data = {
            'intervention_reason': reason,
            'user_input': user_input,
            'requires_attention': True
        }
        self.log_operation(operation, f"Manual intervention required: {reason}", 
                         LogLevel.WARNING, url, data)
        
    def log_data_quality_issue(self, url: str, field: str, issue: str, 
                             extracted_value: Any = None):
        """Log data quality issues"""
        data = {
            'field': field,
            'issue': issue,
            'extracted_value': str(extracted_value) if extracted_value else None,
            'data_quality_flag': True
        }
        self.log_operation(ScrapingOperation.DATA_VALIDATION, 
                         f"Data quality issue in {field}: {issue}", 
                         LogLevel.WARNING, url, data)
        
    def get_session_summary(self) -> Dict:
        """Get summary of current session"""
        duration = datetime.now() - self.session_stats['start_time']
        
        summary = {
            'session_duration': str(duration),
            'total_operations': self.session_stats['successful_operations'] + self.session_stats['failed_operations'],
            'successful_operations': self.session_stats['successful_operations'],
            'failed_operations': self.session_stats['failed_operations'],
            'success_rate': self._calculate_success_rate(),
            'operations_breakdown': self.session_stats['operations'],
            'errors_by_type': self.session_stats['errors_by_type'],
            'total_errors': len(self.error_log)
        }
        
        return summary
        
    def _calculate_success_rate(self) -> float:
        """Calculate overall success rate"""
        total = self.session_stats['successful_operations'] + self.session_stats['failed_operations']
        if total == 0:
            return 0.0
        return round((self.session_stats['successful_operations'] / total) * 100, 2)
        
    def save_session_report(self, filename: str = None):
        """Save detailed session report"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(self.log_dir, f"session_report_{timestamp}.json")
            
        report = {
            'session_summary': self.get_session_summary(),
            'error_log': self.error_log,
            'session_stats': self.session_stats
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            self.logger.info(f"Session report saved to {filename}")
        except Exception as e:
            self.logger.error(f"Failed to save session report: {e}")
            
    def export_errors_csv(self, filename: str = None):
        """Export errors to CSV for analysis"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(self.log_dir, f"errors_{timestamp}.csv")
            
        if not self.error_log:
            self.logger.info("No errors to export")
            return
            
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['timestamp', 'operation', 'message', 'url', 'error_type']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                writer.writeheader()
                for error in self.error_log:
                    row = {
                        'timestamp': error['timestamp'],
                        'operation': error['operation'],
                        'message': error['message'],
                        'url': error.get('url', ''),
                        'error_type': error.get('error_type', 'unknown')
                    }
                    writer.writerow(row)
                    
            self.logger.info(f"Errors exported to {filename}")
        except Exception as e:
            self.logger.error(f"Failed to export errors: {e}")
            
    def get_problematic_urls(self, min_error_count: int = 2) -> List[Dict]:
        """Get URLs that have had multiple errors"""
        url_errors = {}
        
        for error in self.error_log:
            url = error.get('url')
            if url:
                if url not in url_errors:
                    url_errors[url] = []
                url_errors[url].append(error)
                
        problematic = [
            {'url': url, 'error_count': len(errors), 'errors': errors}
            for url, errors in url_errors.items()
            if len(errors) >= min_error_count
        ]
        
        return sorted(problematic, key=lambda x: x['error_count'], reverse=True)
        
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """Clean up old log files"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        try:
            for filename in os.listdir(self.log_dir):
                if filename.endswith('.log') or filename.endswith('.json'):
                    filepath = os.path.join(self.log_dir, filename)
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    
                    if file_time < cutoff_date:
                        os.remove(filepath)
                        self.logger.info(f"Cleaned up old log file: {filename}")
                        
        except Exception as e:
            self.logger.error(f"Error cleaning up logs: {e}")


def with_logging(operation: ScrapingOperation, logger_instance: EnhancedLogger = None):
    """
    Decorator to automatically log function calls and exceptions
    
    Args:
        operation: Type of operation being logged
        logger_instance: Logger instance to use
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get logger instance
            if logger_instance:
                logger = logger_instance
            else:
                logger = get_default_logger()
                
            # Extract URL from arguments if present
            url = kwargs.get('url')
            if not url and args:
                # Try to find URL in first few arguments
                for arg in args[:3]:
                    if isinstance(arg, str) and arg.startswith(('http://', 'https://')):
                        url = arg
                        break
                        
            try:
                logger.log_operation(operation, f"Starting {func.__name__}", 
                                   LogLevel.DEBUG, url)
                
                result = func(*args, **kwargs)
                
                logger.log_success(operation, f"Completed {func.__name__}", url)
                return result
                
            except Exception as e:
                error_data = {
                    'error_type': type(e).__name__,
                    'function': func.__name__
                }
                logger.log_operation(operation, f"Error in {func.__name__}: {str(e)}", 
                                   LogLevel.ERROR, url, error_data)
                raise
                
        return wrapper
    return decorator


# Global logger instance
_default_logger = None


def get_default_logger() -> EnhancedLogger:
    """Get the default logger instance"""
    global _default_logger
    if _default_logger is None:
        _default_logger = EnhancedLogger()
    return _default_logger


def setup_logging(name: str = "oak_scraper", log_dir: str = "logs") -> EnhancedLogger:
    """Setup and return a new logger instance"""
    return EnhancedLogger(name, log_dir)


if __name__ == "__main__":
    # Example usage and testing
    print("Enhanced Logging Module - Testing")
    print("=" * 40)
    
    logger = EnhancedLogger("test_scraper")
    
    # Test different log operations
    logger.log_operation(ScrapingOperation.URL_FETCH, "Testing URL fetch", 
                        LogLevel.INFO, "https://example.com")
    
    logger.log_success(ScrapingOperation.PRICE_EXTRACTION, "Successfully extracted price", 
                      "https://example.com", {'price': '£299.99'})
    
    logger.log_operation(ScrapingOperation.DIMENSION_EXTRACTION, "Failed to extract dimensions", 
                        LogLevel.ERROR, "https://example.com", 
                        {'error_type': 'PatternNotFound'})
    
    logger.log_manual_intervention(ScrapingOperation.MANUAL_ASSISTANCE, 
                                  "https://example.com", 
                                  "Price extraction failed", "£150")
    
    logger.log_data_quality_issue("https://example.com", "dimensions", 
                                 "Unrealistic measurements", "5000x5000x5000")
    
    # Show session summary
    summary = logger.get_session_summary()
    print(f"\nSession Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Save reports
    logger.save_session_report()
    logger.export_errors_csv()
    
    print(f"\nProblematic URLs: {logger.get_problematic_urls()}")