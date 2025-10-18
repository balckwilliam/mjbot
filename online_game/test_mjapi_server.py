"""
Test script for MJAPI Server
测试 MJAPI 服务器的脚本
"""
import requests
import json
import time


def test_user_registration(base_url):
    """Test user registration"""
    print("Testing user registration...")
    username = f"test_user_{int(time.time())}"
    
    response = requests.post(
        f"{base_url}/user/register",
        json={'name': username}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Registered user: {data['name']}")
        print(f"Secret: {data['secret']}")
        return username, data['secret']
    else:
        print(f"Error: {response.text}")
        return None, None


def test_user_login(base_url, username, secret):
    """Test user login"""
    print("\nTesting user login...")
    
    response = requests.post(
        f"{base_url}/user/login",
        json={'name': username, 'secret': secret}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Login successful!")
        print(f"Token (id): {data['id']}")
        return data['id']
    else:
        print(f"Error: {response.text}")
        return None


def test_get_user_info(base_url, token):
    """Test getting user info"""
    print("\nTesting get user info...")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{base_url}/user", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"User info: {data}")
    else:
        print(f"Error: {response.text}")


def test_list_models(base_url, token):
    """Test listing available models"""
    print("\nTesting list models...")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{base_url}/mjai/list", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Available models: {data['models']}")
        return data['models']
    else:
        print(f"Error: {response.text}")
        return []


def test_get_usage(base_url, token):
    """Test getting usage"""
    print("\nTesting get usage...")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{base_url}/mjai/usage", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Usage: {data['used']}")
    else:
        print(f"Error: {response.text}")


def test_get_limit(base_url, token):
    """Test getting limit"""
    print("\nTesting get limit...")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{base_url}/mjai/limit", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Limit: {data['limit']}, Used: {data['used']}")
    else:
        print(f"Error: {response.text}")


def test_start_bot(base_url, token, model):
    """Test starting a bot"""
    print("\nTesting start bot...")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(
        f"{base_url}/mjai/start",
        headers=headers,
        json={'id': 0, 'bound': 256, 'model': model}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Bot started: {data}")
    else:
        print(f"Error: {response.text}")


def test_act(base_url, token):
    """Test single act"""
    print("\nTesting act...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Send a start_game message
    msg = {
        'seq': 0,
        'data': {
            'type': 'start_game',
            'id': 0
        }
    }
    
    response = requests.post(
        f"{base_url}/mjai/act",
        headers=headers,
        json=msg
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        if response.content:
            data = response.json()
            print(f"Response: {data}")
    else:
        print(f"Error: {response.text}")


def test_batch(base_url, token):
    """Test batch actions"""
    print("\nTesting batch...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Send a batch of messages
    messages = [
        {
            'seq': 0,
            'data': {
                'type': 'start_game',
                'id': 0
            }
        },
        {
            'seq': 1,
            'data': {
                'type': 'start_kyoku',
                'bakaze': 'E',
                'kyoku': 1,
                'honba': 0,
                'oya': 0,
                'scores': [25000, 25000, 25000, 25000],
                'dora_marker': '5z',
                'tehais': [
                    ['1m', '2m', '3m', '4m', '5m', '6m', '7m', '8m', '9m', '1p', '2p', '3p', '4p'],
                    [],
                    [],
                    []
                ]
            }
        },
        {
            'seq': 2,
            'data': {
                'type': 'tsumo',
                'actor': 0,
                'pai': '5p',
                'can_act': True
            }
        }
    ]
    
    response = requests.post(
        f"{base_url}/mjai/batch",
        headers=headers,
        json=messages
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        if response.content:
            data = response.json()
            print(f"Bot reaction: {data}")
    else:
        print(f"Error: {response.text}")


def test_stop_bot(base_url, token):
    """Test stopping bot"""
    print("\nTesting stop bot...")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(f"{base_url}/mjai/stop", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Bot stopped: {data}")
    else:
        print(f"Error: {response.text}")


def test_logout(base_url, token):
    """Test user logout"""
    print("\nTesting logout...")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(f"{base_url}/user/logout", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Logout successful: {data}")
    else:
        print(f"Error: {response.text}")


def test_health_check(base_url):
    """Test health check endpoint"""
    print("\nTesting health check endpoint...")
    response = requests.get(f"{base_url}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def main():
    import argparse
    import time
    
    parser = argparse.ArgumentParser(description='Test MJAPI Server')
    parser.add_argument('--url', type=str, default='http://localhost:5001',
                       help='Base URL of the MJAPI server (default: http://localhost:5001)')
    
    args = parser.parse_args()
    
    print(f"Testing MJAPI Server at {args.url}")
    print("=" * 60)
    print()
    
    try:
        # Test health check
        test_health_check(args.url)
        
        # Test user registration and login
        username, secret = test_user_registration(args.url)
        if not username or not secret:
            print("Registration failed, stopping tests")
            return
        
        token = test_user_login(args.url, username, secret)
        if not token:
            print("Login failed, stopping tests")
            return
        
        # Test authenticated endpoints
        test_get_user_info(args.url, token)
        models = test_list_models(args.url, token)
        test_get_usage(args.url, token)
        test_get_limit(args.url, token)
        
        # Test bot operations
        if models:
            test_start_bot(args.url, token, models[0])
            test_act(args.url, token)
            test_batch(args.url, token)
            test_stop_bot(args.url, token)
        
        # Test logout
        test_logout(args.url, token)
        
        print("=" * 60)
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to server at {args.url}")
        print("Make sure the MJAPI server is running:")
        print("  python online_game/mjapi_server.py")
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
