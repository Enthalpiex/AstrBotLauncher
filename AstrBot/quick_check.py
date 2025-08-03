#!/usr/bin/env python3
import json
import os

print("🔍 快速检查AstrBot配置...")

# 检查配置文件
try:
    with open('data/cmd_config.json', 'r', encoding='utf-8-sig') as f:
        config = json.load(f)
    
    provider_enabled = config.get('provider_settings', {}).get('enable', False)
    wake_prefixes = config.get('wake_prefix', [])
    friend_needs_wake = config.get('platform_settings', {}).get('friend_message_needs_wake_prefix', False)
    
    print(f"✅ 提供商启用: {provider_enabled}")
    print(f"✅ 唤醒前缀: {wake_prefixes}")
    print(f"✅ 私聊需要唤醒: {friend_needs_wake}")
    
except Exception as e:
    print(f"❌ 配置文件错误: {e}")

# 检查共享偏好
try:
    with open('data/shared_preferences.json', 'r', encoding='utf-8-sig') as f:
        prefs = json.load(f)
    
    session_config = prefs.get('session_service_config', {})
    aiocqhttp_sessions = {k: v for k, v in session_config.items() if k.startswith('aiocqhttp')}
    
    print(f"✅ aiocqhttp会话数量: {len(aiocqhttp_sessions)}")
    
    disabled_sessions = []
    for session_id, config in aiocqhttp_sessions.items():
        if not config.get('session_enabled', False):
            disabled_sessions.append(session_id)
    
    if disabled_sessions:
        print(f"❌ 禁用的会话: {disabled_sessions}")
    else:
        print("✅ 所有aiocqhttp会话都已启用")
        
except Exception as e:
    print(f"❌ 共享偏好错误: {e}")

# 检查日志目录
if os.path.exists('logs'):
    print("✅ 日志目录存在")
    log_files = [f for f in os.listdir('logs') if f.endswith('.log')]
    if log_files:
        print(f"✅ 找到 {len(log_files)} 个日志文件")
    else:
        print("❌ 没有日志文件")
else:
    print("❌ 日志目录不存在")

print("\n💡 可能的问题:")
print("1. 白名单检查 - 检查是否启用了白名单且您的会话不在白名单中")
print("2. 唤醒检查 - 确保消息以 '/' 开头或@了机器人")
print("3. 插件错误 - 检查日志文件中的错误信息")
print("4. 网络连接 - 确保aiocqhttp连接正常") 