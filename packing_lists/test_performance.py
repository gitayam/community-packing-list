"""
Performance tests for Django backend operations
Tests database queries, view response times, and bulk operations.
"""
from django.test import TestCase, TransactionTestCase
from django.test.utils import override_settings
from django.urls import reverse
from django.core.cache import cache
from django.db import connection
from django.test import Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import time
from unittest import skipIf
import sys

from packing_lists.models import (
    Item, PackingList, Store, Price, Vote, 
    PackingListItem, School
)


class DatabasePerformanceTestCase(TestCase):
    """Test database query performance and optimization."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_test_data()
    
    @classmethod
    def _setup_test_data(cls):
        """Create test data for performance testing."""
        # Create schools
        cls.schools = []
        for i in range(10):
            school = School.objects.create(
                name=f"School {i}",
                address=f"Address for School {i}"
            )
            cls.schools.append(school)
        
        # Create stores
        cls.stores = []
        for i in range(20):
            store = Store.objects.create(
                name=f"Store {i}",
                address_line1=f"{i} Test Street",
                city=f"Store City {i}",
                state="TX",
                zip_code=f"7800{i:02d}"
            )
            cls.stores.append(store)
        
        # Create items
        cls.items = []
        for i in range(100):
            item = Item.objects.create(
                name=f"Item {i}",
                description=f"Description for item {i}",
                nsn_lin=f"NSN{i:04d}" if i % 3 == 0 else None
            )
            cls.items.append(item)
        
        # Create packing lists
        cls.packing_lists = []
        for i in range(20):
            plist = PackingList.objects.create(
                name=f"Packing List {i}",
                description=f"Description for packing list {i}",
                school=cls.schools[i % len(cls.schools)]
            )
            cls.packing_lists.append(plist)
        
        # Create packing list items
        for plist in cls.packing_lists:
            # Add 10-20 items to each list
            items_to_add = cls.items[:(10 + len(cls.packing_lists) % 10)]
            for j, item in enumerate(items_to_add):
                PackingListItem.objects.create(
                    packing_list=plist,
                    item=item,
                    quantity=j % 5 + 1,
                    required=j % 3 == 0
                )
        
        # Create prices
        for i, item in enumerate(cls.items[:50]):  # First 50 items get prices
            for j in range(3):  # 3 prices per item
                Price.objects.create(
                    item=item,
                    store=cls.stores[j % len(cls.stores)],
                    price=f"{10 + i + j}.99",
                    quantity=j + 1,
                    ip_address=f"192.168.1.{i + j + 1}",
                    confidence='medium'
                )

    def test_item_list_query_performance(self):
        """Test that item list queries are efficient."""
        start_time = time.time()
        
        # Simulate the items view query with filtering
        items = Item.objects.select_related().prefetch_related('prices__store')
        list(items)  # Force evaluation
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete in under 1 second even with related data
        self.assertLess(duration, 1.0, 
                       f"Item list query took {duration:.3f}s, expected < 1.0s")

    def test_packing_list_detail_query_performance(self):
        """Test packing list detail view query performance."""
        packing_list = self.packing_lists[0]
        
        start_time = time.time()
        
        # Simulate the detail view query with all related data
        plist = PackingList.objects.select_related('school').prefetch_related(
            'packinglistitem_set__item__prices__store'
        ).get(pk=packing_list.pk)
        
        # Access all related data to trigger queries
        items = list(plist.packinglistitem_set.all())
        for pli in items:
            prices = list(pli.item.prices.all())
            for price in prices:
                _ = price.store.name
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.assertLess(duration, 0.5,
                       f"Packing list detail query took {duration:.3f}s, expected < 0.5s")

    def test_bulk_price_creation_performance(self):
        """Test bulk creation of price objects."""
        test_item = self.items[0]
        test_store = self.stores[0]
        
        start_time = time.time()
        
        # Create 100 prices using bulk_create
        prices = []
        for i in range(100):
            prices.append(Price(
                item=test_item,
                store=test_store,
                price=f"{10 + i}.99",
                quantity=1,
                ip_address=f"10.0.0.{i % 255}",
                confidence='low'
            ))
        
        Price.objects.bulk_create(prices)
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.assertLess(duration, 0.5,
                       f"Bulk price creation took {duration:.3f}s, expected < 0.5s")

    def test_complex_aggregation_performance(self):
        """Test complex aggregation queries."""
        start_time = time.time()
        
        from django.db.models import Count, Avg, Min, Max
        
        # Complex aggregation similar to analytics queries
        stats = Item.objects.annotate(
            price_count=Count('prices'),
            avg_price=Avg('prices__price'),
            min_price=Min('prices__price'),
            max_price=Max('prices__price')
        ).filter(price_count__gt=0)
        
        list(stats)  # Force evaluation
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.assertLess(duration, 1.0,
                       f"Complex aggregation took {duration:.3f}s, expected < 1.0s")

    def test_search_query_performance(self):
        """Test search functionality performance."""
        start_time = time.time()
        
        # Simulate search across multiple fields
        results = Item.objects.filter(
            name__icontains='item'
        ).select_related().prefetch_related('prices__store')
        
        list(results)  # Force evaluation
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.assertLess(duration, 0.5,
                       f"Search query took {duration:.3f}s, expected < 0.5s")


class ViewPerformanceTestCase(TestCase):
    """Test view response time performance."""
    
    def setUp(self):
        """Set up test data for view testing."""
        self.client = Client()
        
        # Create minimal test data
        self.school = School.objects.create(name="Test School", address="Test Address")
        self.store = Store.objects.create(name="Test Store", address_line1="123 Test St")
        
        self.items = []
        for i in range(10):
            item = Item.objects.create(name=f"Test Item {i}")
            self.items.append(item)
        
        self.packing_list = PackingList.objects.create(
            name="Test List",
            description="Test Description",
            school=self.school
        )
        
        # Add items to packing list
        for item in self.items:
            PackingListItem.objects.create(
                packing_list=self.packing_list,
                item=item,
                quantity=1
            )

    def test_home_page_response_time(self):
        """Test home page loads quickly."""
        start_time = time.time()
        
        response = self.client.get(reverse('home'))
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(duration, 1.0,
                       f"Home page took {duration:.3f}s, expected < 1.0s")

    def test_items_list_response_time(self):
        """Test items list page response time."""
        start_time = time.time()
        
        response = self.client.get(reverse('items'))
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(duration, 1.0,
                       f"Items list took {duration:.3f}s, expected < 1.0s")

    def test_packing_list_detail_response_time(self):
        """Test packing list detail page response time."""
        start_time = time.time()
        
        response = self.client.get(
            reverse('packing_list_detail', args=[self.packing_list.pk])
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(duration, 1.0,
                       f"Packing list detail took {duration:.3f}s, expected < 1.0s")

    def test_ajax_price_modal_response_time(self):
        """Test AJAX price modal loading time."""
        start_time = time.time()
        
        response = self.client.get(
            f'/item/{self.items[0].pk}/add_price_modal/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(duration, 0.5,
                       f"AJAX modal took {duration:.3f}s, expected < 0.5s")


class CachePerformanceTestCase(TestCase):
    """Test caching performance and efficiency."""
    
    def setUp(self):
        """Set up test data."""
        cache.clear()
        self.store = Store.objects.create(name="Cache Test Store")
        self.item = Item.objects.create(name="Cache Test Item")

    def test_cache_hit_performance(self):
        """Test that cache hits are fast."""
        cache_key = "test_performance_key"
        test_data = {"complex": "data", "with": ["lists", "and", {"nested": "objects"}]}
        
        # Set cache
        cache.set(cache_key, test_data, timeout=300)
        
        # Measure cache hit time
        start_time = time.time()
        
        for _ in range(100):  # Multiple cache hits
            result = cache.get(cache_key)
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.assertEqual(result, test_data)
        self.assertLess(duration, 0.1,
                       f"100 cache hits took {duration:.3f}s, expected < 0.1s")

    def test_rate_limiting_cache_performance(self):
        """Test rate limiting cache operations."""
        from packing_lists.security import is_rate_limited
        
        start_time = time.time()
        
        # Test multiple rate limit checks
        ip_address = "192.168.1.100"
        for i in range(50):
            is_limited, time_left = is_rate_limited(ip_address)
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.assertLess(duration, 0.5,
                       f"50 rate limit checks took {duration:.3f}s, expected < 0.5s")


class MemoryPerformanceTestCase(TransactionTestCase):
    """Test memory usage and efficiency."""
    
    def test_large_queryset_memory_usage(self):
        """Test memory efficiency with large querysets."""
        # Create a large number of items
        items = []
        for i in range(1000):
            items.append(Item(name=f"Memory Test Item {i}"))
        
        Item.objects.bulk_create(items)
        
        # Test iterator vs all() for memory efficiency
        start_time = time.time()
        
        # Use iterator for memory efficiency
        count = 0
        for item in Item.objects.iterator():
            count += 1
            if count >= 1000:
                break
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.assertEqual(count, 1000)
        self.assertLess(duration, 1.0,
                       f"Iterator over 1000 items took {duration:.3f}s, expected < 1.0s")

    def test_bulk_operations_memory_efficiency(self):
        """Test memory efficiency of bulk operations."""
        start_time = time.time()
        
        # Create items using bulk_create
        items = [Item(name=f"Bulk Item {i}") for i in range(500)]
        Item.objects.bulk_create(items, batch_size=100)
        
        # Update items using bulk_update
        created_items = list(Item.objects.filter(name__startswith="Bulk Item"))
        for item in created_items:
            item.description = f"Updated description for {item.name}"
        
        Item.objects.bulk_update(created_items, ['description'], batch_size=100)
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.assertLess(duration, 2.0,
                       f"Bulk operations took {duration:.3f}s, expected < 2.0s")


@skipIf(sys.platform == 'win32', "Unix-specific performance tests")
class SystemPerformanceTestCase(TestCase):
    """Test system-level performance characteristics."""
    
    def test_concurrent_request_handling(self):
        """Test handling multiple concurrent requests."""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            client = Client()
            start = time.time()
            response = client.get(reverse('home'))
            end = time.time()
            results.put((response.status_code, end - start))
        
        # Create multiple threads for concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        start_time = time.time()
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Collect results
        response_times = []
        while not results.empty():
            status_code, duration = results.get()
            self.assertEqual(status_code, 200)
            response_times.append(duration)
        
        self.assertEqual(len(response_times), 10)
        
        # Average response time should be reasonable
        avg_response_time = sum(response_times) / len(response_times)
        self.assertLess(avg_response_time, 1.0,
                       f"Average response time {avg_response_time:.3f}s, expected < 1.0s")
        
        # Total time should be less than sequential execution
        self.assertLess(total_duration, sum(response_times) * 0.8,
                       "Concurrent requests should be faster than sequential")

    def test_database_connection_efficiency(self):
        """Test database connection management."""
        from django.db import connections
        
        start_time = time.time()
        
        # Multiple database operations
        for i in range(20):
            Item.objects.filter(pk=1).exists()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should reuse connections efficiently
        self.assertLess(duration, 0.5,
                       f"20 DB operations took {duration:.3f}s, expected < 0.5s")
        
        # Check connection count (should not create many connections)
        connection_count = len(connections.all())
        self.assertLessEqual(connection_count, 2,
                           f"Used {connection_count} connections, expected ≤ 2")


class BenchmarkTestCase(TestCase):
    """Benchmark tests for performance regression detection."""
    
    def setUp(self):
        """Create benchmark data."""
        self.store = Store.objects.create(name="Benchmark Store")
        self.items = []
        for i in range(50):
            item = Item.objects.create(name=f"Benchmark Item {i}")
            self.items.append(item)
    
    def benchmark_price_creation(self):
        """Benchmark price creation operations."""
        times = []
        
        for i in range(10):
            start = time.time()
            
            Price.objects.create(
                item=self.items[i],
                store=self.store,
                price=f"{10 + i}.99",
                quantity=1,
                ip_address=f"192.168.1.{i}"
            )
            
            end = time.time()
            times.append(end - start)
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        return {
            'average_time': avg_time,
            'max_time': max_time,
            'total_operations': len(times)
        }
    
    def test_benchmark_regression(self):
        """Test for performance regressions."""
        benchmark = self.benchmark_price_creation()
        
        # Ensure performance hasn't regressed
        self.assertLess(benchmark['average_time'], 0.1,
                       f"Average price creation time {benchmark['average_time']:.3f}s")
        self.assertLess(benchmark['max_time'], 0.5,
                       f"Max price creation time {benchmark['max_time']:.3f}s")
        
        print(f"Benchmark results: {benchmark}")


# Performance test utilities
class PerformanceTestMixin:
    """Mixin for adding performance testing utilities to test cases."""
    
    def assertExecutionTime(self, func, max_time, *args, **kwargs):
        """Assert that a function executes within a maximum time."""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        
        self.assertLess(duration, max_time,
                       f"Function took {duration:.3f}s, expected < {max_time}s")
        return result
    
    def benchmark_function(self, func, iterations=10, *args, **kwargs):
        """Benchmark a function over multiple iterations."""
        times = []
        for _ in range(iterations):
            start = time.time()
            func(*args, **kwargs)
            end = time.time()
            times.append(end - start)
        
        return {
            'times': times,
            'average': sum(times) / len(times),
            'min': min(times),
            'max': max(times),
            'total': sum(times)
        }