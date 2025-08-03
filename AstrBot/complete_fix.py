#!/usr/bin/env python3
"""
AstrBot 完整修复脚本
解决会话状态、映射关系等所有问题
"""

import json
import os
import sqlite3
from pathlib import Path
from typing import Dict, List

def fix_session_mappings():
    """修复会话-对话映射关系"""
    print("🔧 修复会话-对话映射关系...")
    
    data_dir = Path("data")
    shared_prefs_file = data_dir / "shared_preferences.json"
    db_file = data_dir / "data_v3.db"
    
    if not shared_prefs_file.exists():
        print("❌ 找不到配置文件")
        return False
    
    if not db_file.exists():
        print("❌ 找不到数据库文件")
        return False
    
    # 读取配置
    with open(shared_prefs_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 连接数据库
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # 获取所有aiocqhttp对话记录
    cursor.execute("""
        SELECT user_id, cid, updated_at 
        FROM webchat_conversation 
        WHERE user_id LIKE 'aiocqhttp%'
        ORDER BY updated_at DESC
    """)
    conversations = cursor.fetchall()
    
    # 为每个会话创建映射关系
    session_conversations = config.get("session_conversation", {})
    fixed_mappings = 0
    
    for user_id, cid, updated_at in conversations:
        if user_id not in session_conversations:
            session_conversations[user_id] = cid
            print(f"✅ 添加映射: {user_id} -> {cid[:8]}...")
            fixed_mappings += 1
    
    # 更新配置
    config["session_conversation"] = session_conversations
    
    # 保存配置
    with open(shared_prefs_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    
    conn.close()
    
    if fixed_mappings > 0:
        print(f"✅ 已修复 {fixed_mappings} 个映射关系")
        return True
    else:
        print("✅ 映射关系正常")
        return False

def fix_session_status():
    """修复会话状态"""
    print("🔧 修复会话状态...")
    
    data_dir = Path("data")
    shared_prefs_file = data_dir / "shared_preferences.json"
    
    if not shared_prefs_file.exists():
        print("❌ 找不到配置文件")
        return False
    
    # 读取配置
    with open(shared_prefs_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 修复会话状态
    session_config = config.get("session_service_config", {})
    fixed_sessions = 0
    
    for session_id, session_data in session_config.items():
        if session_data.get("session_enabled") == False:
            session_data["session_enabled"] = True
            print(f"✅ 启用会话: {session_id}")
            fixed_sessions += 1
    
    # 保存配置
    with open(shared_prefs_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    
    if fixed_sessions > 0:
        print(f"✅ 已启用 {fixed_sessions} 个会话")
        return True
    else:
        print("✅ 会话状态正常")
        return False

def create_logs_directory():
    """创建日志目录"""
    print("🔧 创建日志目录...")
    
    logs_dir = Path("logs")
    if not logs_dir.exists():
        logs_dir.mkdir(exist_ok=True)
        print("✅ 已创建logs目录")
        return True
    else:
        print("✅ logs目录已存在")
        return False

def main():
    """主修复函数"""
    print("🚀 AstrBot 完整修复开始...\n")
    
    # 执行各项修复
    mappings_fixed = fix_session_mappings()
    status_fixed = fix_session_status()
    logs_created = create_logs_directory()
    
    print("\n" + "="*50)
    print("📋 修复总结:")
    
    if mappings_fixed or status_fixed or logs_created:
        print("✅ 修复完成！")
        print("\n🔄 请重启AstrBot以使更改生效:")
        print("   python main.py")
        
        print("\n💡 重启后检查:")
        print("1. aiocqhttp机器人是否能正常回复")
        print("2. 管理面板中的会话状态")
        print("3. 日志文件是否正常生成")
    else:
        print("✅ 没有发现需要修复的问题")

if __name__ == "__main__":
    main() 