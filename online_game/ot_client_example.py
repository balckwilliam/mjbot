"""
Example client for OT Server
展示如何使用 OT 服务器的示例客户端

This example demonstrates how to connect to the OT server and get AI decisions.
此示例演示如何连接到 OT 服务器并获取 AI 决策。
"""
import json
import gzip
import requests


class OTClient:
    """Client for OT Server / OT 服务器客户端"""
    
    def __init__(self, url, api_key=None, timeout=5):
        """
        Initialize OT client
        
        Args:
            url: Server URL, e.g., "http://localhost:5000"
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
        """
        self.url = url
        self.api_key = api_key
        self.timeout = timeout
        self.headers = {}
        if api_key:
            self.headers['Authorization'] = api_key
    
    def check_connection(self):
        """
        Check if the server is accessible
        检查服务器是否可访问
        
        Returns:
            bool: True if server is accessible
        """
        try:
            response = requests.get(
                f"{self.url}/health",
                timeout=self.timeout
            )
            return response.status_code == 200
        except:
            return False
    
    def get_decision(self, obs, masks, use_3p=False, use_gzip=True):
        """
        Get AI decision for given observation and action masks
        根据给定的观察和动作掩码获取 AI 决策
        
        Args:
            obs: List of observation arrays
            masks: List of action mask arrays
            use_3p: Whether to use 3-player endpoint (default: False for 4-player)
            use_gzip: Whether to compress the request (default: True)
        
        Returns:
            dict: Response containing actions, q_out, masks, and is_greedy
        """
        endpoint = '/react_batch_3p' if use_3p else '/react_batch'
        
        post_data = {
            'obs': obs,
            'masks': masks
        }
        
        headers = self.headers.copy()
        headers['Content-Type'] = 'application/json'
        
        if use_gzip:
            # Compress the request
            data = json.dumps(post_data, separators=(',', ':'))
            compressed_data = gzip.compress(data.encode('utf-8'))
            headers['Content-Encoding'] = 'gzip'
            
            response = requests.post(
                f"{self.url}{endpoint}",
                headers=headers,
                data=compressed_data,
                timeout=self.timeout
            )
        else:
            response = requests.post(
                f"{self.url}{endpoint}",
                headers=headers,
                json=post_data,
                timeout=self.timeout
            )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Server error: {response.status_code} - {response.text}")


def example_basic_usage():
    """Basic usage example / 基本使用示例"""
    print("=== Basic Usage Example ===")
    print("=== 基本使用示例 ===\n")
    
    # Create client
    client = OTClient(url="http://localhost:5000")
    
    # Check connection
    if not client.check_connection():
        print("Error: Cannot connect to server!")
        print("错误：无法连接到服务器！")
        print("Please start the server first:")
        print("请先启动服务器：")
        print("  python online_game/ot_server.py")
        return
    
    print("Connected to server successfully!")
    print("成功连接到服务器！\n")
    
    # Create sample observation and masks
    # In real usage, these should be actual game state data
    obs = [[0.0] * 100]  # Simplified observation
    masks = [[True] + [False] * 46]  # Only first action is valid
    
    # Get AI decision
    try:
        result = client.get_decision(obs, masks)
        print(f"AI selected action: {result['actions'][0]}")
        print(f"AI 选择的动作: {result['actions'][0]}")
        print(f"Q-values: {result['q_out'][0][:5]}... (showing first 5)")
        print(f"Q值: {result['q_out'][0][:5]}... (显示前5个)")
        print(f"Is greedy: {result['is_greedy'][0]}")
        print(f"是否贪婪: {result['is_greedy'][0]}\n")
    except Exception as e:
        print(f"Error: {e}")
        print(f"错误: {e}\n")


def example_with_authentication():
    """Example with API key authentication / 带 API 密钥认证的示例"""
    print("=== Authentication Example ===")
    print("=== 认证示例 ===\n")
    
    # Create client with API key
    api_key = "your-secret-key"
    client = OTClient(url="http://localhost:5000", api_key=api_key)
    
    print(f"Using API key: {api_key}")
    print(f"使用 API 密钥: {api_key}\n")
    
    # Note: This will only work if the server was started with --api-key
    # 注意：只有在服务器使用 --api-key 启动时才有效
    
    if not client.check_connection():
        print("Cannot connect to server or authentication failed")
        print("无法连接到服务器或认证失败")
        return
    
    print("Authentication successful!")
    print("认证成功！\n")


def example_batch_requests():
    """Example with multiple observations / 多个观察的批处理示例"""
    print("=== Batch Request Example ===")
    print("=== 批处理请求示例 ===\n")
    
    client = OTClient(url="http://localhost:5000")
    
    if not client.check_connection():
        print("Cannot connect to server")
        print("无法连接到服务器")
        return
    
    # Multiple observations
    obs = [
        [0.0] * 100,
        [0.1] * 100,
        [0.2] * 100,
    ]
    
    masks = [
        [True, False] + [False] * 45,
        [True, True, False] + [False] * 44,
        [True] + [False] * 46,
    ]
    
    try:
        result = client.get_decision(obs, masks)
        print(f"Batch size: {len(result['actions'])}")
        print(f"批处理大小: {len(result['actions'])}")
        print(f"Actions: {result['actions']}")
        print(f"动作: {result['actions']}\n")
    except Exception as e:
        print(f"Error: {e}")
        print(f"错误: {e}\n")


def example_3p_mode():
    """Example for 3-player mahjong / 三人麻将示例"""
    print("=== 3-Player Mode Example ===")
    print("=== 三人麻将模式示例 ===\n")
    
    client = OTClient(url="http://localhost:5000")
    
    if not client.check_connection():
        print("Cannot connect to server")
        print("无法连接到服务器")
        return
    
    obs = [[0.0] * 100]
    masks = [[True] + [False] * 46]
    
    try:
        # Use 3-player endpoint
        result = client.get_decision(obs, masks, use_3p=True)
        print(f"3P Action: {result['actions'][0]}")
        print(f"三麻动作: {result['actions'][0]}\n")
    except Exception as e:
        print(f"Error: {e}")
        print(f"错误: {e}\n")


def main():
    """Run all examples / 运行所有示例"""
    print("OT Server Client Examples")
    print("OT 服务器客户端示例")
    print("=" * 60)
    print()
    
    example_basic_usage()
    example_with_authentication()
    example_batch_requests()
    example_3p_mode()
    
    print("=" * 60)
    print("Examples completed!")
    print("示例完成！")
    print()
    print("Note: Make sure the OT server is running before running these examples:")
    print("注意：在运行这些示例之前，请确保 OT 服务器正在运行：")
    print("  python online_game/ot_server.py")


if __name__ == '__main__':
    main()
