#!/usr/bin/env python3
"""
AstrBot 自动修复脚本
"""

import json
import os
from pathlib import Path

def fix_astrbot():
    """修复AstrBot的常见问题"""
    
    data_dir = Path("data")
    shared_prefs_file = data_dir / "shared_preferences.json"
    
    if not shared_prefs_file.exists():
        print("❌ 找不到配置文件")
        return
    
    # 读取配置
    with open(shared_prefs_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    fixed = False
    
    # 修复会话状态
    session_config = config.get("session_service_config", {})
    for session_id, session_data in session_config.items():
        if session_data.get("session_enabled") == False:
            session_data["session_enabled"] = True
            print(f"✅ 已启用会话: {session_id}")
            fixed = True
    
    # 保存修复后的配置
    if fixed:
        with open(shared_prefs_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        print("✅ 配置已修复，请重启AstrBot")
    else:
        print("✅ 没有发现需要修复的问题")

if __name__ == "__main__":
    fix_astrbot()
