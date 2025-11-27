import unittest
import os
import tempfile
import csv
from sales_analysis import SalesData, SalesAnalyzer


class TestSalesData(unittest.TestCase):
    # Tests for the SalesData class

    def test_sales_data_creation(self):
        # Test creating a SalesData object from dict
        record = {
            'Order ID': '1001',
            'Product': 'Laptop',
            'Category': 'Electronics',
            'Quantity': '2',
            'Unit Price': '999.99',
            'Total Price': '1999.98',
            'Order Date': '2024-01-15',
            'Region': 'North',
            'Customer ID': 'C001',
            'Payment Method': 'Credit Card'
        }
        sale = SalesData(record)
        self.assertEqual(sale.order_id, 1001)
        self.assertEqual(sale.product, 'Laptop')
        self.assertEqual(sale.category, 'Electronics')
        self.assertEqual(sale.quantity, 2)
        self.assertAlmostEqual(sale.unit_price, 999.99, places=2)
        self.assertAlmostEqual(sale.total_price, 1999.98, places=2)
        self.assertEqual(sale.region, 'North')
        self.assertEqual(sale.customer_id, 'C001')
        self.assertEqual(sale.payment_method, 'Credit Card')


class TestSalesAnalyzerBase(unittest.TestCase):
    # Base test class with sample data setup

    @classmethod
    def setUpClass(cls):
        # Create temporary CSV file for testing
        cls.temp_dir = tempfile.mkdtemp()
        cls.csv_path = os.path.join(cls.temp_dir, 'test_sales.csv')

        test_data = [
            ['Order ID', 'Product', 'Category', 'Quantity', 'Unit Price', 'Total Price', 'Order Date', 'Region', 'Customer ID', 'Payment Method'],
            ['1', 'Laptop', 'Electronics', '2', '1000', '2000', '2024-01-15', 'North', 'C001', 'Credit Card'],
            ['2', 'Chair', 'Furniture', '5', '100', '500', '2024-01-16', 'South', 'C002', 'PayPal'],
            ['3', 'Mouse', 'Electronics', '10', '25', '250', '2024-01-17', 'North', 'C001', 'Credit Card'],
            ['4', 'Desk', 'Furniture', '1', '300', '300', '2024-02-01', 'East', 'C003', 'Debit Card'],
            ['5', 'Monitor', 'Electronics', '3', '400', '1200', '2024-02-15', 'South', 'C004', 'PayPal'],
        ]

        with open(cls.csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(test_data)

        cls.analyzer = SalesAnalyzer(cls.csv_path)

    @classmethod
    def tearDownClass(cls):
        # Clean up temp files
        os.remove(cls.csv_path)
        os.rmdir(cls.temp_dir)


class TestSalesAnalyzerBasicOperations(TestSalesAnalyzerBase):
    # Tests for basic analysis operations

    def test_data_loading(self):
        # Test that data is loaded correctly
        self.assertEqual(len(self.analyzer.data), 5)

    def test_total_revenue(self):
        # Test total revenue calculation
        expected = 2000 + 500 + 250 + 300 + 1200
        self.assertAlmostEqual(self.analyzer.total_revenue(), expected, places=2)

    def test_average_order_value(self):
        # Test average order value calculation
        total = 2000 + 500 + 250 + 300 + 1200
        expected_avg = total / 5
        self.assertAlmostEqual(self.analyzer.average_order_value(), expected_avg, places=2)


class TestSalesAnalyzerGrouping(TestSalesAnalyzerBase):
    # Tests for grouping operations

    def test_revenue_by_category(self):
        # Test revenue grouping by category
        result = self.analyzer.revenue_by_category()
        self.assertIn('Electronics', result)
        self.assertIn('Furniture', result)
        self.assertAlmostEqual(result['Electronics'], 3450, places=2)
        self.assertAlmostEqual(result['Furniture'], 800, places=2)

    def test_revenue_by_region(self):
        # Test revenue grouping by region
        result = self.analyzer.revenue_by_region()
        self.assertIn('North', result)
        self.assertIn('South', result)
        self.assertIn('East', result)

    def test_orders_by_payment_method(self):
        # Test order count by payment method
        result = self.analyzer.orders_by_payment_method()
        self.assertEqual(result['Credit Card'], 2)
        self.assertEqual(result['PayPal'], 2)
        self.assertEqual(result['Debit Card'], 1)


class TestSalesAnalyzerTopItems(TestSalesAnalyzerBase):
    # Tests for top items analysis

    def test_top_products_by_revenue(self):
        # Test getting top products
        result = self.analyzer.top_products_by_revenue(3)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0][0], 'Laptop')
        self.assertAlmostEqual(result[0][1], 2000, places=2)

    def test_top_customers(self):
        # Test getting top customers
        result = self.analyzer.top_customers(2)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], 'C001')


class TestSalesAnalyzerMonthly(TestSalesAnalyzerBase):
    # Tests for time-based analysis

    def test_monthly_revenue(self):
        # Test monthly revenue calculation
        result = self.analyzer.monthly_revenue()
        self.assertIn('2024-01', result)
        self.assertIn('2024-02', result)
        jan_revenue = 2000 + 500 + 250
        self.assertAlmostEqual(result['2024-01'], jan_revenue, places=2)


class TestSalesAnalyzerFiltering(TestSalesAnalyzerBase):
    # Tests for filtering operations

    def test_filter_by_category(self):
        # Test filtering by category
        electronics = self.analyzer.filter_sales(lambda s: s.category == 'Electronics')
        self.assertEqual(len(electronics), 3)

    def test_filter_by_price(self):
        # Test filtering by price threshold
        expensive = self.analyzer.filter_sales(lambda s: s.total_price > 500)
        self.assertEqual(len(expensive), 2)

    def test_filter_by_region(self):
        # Test filtering by region
        north = self.analyzer.filter_sales(lambda s: s.region == 'North')
        self.assertEqual(len(north), 2)


class TestSalesAnalyzerMapping(TestSalesAnalyzerBase):
    # Tests for mapping operations

    def test_map_to_prices(self):
        # Test mapping to prices
        prices = self.analyzer.map_sales(lambda s: s.total_price)
        self.assertEqual(len(prices), 5)
        self.assertIn(2000, prices)

    def test_map_to_products(self):
        # Test mapping to product names
        products = self.analyzer.map_sales(lambda s: s.product)
        self.assertEqual(len(products), 5)
        self.assertIn('Laptop', products)


class TestSalesAnalyzerStatistics(TestSalesAnalyzerBase):
    # Tests for statistics methods

    def test_get_statistics(self):
        # Test statistics dictionary
        stats = self.analyzer.get_statistics()
        self.assertEqual(stats['total_orders'], 5)
        self.assertEqual(stats['unique_products'], 5)
        self.assertIn('total_revenue', stats)
        self.assertIn('average_order_value', stats)

    def test_category_breakdown(self):
        # Test category breakdown
        breakdown = self.analyzer.category_breakdown()
        self.assertIn('Electronics', breakdown)
        self.assertIn('Furniture', breakdown)
        self.assertEqual(breakdown['Electronics']['order_count'], 3)

    def test_regional_performance(self):
        # Test regional performance
        performance = self.analyzer.regional_performance()
        self.assertIn('North', performance)
        self.assertEqual(performance['North']['order_count'], 2)


class TestSalesAnalyzerHighValue(TestSalesAnalyzerBase):
    # Tests for high value order detection

    def test_high_value_orders(self):
        # Test finding high value orders
        high_value = self.analyzer.high_value_orders(1000)
        self.assertEqual(len(high_value), 2)

    def test_high_value_orders_empty(self):
        # Test when no orders meet threshold
        high_value = self.analyzer.high_value_orders(10000)
        self.assertEqual(len(high_value), 0)


class TestSalesAnalyzerQuantity(TestSalesAnalyzerBase):
    # Tests for quantity analysis

    def test_quantity_by_product(self):
        # Test quantity breakdown by product
        result = self.analyzer.quantity_by_product()
        self.assertEqual(result['Mouse'], 10)
        self.assertEqual(result['Chair'], 5)


class TestSalesAnalyzerEmpty(unittest.TestCase):
    # Tests for edge cases with empty data

    def test_empty_data_average(self):
        # Test average with empty data
        temp_dir = tempfile.mkdtemp()
        csv_path = os.path.join(temp_dir, 'empty.csv')

        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Order ID', 'Product', 'Category', 'Quantity', 'Unit Price',
                           'Total Price', 'Order Date', 'Region', 'Customer ID', 'Payment Method'])

        analyzer = SalesAnalyzer(csv_path)
        self.assertEqual(analyzer.average_order_value(), 0.0)
        self.assertEqual(analyzer.total_revenue(), 0.0)

        os.remove(csv_path)
        os.rmdir(temp_dir)


class TestSalesAnalyzerWithRealData(unittest.TestCase):
    # Tests using the actual sales_data.csv file

    @classmethod
    def setUpClass(cls):
        # Load real data file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        cls.csv_path = os.path.join(script_dir, 'sales_data.csv')
        if os.path.exists(cls.csv_path):
            cls.analyzer = SalesAnalyzer(cls.csv_path)
            cls.has_real_data = True
        else:
            cls.has_real_data = False

    def test_real_data_loaded(self):
        # Test that real data file is loaded
        if not self.has_real_data:
            self.skipTest("Real data file not found")
        self.assertEqual(len(self.analyzer.data), 50)

    def test_real_data_categories(self):
        # Test categories in real data
        if not self.has_real_data:
            self.skipTest("Real data file not found")
        categories = self.analyzer.revenue_by_category()
        self.assertIn('Electronics', categories)
        self.assertIn('Furniture', categories)

    def test_real_data_regions(self):
        # Test regions in real data
        if not self.has_real_data:
            self.skipTest("Real data file not found")
        regions = self.analyzer.revenue_by_region()
        self.assertEqual(len(regions), 4)

    def test_real_data_revenue_positive(self):
        # Test that revenue is positive
        if not self.has_real_data:
            self.skipTest("Real data file not found")
        self.assertGreater(self.analyzer.total_revenue(), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
