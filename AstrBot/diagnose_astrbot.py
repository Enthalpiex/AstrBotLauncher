#!/usr/bin/env python3
"""
AstrBot 全面诊断脚本
检查会话状态、数据库、配置文件等所有潜在问题
"""

import json
import os
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple

def check_shared_preferences():
    """检查shared_preferences.json文件"""
    print("🔍 检查 shared_preferences.json 文件...")
    
    data_dir = Path("data")
    shared_prefs_file = data_dir / "shared_preferences.json"
    
    if not shared_prefs_file.exists():
        print("❌ 找不到 shared_preferences.json 文件")
        return False
    
    try:
        with open(shared_prefs_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ 读取 shared_preferences.json 失败: {e}")
        return False
    
    issues = []
    
    # 检查会话状态
    session_config = config.get("session_service_config", {})
    disabled_sessions = []
    for session_id, session_data in session_config.items():
        if session_data.get("session_enabled") == False:
            disabled_sessions.append(session_id)
    
    if disabled_sessions:
        issues.append(f"发现 {len(disabled_sessions)} 个被禁用的会话")
        for session in disabled_sessions:
            print(f"   - 禁用: {session}")
    
    # 检查会话-对话映射
    session_conversations = config.get("session_conversation", {})
    aiocqhttp_mappings = {k: v for k, v in session_conversations.items() if k.startswith("aiocqhttp")}
    
    if not aiocqhttp_mappings:
        issues.append("没有发现aiocqhttp的会话-对话映射关系")
        print("   - 缺少aiocqhttp会话映射")
    
    # 检查提供商配置
    session_provider_perf = config.get("session_provider_perf", {})
    aiocqhttp_providers = {k: v for k, v in session_provider_perf.items() if k.startswith("aiocqhttp")}
    
    if not aiocqhttp_providers:
        issues.append("没有发现aiocqhttp的提供商配置")
        print("   - 缺少aiocqhttp提供商配置")
    
    if not issues:
        print("✅ shared_preferences.json 配置正常")
        return True
    else:
        print(f"⚠️  发现 {len(issues)} 个问题")
        return False

def check_database():
    """检查数据库文件"""
    print("\n🔍 检查数据库文件...")
    
    data_dir = Path("data")
    db_file = data_dir / "data_v3.db"
    
    if not db_file.exists():
        print("❌ 找不到数据库文件 data_v3.db")
        return False
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # 检查表结构
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        if "webchat_conversation" not in tables:
            print("❌ 数据库缺少 webchat_conversation 表")
            return False
        
        # 检查aiocqhttp对话记录
        cursor.execute("""
            SELECT COUNT(*) FROM webchat_conversation 
            WHERE user_id LIKE 'aiocqhttp%'
        """)
        aiocqhttp_count = cursor.fetchone()[0]
        
        print(f"📊 数据库统计:")
        print(f"   - aiocqhttp对话记录: {aiocqhttp_count} 条")
        
        # 检查最近的对话
        cursor.execute("""
            SELECT user_id, cid, updated_at, title 
            FROM webchat_conversation 
            WHERE user_id LIKE 'aiocqhttp%'
            ORDER BY updated_at DESC 
            LIMIT 5
        """)
        recent_conversations = cursor.fetchall()
        
        if recent_conversations:
            print(f"   - 最近的aiocqhttp对话:")
            for user_id, cid, updated_at, title in recent_conversations:
                print(f"     * {user_id} -> {cid[:8]}... ({title or '无标题'})")
        else:
            print("   - 没有发现aiocqhttp对话记录")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")
        return False

def check_logs():
    """检查日志文件"""
    print("\n🔍 检查日志文件...")
    
    log_dir = Path("logs")
    if not log_dir.exists():
        print("⚠️  找不到logs目录")
        return
    
    log_files = list(log_dir.glob("*.log"))
    if not log_files:
        print("⚠️  没有找到日志文件")
        return
    
    # 检查最新的日志文件
    latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
    print(f"📄 最新日志文件: {latest_log.name}")
    
    try:
        with open(latest_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            recent_lines = lines[-50:]  # 最近50行
            
            # 查找错误和警告
            errors = [line for line in recent_lines if 'ERROR' in line or 'error' in line.lower()]
            warnings = [line for line in recent_lines if 'WARNING' in line or 'warning' in line.lower()]
            
            if errors:
                print(f"⚠️  发现 {len(errors)} 个错误:")
                for error in errors[-5:]:  # 显示最近5个错误
                    print(f"   - {error.strip()}")
            
            if warnings:
                print(f"⚠️  发现 {len(warnings)} 个警告:")
                for warning in warnings[-5:]:  # 显示最近5个警告
                    print(f"   - {warning.strip()}")
                    
    except Exception as e:
        print(f"❌ 读取日志文件失败: {e}")

def generate_fix_script():
    """生成修复脚本"""
    print("\n🔧 生成修复脚本...")
    
    fix_script = '''#!/usr/bin/env python3
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
'''
    
    with open("fix_astrbot.py", "w", encoding="utf-8") as f:
        f.write(fix_script)
    
    print("✅ 已生成修复脚本: fix_astrbot.py")

def main():
    """主诊断函数"""
    print("🚀 AstrBot 全面诊断开始...\n")
    
    # 检查各个组件
    prefs_ok = check_shared_preferences()
    db_ok = check_database()
    check_logs()
    
    print("\n" + "="*50)
    print("📋 诊断总结:")
    
    if prefs_ok and db_ok:
        print("✅ 所有检查项目正常")
    else:
        print("⚠️  发现一些问题，建议运行修复脚本")
        generate_fix_script()
    
    print("\n💡 建议:")
    print("1. 如果发现问题，运行: python fix_astrbot.py")
    print("2. 重启AstrBot: python main.py")
    print("3. 检查aiocqhttp连接状态")
    print("4. 查看详细日志: tail -f logs/astrbot.log")

if __name__ == "__main__":
    main() 