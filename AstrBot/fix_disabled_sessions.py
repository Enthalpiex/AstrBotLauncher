#!/usr/bin/env python3
"""
修复被禁用的aiocqhttp会话
"""

import json
import os

def fix_disabled_sessions():
    """启用所有被禁用的aiocqhttp会话"""
    print("🔧 开始修复被禁用的aiocqhttp会话...")
    
    try:
        # 读取共享偏好文件
        with open('data/shared_preferences.json', 'r', encoding='utf-8-sig') as f:
            prefs = json.load(f)
        
        session_config = prefs.get('session_service_config', {})
        aiocqhttp_sessions = {k: v for k, v in session_config.items() if k.startswith('aiocqhttp')}
        
        print(f"📊 找到 {len(aiocqhttp_sessions)} 个aiocqhttp会话")
        
        # 检查并启用被禁用的会话
        disabled_count = 0
        for session_id, config in aiocqhttp_sessions.items():
            if not config.get('session_enabled', False):
                config['session_enabled'] = True
                disabled_count += 1
                print(f"✅ 启用会话: {session_id}")
        
        if disabled_count > 0:
            # 保存修改
            prefs['session_service_config'] = session_config
            
            with open('data/shared_preferences.json', 'w', encoding='utf-8') as f:
                json.dump(prefs, f, ensure_ascii=False, indent=2)
            
            print(f"🎉 成功启用 {disabled_count} 个被禁用的会话")
        else:
            print("✅ 所有会话都已启用，无需修复")
        
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

if __name__ == "__main__":
    fix_disabled_sessions() 