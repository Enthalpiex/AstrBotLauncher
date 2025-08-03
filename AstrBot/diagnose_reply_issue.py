#!/usr/bin/env python3
"""
诊断AstrBot不回复问题
"""

import json
import os
from pathlib import Path

def check_config_file():
    """检查配置文件"""
    config_path = "data/cmd_config.json"
    print("🔍 检查配置文件...")
    
    if not os.path.exists(config_path):
        print("❌ 配置文件不存在")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ 配置文件存在")
        
        # 检查关键配置
        platform_settings = config.get("platform_settings", {})
        
        # 检查白名单设置
        enable_whitelist = platform_settings.get("enable_id_white_list", False)
        whitelist = platform_settings.get("id_whitelist", [])
        print(f"📋 白名单检查: {'启用' if enable_whitelist else '禁用'}")
        if enable_whitelist and whitelist:
            print(f"   📝 白名单内容: {whitelist}")
        
        # 检查唤醒前缀
        wake_prefixes = config.get("wake_prefix", [])
        print(f"🔔 唤醒前缀: {wake_prefixes}")
        
        # 检查私聊设置
        friend_needs_wake = platform_settings.get("friend_message_needs_wake_prefix", False)
        print(f"💬 私聊需要唤醒前缀: {'是' if friend_needs_wake else '否'}")
        
        # 检查管理员设置
        admins = config.get("admins_id", [])
        print(f"👑 管理员列表: {admins}")
        
        # 检查提供商设置
        provider_settings = config.get("provider_settings", {})
        provider_enabled = provider_settings.get("enable", False)
        print(f"🤖 提供商启用: {'是' if provider_enabled else '否'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        return False

def check_shared_preferences():
    """检查共享偏好设置"""
    prefs_path = "data/shared_preferences.json"
    print("\n🔍 检查共享偏好设置...")
    
    if not os.path.exists(prefs_path):
        print("❌ 共享偏好文件不存在")
        return False
    
    try:
        with open(prefs_path, 'r', encoding='utf-8') as f:
            prefs = json.load(f)
        
        print("✅ 共享偏好文件存在")
        
        # 检查会话状态
        session_config = prefs.get("session_service_config", {})
        print(f"📊 会话配置数量: {len(session_config)}")
        
        # 检查aiocqhttp会话
        aiocqhttp_sessions = {k: v for k, v in session_config.items() if k.startswith("aiocqhttp")}
        print(f"🤖 aiocqhttp会话数量: {len(aiocqhttp_sessions)}")
        
        for session_id, config in aiocqhttp_sessions.items():
            session_enabled = config.get("session_enabled", False)
            tts_enabled = config.get("tts_enabled", False)
            print(f"   📱 {session_id}: 会话启用={session_enabled}, TTS启用={tts_enabled}")
        
        # 检查会话映射
        session_mappings = prefs.get("session_conversation", {})
        aiocqhttp_mappings = {k: v for k, v in session_mappings.items() if k.startswith("aiocqhttp")}
        print(f"🔗 aiocqhttp会话映射数量: {len(aiocqhttp_mappings)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 读取共享偏好文件失败: {e}")
        return False

def check_logs():
    """检查日志文件"""
    print("\n🔍 检查日志文件...")
    
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        print("❌ 日志目录不存在")
        return False
    
    print("✅ 日志目录存在")
    
    # 查找最新的日志文件
    log_files = []
    for file in os.listdir(logs_dir):
        if file.endswith('.log'):
            log_files.append(os.path.join(logs_dir, file))
    
    if not log_files:
        print("❌ 没有找到日志文件")
        return False
    
    # 按修改时间排序
    log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    latest_log = log_files[0]
    
    print(f"📄 最新日志文件: {os.path.basename(latest_log)}")
    
    # 读取最后几行日志
    try:
        with open(latest_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            last_lines = lines[-20:]  # 最后20行
        
        print("📋 最新日志内容:")
        for line in last_lines:
            line = line.strip()
            if line and ("ERROR" in line or "WARNING" in line or "INFO" in line):
                print(f"   {line}")
                
    except Exception as e:
        print(f"❌ 读取日志文件失败: {e}")
    
    return True

def check_database():
    """检查数据库"""
    print("\n🔍 检查数据库...")
    
    db_path = "data/data_v3.db"
    if not os.path.exists(db_path):
        print("❌ 数据库文件不存在")
        return False
    
    print("✅ 数据库文件存在")
    
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查webchat_conversation表
        cursor.execute("SELECT COUNT(*) FROM webchat_conversation WHERE user_id LIKE 'aiocqhttp%'")
        count = cursor.fetchone()[0]
        print(f"📊 aiocqhttp对话记录数量: {count}")
        
        # 检查最近的对话
        cursor.execute("""
            SELECT user_id, cid, created_at 
            FROM webchat_conversation 
            WHERE user_id LIKE 'aiocqhttp%' 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        recent_conversations = cursor.fetchall()
        
        if recent_conversations:
            print("📝 最近的aiocqhttp对话:")
            for conv in recent_conversations:
                print(f"   {conv[0]} -> {conv[1]} ({conv[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 检查数据库失败: {e}")
        return False

def generate_fix_script():
    """生成修复脚本"""
    print("\n🔧 生成修复脚本...")
    
    fix_script = '''#!/usr/bin/env python3
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
'''
    
    with open("fix_reply_issue.py", 'w', encoding='utf-8') as f:
        f.write(fix_script)
    
    print("✅ 修复脚本已生成: fix_reply_issue.py")

def main():
    """主函数"""
    print("🔍 AstrBot不回复问题诊断工具")
    print("=" * 50)
    
    # 检查各项配置
    config_ok = check_config_file()
    prefs_ok = check_shared_preferences()
    logs_ok = check_logs()
    db_ok = check_database()
    
    print("\n" + "=" * 50)
    print("📊 诊断结果:")
    print(f"   配置文件: {'✅ 正常' if config_ok else '❌ 异常'}")
    print(f"   共享偏好: {'✅ 正常' if prefs_ok else '❌ 异常'}")
    print(f"   日志文件: {'✅ 正常' if logs_ok else '❌ 异常'}")
    print(f"   数据库: {'✅ 正常' if db_ok else '❌ 异常'}")
    
    # 生成修复脚本
    generate_fix_script()
    
    print("\n💡 建议:")
    print("1. 运行修复脚本: python fix_reply_issue.py")
    print("2. 重启AstrBot")
    print("3. 检查日志文件查看详细错误信息")
    print("4. 确保aiocqhttp连接正常")

if __name__ == "__main__":
    main() 