"""
Load testing configuration for Community Packing List scaling validation.
Tests the application under realistic load patterns for 10,000+ users.
"""

from locust import HttpUser, task, between, events
import random
import json
import time
from datetime import datetime, timedelta


class PackingListUser(HttpUser):
    """
    Simulates realistic user behavior on the Community Packing List application.
    """
    wait_time = between(1, 5)  # Realistic pause between actions
    
    def on_start(self):
        """Initialize user session with realistic data."""
        self.item_ids = []
        self.packing_list_ids = []
        self.store_ids = []
        self.price_ids = []
        
        # Cache some IDs on startup
        self.load_initial_data()
    
    def load_initial_data(self):
        """Load initial data to use in tests."""
        try:
            # Get some item IDs
            response = self.client.get("/items/?limit=50")
            if response.status_code == 200 and response.text:
                # Parse response to extract item IDs (would need actual parsing based on response format)
                self.item_ids = list(range(1, 101))  # Fallback to assumed IDs
            
            # Get packing list IDs
            response = self.client.get("/lists/")
            if response.status_code == 200:
                self.packing_list_ids = list(range(1, 21))  # Fallback to assumed IDs
                
            # Get store IDs
            self.store_ids = list(range(1, 51))  # Assumed store IDs
            
        except Exception as e:
            # Fallback to default data if API calls fail
            self.item_ids = list(range(1, 101))
            self.packing_list_ids = list(range(1, 21))
            self.store_ids = list(range(1, 51))
    
    @task(10)
    def browse_home_page(self):
        """Browse the home page - most common action."""
        self.client.get("/", name="home_page")
    
    @task(8)
    def browse_items(self):
        """Browse items page with various filters."""
        filters = [
            "",  # No filters
            "?search=sleeping+bag",
            "?category=gear",
            "?has_prices=yes",
            "?price_min=10&price_max=100",
            f"?store={random.choice(self.store_ids)}",
        ]
        
        filter_params = random.choice(filters)
        self.client.get(f"/items/{filter_params}", name="browse_items")
    
    @task(6)
    def view_packing_list_detail(self):
        """View a packing list in detail."""
        if self.packing_list_ids:
            list_id = random.choice(self.packing_list_ids)
            self.client.get(f"/packing-lists/{list_id}/", name="packing_list_detail")
    
    @task(4)
    def search_items(self):
        """Search for items with various queries."""
        search_terms = [
            "boots", "sleeping", "backpack", "tent", "jacket",
            "flashlight", "compass", "map", "water", "food"
        ]
        
        term = random.choice(search_terms)
        self.client.get(f"/items/?search={term}", name="search_items")
    
    @task(3)
    def view_store_list(self):
        """Browse stores and locations."""
        self.client.get("/stores/", name="view_stores")
    
    @task(2)
    def add_price_submission(self):
        """Submit a price (realistic form submission)."""
        if self.item_ids and self.store_ids:
            item_id = random.choice(self.item_ids)
            store_id = random.choice(self.store_ids)
            
            # First get the form page
            self.client.get(f"/prices/add/?item_id={item_id}", name="get_price_form")
            
            # Then submit the form
            price_data = {
                'item': item_id,
                'store': store_id,
                'price': round(random.uniform(10.0, 200.0), 2),
                'quantity': random.choice([1, 2, 3, 4]),
                'confidence': random.choice(['low', 'medium', 'high']),
                'date_purchased': (datetime.now() - timedelta(days=random.randint(1, 30))).date().isoformat()
            }
            
            self.client.post(
                "/prices/add/",
                data=price_data,
                name="submit_price"
            )
    
    @task(2)
    def vote_on_price(self):
        """Vote on existing prices."""
        if self.item_ids:
            item_id = random.choice(self.item_ids)
            
            # Simulate getting price data and voting
            vote_data = {
                'is_correct_price': random.choice([True, False])
            }
            
            # This would need the actual price ID from a real implementation
            price_id = random.randint(1, 1000)  # Simulated
            self.client.post(
                f"/prices/{price_id}/vote/",
                data=vote_data,
                name="vote_on_price"
            )
    
    @task(1)
    def create_packing_list(self):
        """Create a new packing list (rare but important action)."""
        list_data = {
            'name': f'Test List {random.randint(1000, 9999)}',
            'description': 'Load test generated packing list',
            'event_type': random.choice(['school', 'training', 'deployment', 'other'])
        }
        
        self.client.post(
            "/packing-lists/create/",
            data=list_data,
            name="create_packing_list"
        )
    
    @task(1)
    def geographic_filter(self):
        """Test geographic filtering (computationally expensive)."""
        if self.packing_list_ids:
            list_id = random.choice(self.packing_list_ids)
            base_id = random.randint(1, 10)  # Assumed base IDs
            radius = random.choice([25, 50, 100])
            
            self.client.get(
                f"/packing-lists/{list_id}/?base_filter={base_id}&radius={radius}",
                name="geographic_filter"
            )


class PeakTrafficUser(PackingListUser):
    """
    Simulates peak traffic behavior with more intensive usage patterns.
    """
    wait_time = between(0.5, 2)  # Faster interactions during peak
    
    @task(15)
    def rapid_item_browsing(self):
        """Rapid browsing during peak hours."""
        for _ in range(3):  # Browse multiple pages quickly
            page = random.randint(1, 5)
            self.client.get(f"/items/?page={page}", name="rapid_browse")


class AdminUser(HttpUser):
    """
    Simulates admin user behavior (less frequent but more database-intensive).
    """
    wait_time = between(5, 15)
    weight = 1  # Much fewer admin users
    
    @task(3)
    def admin_dashboard(self):
        """Admin dashboard access."""
        self.client.get("/admin/", name="admin_dashboard")
    
    @task(2)
    def bulk_operations(self):
        """Bulk operations that stress the database."""
        self.client.get("/admin/packing_lists/item/?all", name="bulk_admin_view")


# Performance monitoring events
@events.request.add_listener
def record_request_metrics(request_type, name, response_time, response_length, response, context, exception, **kwargs):
    """Record detailed performance metrics."""
    if exception:
        print(f"Request failed: {name} - {exception}")
    elif response_time > 2000:  # Log slow requests (>2s)
        print(f"Slow request: {name} - {response_time}ms")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Initialize test environment."""
    print("🚀 Starting load test for Community Packing List")
    print(f"Target URL: {environment.host}")
    print("Simulating realistic user behavior patterns...")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Generate performance report."""
    print("\n📊 Load Test Summary")
    print("=" * 50)
    
    stats = environment.stats
    
    print(f"Total requests: {stats.total.num_requests}")
    print(f"Failed requests: {stats.total.num_failures}")
    print(f"Average response time: {stats.total.avg_response_time:.2f}ms")
    print(f"95th percentile: {stats.total.get_response_time_percentile(0.95):.2f}ms")
    print(f"99th percentile: {stats.total.get_response_time_percentile(0.99):.2f}ms")
    print(f"Requests per second: {stats.total.current_rps:.2f}")
    
    # Identify problematic endpoints
    slow_endpoints = [
        (name, stat.avg_response_time) 
        for name, stat in stats.entries.items() 
        if stat.avg_response_time > 1000
    ]
    
    if slow_endpoints:
        print("\n⚠️  Slow Endpoints (>1s average):")
        for endpoint, avg_time in sorted(slow_endpoints, key=lambda x: x[1], reverse=True):
            print(f"  {endpoint}: {avg_time:.2f}ms")
    
    # Performance targets
    print(f"\n🎯 Performance Target Analysis:")
    print(f"  ✅ < 1s response time: {stats.total.get_response_time_percentile(0.95) < 1000}")
    print(f"  ✅ < 0.1% error rate: {(stats.total.num_failures / stats.total.num_requests * 100) < 0.1 if stats.total.num_requests > 0 else False}")
    print(f"  ✅ > 1000 RPS capability: {stats.total.current_rps > 1000}")


# Load test scenarios
class LoadTestScenarios:
    """
    Predefined load test scenarios for different scaling phases.
    """
    
    @staticmethod
    def get_ramp_up_test():
        """Gradual ramp-up test to find breaking point."""
        return {
            'users': 1000,
            'spawn_rate': 10,  # 10 users per second
            'run_time': '10m',
            'description': 'Gradual ramp-up to 1000 concurrent users'
        }
    
    @staticmethod
    def get_steady_state_test():
        """Steady state test at target load."""
        return {
            'users': 10000,
            'spawn_rate': 100,  # 100 users per second spawn rate
            'run_time': '30m',
            'description': 'Sustained load at 10,000 concurrent users'
        }
    
    @staticmethod
    def get_spike_test():
        """Spike test for traffic surges."""
        return {
            'users': 15000,
            'spawn_rate': 500,  # Rapid spike
            'run_time': '5m',
            'description': 'Traffic spike simulation'
        }
    
    @staticmethod
    def get_endurance_test():
        """Long-running endurance test."""
        return {
            'users': 5000,
            'spawn_rate': 50,
            'run_time': '2h',
            'description': 'Extended endurance test for memory leaks'
        }


if __name__ == "__main__":
    print("Available load test scenarios:")
    print("1. Ramp-up test: locust -f load-test.py --users 1000 --spawn-rate 10 -t 10m")
    print("2. Steady state: locust -f load-test.py --users 10000 --spawn-rate 100 -t 30m")
    print("3. Spike test: locust -f load-test.py --users 15000 --spawn-rate 500 -t 5m")
    print("4. Endurance: locust -f load-test.py --users 5000 --spawn-rate 50 -t 2h")