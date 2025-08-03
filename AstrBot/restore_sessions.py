#!/usr/bin/env python3
"""
AstrBot 会话恢复脚本
用于恢复被禁用的会话状态
"""

import json
import os
from pathlib import Path

def restore_sessions():
    """恢复所有被禁用的会话"""
    
    # 获取数据目录路径
    data_dir = Path("data")
    shared_prefs_file = data_dir / "shared_preferences.json"
    
    if not shared_prefs_file.exists():
        print("❌ 找不到 shared_preferences.json 文件")
        return
    
    # 读取配置文件
    with open(shared_prefs_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 获取会话配置
    session_config = config.get("session_service_config", {})
    
    # 统计需要恢复的会话
    disabled_sessions = []
    for session_id, session_data in session_config.items():
        if session_data.get("session_enabled") == False:
            disabled_sessions.append(session_id)
            session_data["session_enabled"] = True
    
    if not disabled_sessions:
        print("✅ 没有发现被禁用的会话")
        return
    
    # 保存修改后的配置
    with open(shared_prefs_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    
    print(f"✅ 已恢复 {len(disabled_sessions)} 个被禁用的会话:")
    for session in disabled_sessions:
        print(f"   - {session}")
    
    print("\n🔄 请重启 AstrBot 以使更改生效")

if __name__ == "__main__":
    restore_sessions() 