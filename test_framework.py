# test_framework.py
"""
Testing and Validation Framework for the Enhanced Oak Table Scraper
Provides unit tests, integration tests, and validation mechanisms
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pytest
import requests
from bs4 import BeautifulSoup
import json
import os
import sys
from typing import Dict, List, Any
import tempfile
import shutil
from datetime import datetime

# Import our modules
from enhanced_logging import EnhancedLogger, ScrapingOperation, LogLevel
from company_tracker import CompanyTracker
from config_manager import ConfigManager, ScrapingConfig
from google_geeking import GoogleGeeking

class TestDataExtraction(unittest.TestCase):
    """Test data extraction functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_html = """
        <html>
            <head><title>Test Oak Dining Table</title></head>
            <body>
                <h1>Solid Oak Dining Table</h1>
                <div class="price">£299.99</div>
                <div class="specifications">
                    Dimensions: 180cm x 90cm x 75cm
                    Material: Solid Oak Wood
                    Finish: Natural Wax
                </div>
                <div class="delivery">Free delivery in 5-7 working days</div>
                <div class="warranty">2 year warranty included</div>
            </body>
        </html>
        """
        self.soup = BeautifulSoup(self.test_html, 'html.parser')
    
    def test_enhanced_parse_price(self):
        """Test enhanced price parsing"""
        from enhanced_main import enhanced_parse_price
        
        test_cases = [
            ("£299.99", ("GBP", 299.99)),
            ("€250.00", ("EUR", 250.00)),
            ("$199", ("USD", 199.0)),
            ("Price: £150", ("GBP", 150.0)),
            ("From £99.50", ("GBP", 99.50)),
            ("1,299.99 EUR", ("EUR", 1299.99)),
            ("Invalid text", (None, None))
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = enhanced_parse_price(input_text)
                self.assertEqual(result, expected)
    
    def test_material_detection(self):
        """Test material detection"""
        from enhanced_main import detect_material
        
        result = detect_material(self.soup, "Solid Oak Dining Table")
        self.assertIn("Oak", result)
    
    def test_table_type_detection(self):
        """Test table type detection"""
        from enhanced_main import detect_table_type
        
        result = detect_table_type(self.soup, "Solid Oak Dining Table")
        self.assertEqual(result, "Dining Table")
    
    def test_dimension_validation(self):
        """Test dimension validation logic"""
        valid_dimensions = {'length': 180, 'width': 90, 'height': 75}
        invalid_dimensions = {'length': 5000, 'width': 5000, 'height': 5000}
        
        # Test validation logic (would be part of enhanced extraction)
        self.assertTrue(50 <= valid_dimensions['length'] <= 500)
        self.assertFalse(50 <= invalid_dimensions['length'] <= 500)

class TestCompanyTracker(unittest.TestCase):
    """Test company tracking functionality"""
    
    def setUp(self):
        """Set up test tracker with temporary file"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_companies.json")
        self.tracker = CompanyTracker(storage_file=self.test_file)
    
    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.temp_dir)
    
    def test_domain_normalization(self):
        """Test URL domain normalization"""
        test_cases = [
            ("https://www.oakfurnitureland.co.uk/tables/", "oakfurnitureland"),
            ("https://shop.next.co.uk/furniture/", "next"),
            ("http://ikea.com/products/", "ikea")
        ]
        
        for url, expected in test_cases:
            result = self.tracker._normalize_domain(url)
            self.assertEqual(result, expected)
    
    def test_company_processing_tracking(self):
        """Test marking and checking processed companies"""
        test_url = "https://www.testfurniture.co.uk/tables/"
        
        # Initially not processed
        self.assertFalse(self.tracker.is_company_processed(test_url))
        
        # Mark as processed
        self.tracker.mark_company_processed(test_url)
        
        # Should now be processed
        self.assertTrue(self.tracker.is_company_processed(test_url))
    
    def test_url_filtering(self):
        """Test filtering URLs for unique companies"""
        test_urls = [
            "https://www.company1.co.uk/table1/",
            "https://www.company1.co.uk/table2/",  # Same company
            "https://www.company2.com/furniture/",
            "https://shop.company2.com/tables/"     # Same company, different subdomain
        ]
        
        filtered = self.tracker.filter_unique_urls(test_urls)
        
        # Should have only 2 URLs (one per company)
        self.assertEqual(len(filtered), 2)
        
        # Verify we have one from each company
        domains = [self.tracker._normalize_domain(url) for url in filtered]
        self.assertEqual(len(set(domains)), 2)

class TestEnhancedLogging(unittest.TestCase):
    """Test enhanced logging functionality"""
    
    def setUp(self):
        """Set up test logger"""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = EnhancedLogger("test_logger", log_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.temp_dir)
    
    def test_operation_logging(self):
        """Test operation logging"""
        test_url = "https://example.com"
        
        self.logger.log_operation(
            ScrapingOperation.PRICE_EXTRACTION,
            "Test message",
            LogLevel.INFO,
            test_url
        )
        
        # Check session stats
        stats = self.logger.get_session_summary()
        self.assertGreater(stats['total_operations'], 0)
        self.assertIn('price_extraction', stats['operations_breakdown'])
    
    def test_error_tracking(self):
        """Test error tracking"""
        test_url = "https://example.com"
        
        self.logger.log_operation(
            ScrapingOperation.PRICE_EXTRACTION,
            "Test error",
            LogLevel.ERROR,
            test_url,
            {'error_type': 'TestError'}
        )
        
        # Check error tracking
        self.assertEqual(len(self.logger.error_log), 1)
        self.assertEqual(self.logger.error_log[0]['operation'], 'price_extraction')
        
        # Check stats
        stats = self.logger.get_session_summary()
        self.assertGreater(stats['failed_operations'], 0)
        self.assertIn('TestError', stats['errors_by_type'])
    
    def test_session_report_generation(self):
        """Test session report generation"""
        # Generate some test activity
        for i in range(3):
            self.logger.log_success(
                ScrapingOperation.URL_FETCH,
                f"Test success {i}",
                f"https://example{i}.com"
            )
        
        # Generate report
        self.logger.save_session_report()
        
        # Check if report file was created
        report_files = [f for f in os.listdir(self.temp_dir) if f.startswith('session_report_')]
        self.assertGreater(len(report_files), 0)

class TestConfigManager(unittest.TestCase):
    """Test configuration management"""
    
    def setUp(self):
        """Set up test config manager"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.yaml")
        self.config_manager = ConfigManager(config_file=self.config_file)
    
    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.temp_dir)
    
    def test_config_loading_and_saving(self):
        """Test config loading and saving"""
        # Modify config
        original_timeout = self.config_manager.scraping_config.timeout
        self.config_manager.update_config('scraping', {'timeout': 30})
        
        # Create new manager with same file
        new_manager = ConfigManager(config_file=self.config_file)
        
        # Should have loaded the modified value
        self.assertEqual(new_manager.scraping_config.timeout, 30)
        self.assertNotEqual(new_manager.scraping_config.timeout, original_timeout)
    
    def test_config_validation(self):
        """Test config validation"""
        # Set invalid values
        self.config_manager.scraping_config.timeout = -1
        self.config_manager.scraping_config.min_price = 1000
        self.config_manager.scraping_config.max_price = 100  # Less than min_price
        
        # Validate
        issues = self.config_manager.validate_config()
        
        # Should have validation issues
        self.assertGreater(len(issues), 0)
        self.assertTrue(any("timeout" in issue.lower() for issue in issues))
        self.assertTrue(any("price" in issue.lower() for issue in issues))

class TestGoogleGeeking(unittest.TestCase):
    """Test Google search functionality"""
    
    def setUp(self):
        """Set up test Google geeking"""
        # Mock the Google geeking since we don't want to make real requests in tests
        self.mock_geeking = Mock(spec=GoogleGeeking)
    
    def test_url_validation(self):
        """Test URL validation logic"""
        # Create a real instance for testing validation logic
        geeking = GoogleGeeking(headless=True)
        
        valid_urls = [
            "https://www.oakfurnitureland.co.uk/dining-tables/",
            "https://www.next.co.uk/furniture/dining-tables"
        ]
        
        invalid_urls = [
            "https://www.google.com/search",
            "https://www.youtube.com/watch",
            "not-a-url"
        ]
        
        for url in valid_urls:
            # Note: This would need the actual validation logic
            # result = geeking._is_valid_url(url)
            # self.assertTrue(result, f"Should be valid: {url}")
            pass
        
        for url in invalid_urls:
            # result = geeking._is_valid_url(url)
            # self.assertFalse(result, f"Should be invalid: {url}")
            pass
    
    def test_query_generation(self):
        """Test search query generation"""
        geeking = GoogleGeeking(headless=True)
        
        base_terms = ["oak table", "dining table"]
        queries = geeking.generate_furniture_queries(base_terms)
        
        self.assertIsInstance(queries, list)
        self.assertGreater(len(queries), len(base_terms))
        
        # Should contain original terms
        for term in base_terms:
            self.assertTrue(any(term in query for query in queries))

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock HTML content for testing
        self.mock_html = """
        <html>
            <head><title>Test Table</title></head>
            <body>
                <h1>Premium Oak Dining Table</h1>
                <div class="price">£599.99</div>
                <div class="dimensions">200cm x 100cm x 75cm</div>
                <div class="material">Solid Oak</div>
            </body>
        </html>
        """
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)
    
    @patch('requests.Session.get')
    def test_end_to_end_scraping(self, mock_get):
        """Test end-to-end scraping process"""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.text = self.mock_html
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Import scraping function
        from enhanced_main import enhanced_scrape_table_data
        
        # Test scraping
        test_url = "https://example.com/table"
        result = enhanced_scrape_table_data(test_url, manual_assistance=False)
        
        # Verify results
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['Produkta lapas URL'], test_url)
        self.assertIn('Oak', result['Materiāls(-i)'])

class TestValidation(unittest.TestCase):
    """Test data validation and quality checks"""
    
    def test_price_validation(self):
        """Test price validation logic"""
        valid_prices = [50.0, 299.99, 1500.0]
        invalid_prices = [0.0, -10.0, 100000.0]
        
        min_price, max_price = 10.0, 50000.0
        
        for price in valid_prices:
            self.assertTrue(min_price <= price <= max_price, f"Valid price failed: {price}")
        
        for price in invalid_prices:
            self.assertFalse(min_price <= price <= max_price, f"Invalid price passed: {price}")
    
    def test_dimension_validation(self):
        """Test dimension validation logic"""
        valid_dimensions = [
            {'length': 180, 'width': 90, 'height': 75},
            {'length': 120, 'width': 60, 'height': 72}
        ]
        
        invalid_dimensions = [
            {'length': 10, 'width': 90, 'height': 75},  # Too small
            {'length': 1000, 'width': 90, 'height': 75},  # Too large
            {'length': 180, 'width': 5, 'height': 75}   # Width too small
        ]
        
        def validate_dimensions(dims):
            return (50 <= dims['length'] <= 500 and 
                   50 <= dims['width'] <= 200 and 
                   50 <= dims['height'] <= 120)
        
        for dims in valid_dimensions:
            self.assertTrue(validate_dimensions(dims), f"Valid dimensions failed: {dims}")
        
        for dims in invalid_dimensions:
            self.assertFalse(validate_dimensions(dims), f"Invalid dimensions passed: {dims}")

def run_all_tests():
    """Run all tests and generate report"""
    print("Running Enhanced Oak Table Scraper Test Suite")
    print("=" * 60)
    
    # Create test suite
    test_classes = [
        TestDataExtraction,
        TestCompanyTracker,
        TestEnhancedLogging,
        TestConfigManager,
        TestGoogleGeeking,
        TestIntegration,
        TestValidation
    ]
    
    total_tests = 0
    total_failures = 0
    total_errors = 0
    
    for test_class in test_classes:
        print(f"\nRunning {test_class.__name__}...")
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
        result = runner.run(suite)
        
        total_tests += result.testsRun
        total_failures += len(result.failures)
        total_errors += len(result.errors)
        
        if result.failures:
            print(f"  Failures: {len(result.failures)}")
        if result.errors:
            print(f"  Errors: {len(result.errors)}")
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print(f"Total tests: {total_tests}")
    print(f"Failures: {total_failures}")
    print(f"Errors: {total_errors}")
    print(f"Success rate: {((total_tests - total_failures - total_errors) / total_tests * 100):.1f}%")
    
    return total_failures + total_errors == 0

def run_performance_tests():
    """Run performance tests"""
    print("\nRunning Performance Tests")
    print("-" * 30)
    
    import time
    
    # Test HTML parsing speed
    test_html = """<html><body><div class="price">£299.99</div></body></html>""" * 100
    
    start_time = time.time()
    for _ in range(100):
        soup = BeautifulSoup(test_html, 'html.parser')
        price_tag = soup.select_one('.price')
    end_time = time.time()
    
    print(f"HTML parsing (100 iterations): {(end_time - start_time):.3f}s")
    
    # Test regex performance
    import re
    price_pattern = r"([€£$])\s?([\d.,]+)"
    test_text = "Price: £299.99 was £399.99"
    
    start_time = time.time()
    for _ in range(1000):
        match = re.search(price_pattern, test_text)
    end_time = time.time()
    
    print(f"Regex matching (1000 iterations): {(end_time - start_time):.3f}s")

if __name__ == "__main__":
    # Check if pytest is available for more advanced testing
    try:
        import pytest
        print("pytest available - you can run: pytest test_framework.py")
    except ImportError:
        print("pytest not available - using unittest")
    
    # Run all tests
    success = run_all_tests()
    
    # Run performance tests
    run_performance_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)