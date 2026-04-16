"""
记忆系统 - 支持 SQLite 和 Redis 存储
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

import aiosqlite
import redis.asyncio as redis


class Memory:
    """记忆系统"""
    
    def __init__(self, db_path: str = None, redis_url: str = None):
        self.db_path = db_path or os.getenv("MEMORY_DB", "./data/memory.db")
        self.redis_url = redis_url or os.getenv("REDIS_URL")
        self.use_redis = bool(self.redis_url)
        
        self._sqlite = None
        self._redis = None
    
    async def init(self):
        """初始化存储"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        if self.use_redis:
            self._redis = redis.from_url(self.redis_url, decode_responses=True)
        else:
            self._sqlite = await aiosqlite.connect(self.db_path)
            await self._init_sqlite()
    
    async def _init_sqlite(self):
        """初始化 SQLite 表"""
        await self._sqlite.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await self._sqlite.execute("""
            CREATE INDEX IF NOT EXISTS idx_session ON memory(session_id)
        """)
        await self._sqlite.commit()
    
    async def add(self, session_id: str, role: str, content: str, 
                  metadata: Dict = None) -> int:
        """添加记忆"""
        if self.use_redis:
            key = f"memory:{session_id}"
            entry = json.dumps({
                "role": role,
                "content": content,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat()
            }, ensure_ascii=False)
            await self._redis.rpush(key, entry)
            await self._redis.expire(key, 86400 * 30)  # 30天过期
            return await self._redis.llen(key)
        else:
            cursor = await self._sqlite.execute(
                """INSERT INTO memory (session_id, role, content, metadata) 
                   VALUES (?, ?, ?, ?)""",
                (session_id, role, content, json.dumps(metadata or {}))
            )
            await self._sqlite.commit()
            return cursor.lastrowid
    
    async def get_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """获取历史记忆"""
        if self.use_redis:
            key = f"memory:{session_id}"
            entries = await self._redis.lrange(key, -limit, -1)
            return [json.loads(e) for e in entries]
        else:
            cursor = await self._sqlite.execute(
                """SELECT role, content, metadata, created_at 
                   FROM memory 
                   WHERE session_id = ? 
                   ORDER BY created_at DESC 
                   LIMIT ?""",
                (session_id, limit)
            )
            rows = await cursor.fetchall()
            return [
                {
                    "role": row[0],
                    "content": row[1],
                    "metadata": json.loads(row[2]) if row[2] else {},
                    "timestamp": row[3]
                }
                for row in rows
            ]
    
    async def search(self, session_id: str, query: str) -> List[Dict]:
        """搜索记忆"""
        if self.use_redis:
            # Redis 简单关键词搜索
            key = f"memory:{session_id}"
            entries = await self._redis.lrange(key, 0, -1)
            results = []
            for e in entries:
                entry = json.loads(e)
                if query.lower() in entry["content"].lower():
                    results.append(entry)
            return results
        else:
            cursor = await self._sqlite.execute(
                """SELECT role, content, metadata, created_at 
                   FROM memory 
                   WHERE session_id = ? AND content LIKE ?""",
                (session_id, f"%{query}%")
            )
            rows = await cursor.fetchall()
            return [
                {
                    "role": row[0],
                    "content": row[1],
                    "metadata": json.loads(row[2]) if row[2] else {},
                    "timestamp": row[3]
                }
                for row in rows
            ]
    
    async def clear(self, session_id: str):
        """清除会话记忆"""
        if self.use_redis:
            await self._redis.delete(f"memory:{session_id}")
        else:
            await self._sqlite.execute(
                "DELETE FROM memory WHERE session_id = ?",
                (session_id,)
            )
            await self._sqlite.commit()
    
    async def close(self):
        """关闭连接"""
        if self._sqlite:
            await self._sqlite.close()
        if self._redis:
            await self._redis.close()
