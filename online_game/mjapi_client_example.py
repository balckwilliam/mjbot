"""
Example client for MJAPI Server
展示如何使用 MJAPI 服务器的示例客户端

This example demonstrates how to connect to the MJAPI server and interact with the AI bot.
此示例演示如何连接到 MJAPI 服务器并与 AI bot 交互。
"""
import requests
import json


class MJAPIClient:
    """Client for MJAPI Server / MJAPI 服务器客户端"""
    
    def __init__(self, url, timeout=5):
        """
        Initialize MJAPI client
        
        Args:
            url: Server URL, e.g., "http://localhost:5001"
            timeout: Request timeout in seconds
        """
        self.url = url
        self.timeout = timeout
        self.token = None
        self.username = None
    
    def register(self, username):
        """
        Register a new user
        注册新用户
        
        Args:
            username: Username to register
        
        Returns:
            secret: User secret for login
        """
        response = requests.post(
            f"{self.url}/user/register",
            json={'name': username},
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['secret']
        else:
            raise Exception(f"Registration failed: {response.status_code} - {response.text}")
    
    def login(self, username, secret):
        """
        Login with username and secret
        使用用户名和密钥登录
        
        Args:
            username: Username
            secret: User secret
        
        Returns:
            token: Authentication token
        """
        response = requests.post(
            f"{self.url}/user/login",
            json={'name': username, 'secret': secret},
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data['id']
            self.username = username
            return self.token
        else:
            raise Exception(f"Login failed: {response.status_code} - {response.text}")
    
    def logout(self):
        """
        Logout current user
        登出当前用户
        """
        if not self.token:
            return
        
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.post(
            f"{self.url}/user/logout",
            headers=headers,
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            self.token = None
            self.username = None
        else:
            raise Exception(f"Logout failed: {response.status_code} - {response.text}")
    
    def get_user_info(self):
        """
        Get current user information
        获取当前用户信息
        
        Returns:
            dict: User information including usage and limit
        """
        if not self.token:
            raise Exception("Not logged in")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(
            f"{self.url}/user",
            headers=headers,
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Get user info failed: {response.status_code} - {response.text}")
    
    def list_models(self):
        """
        List available AI models
        列出可用的 AI 模型
        
        Returns:
            list: List of model names
        """
        if not self.token:
            raise Exception("Not logged in")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(
            f"{self.url}/mjai/list",
            headers=headers,
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['models']
        else:
            raise Exception(f"List models failed: {response.status_code} - {response.text}")
    
    def start_bot(self, seat=0, model='mjbot-default', bound=256):
        """
        Start a bot session
        启动 bot 会话
        
        Args:
            seat: Player seat (0-3)
            model: Model name
            bound: Sequence bound
        """
        if not self.token:
            raise Exception("Not logged in")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.post(
            f"{self.url}/mjai/start",
            headers=headers,
            json={'id': seat, 'bound': bound, 'model': model},
            timeout=self.timeout
        )
        
        if response.status_code != 200:
            raise Exception(f"Start bot failed: {response.status_code} - {response.text}")
    
    def stop_bot(self):
        """
        Stop the bot session
        停止 bot 会话
        """
        if not self.token:
            raise Exception("Not logged in")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.post(
            f"{self.url}/mjai/stop",
            headers=headers,
            timeout=self.timeout
        )
        
        if response.status_code != 200:
            raise Exception(f"Stop bot failed: {response.status_code} - {response.text}")
    
    def act(self, seq, message):
        """
        Send a single mjai message and get bot reaction
        发送单个 mjai 消息并获取 bot 反应
        
        Args:
            seq: Sequence number
            message: mjai protocol message dict
        
        Returns:
            dict: Bot reaction or None
        """
        if not self.token:
            raise Exception("Not logged in")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.post(
            f"{self.url}/mjai/act",
            headers=headers,
            json={'seq': seq, 'data': message},
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            if response.content:
                return response.json().get('act')
            return None
        else:
            raise Exception(f"Act failed: {response.status_code} - {response.text}")
    
    def batch(self, messages):
        """
        Send multiple mjai messages and get last bot reaction
        发送多个 mjai 消息并获取最后的 bot 反应
        
        Args:
            messages: List of messages, each with 'seq' and 'data' keys
        
        Returns:
            dict: Bot reaction or None
        """
        if not self.token:
            raise Exception("Not logged in")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.post(
            f"{self.url}/mjai/batch",
            headers=headers,
            json=messages,
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            if response.content:
                return response.json().get('act')
            return None
        else:
            raise Exception(f"Batch failed: {response.status_code} - {response.text}")


def example_basic_usage():
    """Basic usage example / 基本使用示例"""
    print("=== Basic Usage Example ===")
    print("=== 基本使用示例 ===\n")
    
    # Create client
    client = MJAPIClient(url="http://localhost:5001")
    
    # Register and login
    import time
    import random
    username = f"test_user_{int(time.time())}_{random.randint(1000, 9999)}"
    print(f"Registering user: {username}")
    secret = client.register(username)
    print(f"Secret: {secret}\n")
    
    print(f"Logging in...")
    client.login(username, secret)
    print(f"Logged in successfully!\n")
    
    # Get user info
    user_info = client.get_user_info()
    print(f"User info: {user_info}\n")
    
    # List models
    models = client.list_models()
    print(f"Available models: {models}\n")
    
    # Start bot
    print("Starting bot...")
    client.start_bot(seat=0, model=models[0])
    print("Bot started!\n")
    
    # Send start_game message
    print("Sending start_game message...")
    reaction = client.act(0, {
        'type': 'start_game',
        'id': 0
    })
    print(f"Bot reaction: {reaction}\n")
    
    # Send start_kyoku message
    print("Sending start_kyoku message...")
    reaction = client.act(1, {
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
    })
    print(f"Bot reaction: {reaction}\n")
    
    # Send tsumo message (draw a tile)
    print("Sending tsumo message...")
    reaction = client.act(2, {
        'type': 'tsumo',
        'actor': 0,
        'pai': '5p',
        'can_act': True
    })
    print(f"Bot reaction (should discard): {reaction}\n")
    
    # Stop bot
    print("Stopping bot...")
    client.stop_bot()
    print("Bot stopped!\n")
    
    # Logout
    print("Logging out...")
    client.logout()
    print("Logged out!\n")


def example_batch_usage():
    """Batch usage example / 批量使用示例"""
    print("=== Batch Usage Example ===")
    print("=== 批量使用示例 ===\n")
    
    # Create client
    client = MJAPIClient(url="http://localhost:5001")
    
    # Register and login
    import time
    import random
    username = f"test_user_{int(time.time())}_{random.randint(1000, 9999)}"
    print(f"Registering and logging in as {username}...")
    secret = client.register(username)
    client.login(username, secret)
    print("Logged in!\n")
    
    # Start bot
    models = client.list_models()
    client.start_bot(seat=0, model=models[0])
    print("Bot started!\n")
    
    # Send multiple messages in batch
    print("Sending batch of messages...")
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
    
    reaction = client.batch(messages)
    print(f"Bot final reaction: {reaction}\n")
    
    # Cleanup
    client.stop_bot()
    client.logout()
    print("Done!\n")


def main():
    """Run all examples / 运行所有示例"""
    print("MJAPI Server Client Examples")
    print("MJAPI 服务器客户端示例")
    print("=" * 60)
    print()
    
    try:
        example_basic_usage()
        example_batch_usage()
        
        print("=" * 60)
        print("Examples completed!")
        print("示例完成！")
        print()
        print("Note: Make sure the MJAPI server is running before running these examples:")
        print("注意：在运行这些示例之前，请确保 MJAPI 服务器正在运行：")
        print("  python online_game/mjapi_server.py")
        
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to server!")
        print("错误：无法连接到服务器！")
        print("Please start the MJAPI server first:")
        print("请先启动 MJAPI 服务器：")
        print("  python online_game/mjapi_server.py")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
