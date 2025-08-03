#!/usr/bin/env python3
"""
测试aiocqhttp和AstrBot连接
"""

import requests
import json
import time

def test_connections():
    """测试连接"""
    print("🧪 测试连接...")
    
    # 1. 测试aiocqhttp
    try:
        response = requests.get("http://127.0.0.1:5700/status", timeout=5)
        print(f"✅ aiocqhttp状态: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 状态: {data.get('status', 'Unknown')}")
    except Exception as e:
        print(f"❌ aiocqhttp连接失败: {e}")
    
    # 2. 测试AstrBot
    try:
        response = requests.get("http://localhost:6185/api/auth/login", timeout=5)
        print(f"✅ AstrBot状态: {response.status_code}")
    except Exception as e:
        print(f"❌ AstrBot连接失败: {e}")
    
    # 3. 测试消息发送
    try:
        test_data = {
            "action": "send_msg",
            "params": {
                "message_type": "private",
                "user_id": 2078641650,
                "message": "测试消息"
            }
        }
        response = requests.post("http://127.0.0.1:5700/send_msg", json=test_data, timeout=5)
        print(f"✅ 消息发送测试: {response.status_code}")
    except Exception as e:
        print(f"❌ 消息发送测试失败: {e}")

if __name__ == "__main__":
    test_connections()
