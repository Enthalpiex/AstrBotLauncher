#!/usr/bin/env python3
"""
测试AstrBot基本功能
"""

import json
import os

def test_basic_functionality():
    """测试基本功能"""
    print("🧪 测试AstrBot基本功能...")
    
    # 1. 测试配置文件读取
    try:
        with open('data/cmd_config.json', 'r', encoding='utf-8-sig') as f:
            config = json.load(f)
        print("✅ 配置文件读取正常")
    except Exception as e:
        print(f"❌ 配置文件读取失败: {e}")
        return False
    
    # 2. 测试共享偏好读取
    try:
        with open('data/shared_preferences.json', 'r', encoding='utf-8-sig') as f:
            prefs = json.load(f)
        print("✅ 共享偏好读取正常")
    except Exception as e:
        print(f"❌ 共享偏好读取失败: {e}")
        return False
    
    # 3. 测试数据库连接
    try:
        import sqlite3
        conn = sqlite3.connect('data/data_v3.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM webchat_conversation")
        count = cursor.fetchone()[0]
        print(f"✅ 数据库连接正常，对话记录: {count}")
        conn.close()
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False
    
    # 4. 测试日志写入
    try:
        logs_dir = "logs"
        os.makedirs(logs_dir, exist_ok=True)
        test_log = os.path.join(logs_dir, "test.log")
        with open(test_log, 'w', encoding='utf-8') as f:
            f.write("测试日志\n")
        print("✅ 日志写入正常")
        os.remove(test_log)
    except Exception as e:
        print(f"❌ 日志写入失败: {e}")
        return False
    
    print("🎉 基本功能测试通过")
    return True

if __name__ == "__main__":
    test_basic_functionality()
