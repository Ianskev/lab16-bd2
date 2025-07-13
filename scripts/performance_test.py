import requests
import time
import statistics
import matplotlib.pyplot as plt
from app import create_app
from app.cache.redis_client import redis_client

def measure_response_time(url, runs=50):
    """Measure the response time for a given URL over multiple runs"""
    response_times = []
    
    for i in range(runs):
        start_time = time.time()
        response = requests.get(url)
        end_time = time.time()
        
        # Ensure the request was successful
        if response.status_code == 200:
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            response_times.append(response_time)
        else:
            print(f"Request failed with status code {response.status_code}")
    
    return response_times

def clear_cache():
    """Clear Redis cache for all test users"""
    for i in range(1, 21):
        redis_client.delete_data(f"cart:user{i}")

def run_performance_test():
    app = create_app()
    base_url = "http://localhost:5000"
    
    with app.app_context():
        # Test parameters
        test_user = "user5"  # Select one of the test users
        cart_url = f"{base_url}/cart/{test_user}"
        runs = 50
        
        print("Running performance tests...")
        print("=" * 50)
        
        # Test 1: First request (no cache)
        print("Test 1: First request (no cache)")
        clear_cache()  # Ensure cache is empty
        cold_times = measure_response_time(cart_url, 1)
        print(f"Cold response time: {cold_times[0]:.2f}ms")
        
        # Test 2: Subsequent requests (with cache)
        print("\nTest 2: Subsequent requests (with cache)")
        cached_times = measure_response_time(cart_url, runs)
        avg_cached = statistics.mean(cached_times)
        min_cached = min(cached_times)
        max_cached = max(cached_times)
        print(f"Average cached response time: {avg_cached:.2f}ms")
        print(f"Min cached response time: {min_cached:.2f}ms")
        print(f"Max cached response time: {max_cached:.2f}ms")
        
        # Test 3: Requests without cache
        print("\nTest 3: Requests without cache (clearing cache before each request)")
        uncached_times = []
        for i in range(runs):
            clear_cache()
            times = measure_response_time(cart_url, 1)
            uncached_times.extend(times)
        
        avg_uncached = statistics.mean(uncached_times)
        min_uncached = min(uncached_times)
        max_uncached = max(uncached_times)
        print(f"Average uncached response time: {avg_uncached:.2f}ms")
        print(f"Min uncached response time: {min_uncached:.2f}ms")
        print(f"Max uncached response time: {max_uncached:.2f}ms")
        
        # Calculate improvement
        improvement = ((avg_uncached - avg_cached) / avg_uncached) * 100
        print(f"\nCache performance improvement: {improvement:.2f}%")
        
        # Plot results
        plt.figure(figsize=(10, 6))
        plt.boxplot([cached_times, uncached_times], labels=['Cached', 'Uncached'])
        plt.title('Response Time Comparison: Cached vs. Uncached')
        plt.ylabel('Response Time (ms)')
        plt.savefig('performance_comparison.png')
        print("\nPerformance comparison chart saved to 'performance_comparison.png'")

if __name__ == "__main__":
    run_performance_test() 