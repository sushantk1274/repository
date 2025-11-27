import csv
from functools import reduce
from itertools import groupby
from operator import itemgetter
from typing import List, Dict, Any, Callable
from datetime import datetime
from collections import defaultdict


class SalesData:
    # Container for a single sales record
    def __init__(self, record: Dict[str, Any]):
        self.order_id = int(record['Order ID'])
        self.product = record['Product']
        self.category = record['Category']
        self.quantity = int(record['Quantity'])
        self.unit_price = float(record['Unit Price'])
        self.total_price = float(record['Total Price'])
        self.order_date = datetime.strptime(record['Order Date'], '%Y-%m-%d')
        self.region = record['Region']
        self.customer_id = record['Customer ID']
        self.payment_method = record['Payment Method']

    def __repr__(self):
        return f"SalesData({self.order_id}, {self.product}, ${self.total_price:.2f})"


class SalesAnalyzer:
    # Performs various analytical operations on sales data
    def __init__(self, csv_file_path: str):
        self.data: List[SalesData] = []
        self._load_data(csv_file_path)

    # Load and parse CSV file into SalesData objects
    def _load_data(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            self.data = list(map(lambda row: SalesData(row), reader))

    # Calculate total revenue across all sales
    def total_revenue(self) -> float:
        return reduce(lambda acc, sale: acc + sale.total_price, self.data, 0.0)

    # Calculate average order value
    def average_order_value(self) -> float:
        if not self.data:
            return 0.0
        total = self.total_revenue()
        return total / len(self.data)

    # Group sales by category and sum totals
    def revenue_by_category(self) -> Dict[str, float]:
        result = defaultdict(float)
        for sale in self.data:
            result[sale.category] += sale.total_price
        return dict(sorted(result.items(), key=lambda x: x[1], reverse=True))

    # Group sales by region and sum totals
    def revenue_by_region(self) -> Dict[str, float]:
        result = defaultdict(float)
        for sale in self.data:
            result[sale.region] += sale.total_price
        return dict(sorted(result.items(), key=lambda x: x[1], reverse=True))

    # Count orders by payment method
    def orders_by_payment_method(self) -> Dict[str, int]:
        result = defaultdict(int)
        for sale in self.data:
            result[sale.payment_method] += 1
        return dict(sorted(result.items(), key=lambda x: x[1], reverse=True))

    # Get top N products by revenue
    def top_products_by_revenue(self, n: int = 5) -> List[tuple]:
        product_revenue = defaultdict(float)
        for sale in self.data:
            product_revenue[sale.product] += sale.total_price
        sorted_products = sorted(product_revenue.items(), key=lambda x: x[1], reverse=True)
        return sorted_products[:n]

    # Get top N customers by total spending
    def top_customers(self, n: int = 5) -> List[tuple]:
        customer_spending = defaultdict(float)
        for sale in self.data:
            customer_spending[sale.customer_id] += sale.total_price
        sorted_customers = sorted(customer_spending.items(), key=lambda x: x[1], reverse=True)
        return sorted_customers[:n]

    # Calculate total quantity sold per product
    def quantity_by_product(self) -> Dict[str, int]:
        result = defaultdict(int)
        for sale in self.data:
            result[sale.product] += sale.quantity
        return dict(sorted(result.items(), key=lambda x: x[1], reverse=True))

    # Group revenue by month
    def monthly_revenue(self) -> Dict[str, float]:
        result = defaultdict(float)
        for sale in self.data:
            month_key = sale.order_date.strftime('%Y-%m')
            result[month_key] += sale.total_price
        return dict(sorted(result.items()))

    # Filter sales by custom predicate function
    def filter_sales(self, predicate: Callable[[SalesData], bool]) -> List[SalesData]:
        return list(filter(predicate, self.data))

    # Apply transformation to all sales records
    def map_sales(self, transform: Callable[[SalesData], Any]) -> List[Any]:
        return list(map(transform, self.data))

    # Get sales statistics summary
    def get_statistics(self) -> Dict[str, Any]:
        prices = self.map_sales(lambda s: s.total_price)
        quantities = self.map_sales(lambda s: s.quantity)
        return {
            'total_orders': len(self.data),
            'total_revenue': self.total_revenue(),
            'average_order_value': self.average_order_value(),
            'min_order_value': min(prices) if prices else 0,
            'max_order_value': max(prices) if prices else 0,
            'total_items_sold': sum(quantities),
            'unique_products': len(set(self.map_sales(lambda s: s.product))),
            'unique_customers': len(set(self.map_sales(lambda s: s.customer_id)))
        }

    # Get category-wise breakdown with detailed stats
    def category_breakdown(self) -> Dict[str, Dict[str, Any]]:
        categories = defaultdict(list)
        for sale in self.data:
            categories[sale.category].append(sale)

        result = {}
        for category, sales in categories.items():
            revenues = [s.total_price for s in sales]
            result[category] = {
                'order_count': len(sales),
                'total_revenue': sum(revenues),
                'avg_order_value': sum(revenues) / len(revenues),
                'min_order': min(revenues),
                'max_order': max(revenues)
            }
        return result

    # Get region-wise performance metrics
    def regional_performance(self) -> Dict[str, Dict[str, Any]]:
        regions = defaultdict(list)
        for sale in self.data:
            regions[sale.region].append(sale)

        result = {}
        for region, sales in regions.items():
            revenues = [s.total_price for s in sales]
            result[region] = {
                'order_count': len(sales),
                'total_revenue': sum(revenues),
                'avg_order_value': sum(revenues) / len(revenues),
                'unique_customers': len(set(s.customer_id for s in sales))
            }
        return result

    # Find orders above a certain value threshold
    def high_value_orders(self, threshold: float = 1000.0) -> List[SalesData]:
        return self.filter_sales(lambda s: s.total_price >= threshold)

    # Get revenue by day of week
    def revenue_by_day_of_week(self) -> Dict[str, float]:
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        result = defaultdict(float)
        for sale in self.data:
            day_name = days[sale.order_date.weekday()]
            result[day_name] += sale.total_price
        return {day: result[day] for day in days if result[day] > 0}


def print_section(title: str):
    # Print a formatted section header
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def format_currency(value: float) -> str:
    # Format number as currency
    return f"${value:,.2f}"


def run_analysis(csv_path: str):
    # Execute all analysis operations and print results
    analyzer = SalesAnalyzer(csv_path)

    print_section("SALES DATA ANALYSIS REPORT")
    print(f"Data source: {csv_path}")
    print(f"Total records loaded: {len(analyzer.data)}")

    print_section("1. OVERALL STATISTICS")
    stats = analyzer.get_statistics()
    print(f"Total Orders: {stats['total_orders']}")
    print(f"Total Revenue: {format_currency(stats['total_revenue'])}")
    print(f"Average Order Value: {format_currency(stats['average_order_value'])}")
    print(f"Min Order Value: {format_currency(stats['min_order_value'])}")
    print(f"Max Order Value: {format_currency(stats['max_order_value'])}")
    print(f"Total Items Sold: {stats['total_items_sold']}")
    print(f"Unique Products: {stats['unique_products']}")
    print(f"Unique Customers: {stats['unique_customers']}")

    print_section("2. REVENUE BY CATEGORY")
    for category, revenue in analyzer.revenue_by_category().items():
        percentage = (revenue / stats['total_revenue']) * 100
        print(f"{category}: {format_currency(revenue)} ({percentage:.1f}%)")

    print_section("3. REVENUE BY REGION")
    for region, revenue in analyzer.revenue_by_region().items():
        percentage = (revenue / stats['total_revenue']) * 100
        print(f"{region}: {format_currency(revenue)} ({percentage:.1f}%)")

    print_section("4. TOP 5 PRODUCTS BY REVENUE")
    for i, (product, revenue) in enumerate(analyzer.top_products_by_revenue(5), 1):
        print(f"{i}. {product}: {format_currency(revenue)}")

    print_section("5. TOP 5 CUSTOMERS BY SPENDING")
    for i, (customer, spending) in enumerate(analyzer.top_customers(5), 1):
        print(f"{i}. {customer}: {format_currency(spending)}")

    print_section("6. ORDERS BY PAYMENT METHOD")
    total_orders = stats['total_orders']
    for method, count in analyzer.orders_by_payment_method().items():
        percentage = (count / total_orders) * 100
        print(f"{method}: {count} orders ({percentage:.1f}%)")

    print_section("7. MONTHLY REVENUE TREND")
    for month, revenue in analyzer.monthly_revenue().items():
        bar_length = int(revenue / stats['total_revenue'] * 30)
        bar = "█" * bar_length
        print(f"{month}: {format_currency(revenue):>12} {bar}")

    print_section("8. CATEGORY BREAKDOWN")
    for category, data in analyzer.category_breakdown().items():
        print(f"\n{category}:")
        print(f"  Orders: {data['order_count']}")
        print(f"  Total Revenue: {format_currency(data['total_revenue'])}")
        print(f"  Avg Order Value: {format_currency(data['avg_order_value'])}")

    print_section("9. HIGH VALUE ORDERS (>$1000)")
    high_value = analyzer.high_value_orders(1000.0)
    print(f"Found {len(high_value)} high-value orders:")
    for sale in sorted(high_value, key=lambda s: s.total_price, reverse=True)[:10]:
        print(f"  Order #{sale.order_id}: {sale.product} - {format_currency(sale.total_price)}")

    print_section("10. QUANTITY ANALYSIS (Top 10 Products)")
    for i, (product, qty) in enumerate(list(analyzer.quantity_by_product().items())[:10], 1):
        print(f"{i}. {product}: {qty} units")

    print_section("11. REVENUE BY DAY OF WEEK")
    for day, revenue in analyzer.revenue_by_day_of_week().items():
        print(f"{day}: {format_currency(revenue)}")

    print_section("12. REGIONAL PERFORMANCE")
    for region, data in analyzer.regional_performance().items():
        print(f"\n{region}:")
        print(f"  Orders: {data['order_count']}")
        print(f"  Revenue: {format_currency(data['total_revenue'])}")
        print(f"  Avg Order: {format_currency(data['avg_order_value'])}")
        print(f"  Unique Customers: {data['unique_customers']}")

    print("\n" + "=" * 60)
    print(" ANALYSIS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(script_dir, "sales_data.csv")
    run_analysis(csv_file)
