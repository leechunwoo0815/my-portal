#!/usr/bin/env python3
"""修复数据库schema: 添加缺失列和默认配置"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ai_portal.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查并添加 shares_count 列
tables = ['solutions', 'projects', 'products', 'news', 'moments']
for table in tables:
    cursor.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cursor.fetchall()]
    if 'shares_count' not in cols:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN shares_count INTEGER DEFAULT 0")
        print(f"✅ {table}.shares_count 已添加")
    else:
        print(f"  {table}.shares_count 已存在")

# 检查并添加 system_configs 默认记录
cursor.execute("SELECT COUNT(*) FROM system_configs")
count = cursor.fetchone()[0]
if count == 0:
    configs = [
        ('site_name', 'AI技术门户', '站点名称'),
        ('site_description', 'AI技术分享与交流平台', '站点描述'),
        ('daily_chat_limit', '50', '每日对话限制次数'),
        ('register_enabled', 'true', '是否开放用户注册'),
        ('default_model', 'deepseek-chat', '默认AI对话模型'),
        ('max_upload_size_mb', '10', '最大上传文件大小(MB)'),
        ('comment_audit', 'false', '评论是否需要审核'),
        ('moment_level_required', '2', '发布动态所需最低等级'),
    ]
    from datetime import datetime
    now = datetime.now().isoformat()
    cursor.executemany(
        "INSERT INTO system_configs (key, value, description, updated_at) VALUES (?, ?, ?, ?)",
        [(k, v, d, now) for k, v, d in configs]
    )
    print(f"✅ 已插入 {len(configs)} 条默认系统配置")
else:
    print(f"  system_configs 已有 {count} 条记录")

conn.commit()
conn.close()
print("✅ 数据库修复完成")
