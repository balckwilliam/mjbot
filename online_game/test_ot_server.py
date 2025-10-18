"""
Test script for OT Server
测试 OT 服务器的脚本
"""
import json
import gzip
import requests


def test_health_check(base_url):
    """Test health check endpoint"""
    print("Testing health check endpoint...")
    response = requests.get(f"{base_url}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_check_auth(base_url, api_key=None):
    """Test authentication check endpoint"""
    print("Testing authentication check endpoint...")
    headers = {}
    if api_key:
        headers['Authorization'] = api_key
    
    response = requests.post(f"{base_url}/check", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_react_batch(base_url, api_key=None, use_gzip=False):
    """Test react_batch endpoint"""
    print(f"Testing react_batch endpoint (gzip={use_gzip})...")
    
    # Create sample data
    # obs: observation array (simplified example)
    obs = [[0.0] * 100]  # Simplified observation
    masks = [[True] + [False] * 46]  # Only first action is valid
    
    post_data = {
        'obs': obs,
        'masks': masks
    }
    
    headers = {'Content-Type': 'application/json'}
    if api_key:
        headers['Authorization'] = api_key
    
    if use_gzip:
        # Compress the data
        data = json.dumps(post_data, separators=(',', ':'))
        compressed_data = gzip.compress(data.encode('utf-8'))
        headers['Content-Encoding'] = 'gzip'
        response = requests.post(f"{base_url}/react_batch", 
                                headers=headers, 
                                data=compressed_data)
    else:
        response = requests.post(f"{base_url}/react_batch", 
                                headers=headers, 
                                json=post_data)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Actions: {result['actions']}")
        print(f"Is Greedy: {result['is_greedy']}")
        print(f"Number of Q-values: {len(result['q_out'][0]) if result['q_out'] else 0}")
    else:
        print(f"Error: {response.text}")
    print()


def test_react_batch_3p(base_url, api_key=None):
    """Test react_batch_3p endpoint"""
    print("Testing react_batch_3p endpoint...")
    
    # Create sample data
    obs = [[0.0] * 100]  # Simplified observation
    masks = [[True] + [False] * 46]  # Only first action is valid
    
    post_data = {
        'obs': obs,
        'masks': masks
    }
    
    headers = {'Content-Type': 'application/json'}
    if api_key:
        headers['Authorization'] = api_key
    
    response = requests.post(f"{base_url}/react_batch_3p", 
                            headers=headers, 
                            json=post_data)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Actions: {result['actions']}")
        print(f"Is Greedy: {result['is_greedy']}")
    else:
        print(f"Error: {response.text}")
    print()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Test OT Server')
    parser.add_argument('--url', type=str, default='http://localhost:5000',
                       help='Base URL of the OT server (default: http://localhost:5000)')
    parser.add_argument('--api-key', type=str, default=None,
                       help='API key for authentication (optional)')
    
    args = parser.parse_args()
    
    print(f"Testing OT Server at {args.url}")
    print("=" * 50)
    print()
    
    try:
        # Run tests
        test_health_check(args.url)
        test_check_auth(args.url, args.api_key)
        test_react_batch(args.url, args.api_key, use_gzip=False)
        test_react_batch(args.url, args.api_key, use_gzip=True)
        test_react_batch_3p(args.url, args.api_key)
        
        print("=" * 50)
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to server at {args.url}")
        print("Make sure the OT server is running:")
        print("  python online_game/ot_server.py")
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
