#!/usr/bin/env python3
"""
修复AstrBot不回复问题
"""

import json
import os

def fix_reply_issue():
    """修复不回复问题"""
    print("🔧 开始修复AstrBot不回复问题...")
    
    # 1. 检查并修复配置文件
    config_path = "data/cmd_config.json"
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 确保提供商启用
        if "provider_settings" not in config:
            config["provider_settings"] = {}
        config["provider_settings"]["enable"] = True
        
        # 确保有唤醒前缀
        if "wake_prefix" not in config:
            config["wake_prefix"] = ["/", "！", "！"]
        
        # 确保私聊不需要唤醒前缀
        if "platform_settings" not in config:
            config["platform_settings"] = {}
        config["platform_settings"]["friend_message_needs_wake_prefix"] = False
        
        # 保存配置
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print("✅ 配置文件已修复")
    
    # 2. 检查并修复共享偏好
    prefs_path = "data/shared_preferences.json"
    if os.path.exists(prefs_path):
        with open(prefs_path, 'r', encoding='utf-8') as f:
            prefs = json.load(f)
        
        # 确保所有aiocqhttp会话都启用
        session_config = prefs.get("session_service_config", {})
        for session_id, config in session_config.items():
            if session_id.startswith("aiocqhttp"):
                config["session_enabled"] = True
        
        prefs["session_service_config"] = session_config
        
        # 保存偏好
        with open(prefs_path, 'w', encoding='utf-8') as f:
            json.dump(prefs, f, ensure_ascii=False, indent=2)
        
        print("✅ 共享偏好已修复")
    
    print("🎉 修复完成！请重启AstrBot")

if __name__ == "__main__":
    fix_reply_issue()
