"""本地 SQLite 数据库管理"""

import json
import aiosqlite
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.config import get_settings


class Database:
    """SQLite 数据库管理类"""

    def __init__(self) -> None:
        settings = get_settings()
        self.db_path = settings.BASE_DIR / "data" / "projects.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    async def init_db(self) -> None:
        """初始化数据库表"""
        async with aiosqlite.connect(self.db_path) as db:
            # 地区项目表
            await db.execute("""
                CREATE TABLE IF NOT EXISTS regions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    item TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(name, category, topic, item)
                )
            """)

            # 项目数据表
            await db.execute("""
                CREATE TABLE IF NOT EXISTS project_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    region_id INTEGER NOT NULL,
                    data_type TEXT NOT NULL,
                    data_content TEXT NOT NULL,
                    file_name TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (region_id) REFERENCES regions(id) ON DELETE CASCADE
                )
            """)

            # 项目配置表
            await db.execute("""
                CREATE TABLE IF NOT EXISTS project_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    region_id INTEGER NOT NULL UNIQUE,
                    config_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (region_id) REFERENCES regions(id) ON DELETE CASCADE
                )
            """)

            await db.commit()

    async def create_region(
        self,
        name: str,
        category: str,
        topic: str,
        item: str,
    ) -> int:
        """创建新地区项目

        Args:
            name: 地区名称
            category: 大类
            topic: 专题
            item: 具体项目

        Returns:
            新创建的地区ID
        """
        now = datetime.now().isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO regions (name, category, topic, item, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (name, category, topic, item, now, now),
            )
            await db.commit()
            return cursor.lastrowid or 0

    async def get_regions(
        self,
        category: Optional[str] = None,
        topic: Optional[str] = None,
        item: Optional[str] = None,
    ) -> list[dict]:
        """获取地区列表

        Args:
            category: 筛选大类
            topic: 筛选专题
            item: 筛选具体项目

        Returns:
            地区列表
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row

            query = "SELECT * FROM regions WHERE 1=1"
            params: list = []

            if category:
                query += " AND category = ?"
                params.append(category)
            if topic:
                query += " AND topic = ?"
                params.append(topic)
            if item:
                query += " AND item = ?"
                params.append(item)

            query += " ORDER BY updated_at DESC"

            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()

            return [dict(row) for row in rows]

    async def get_region_by_id(self, region_id: int) -> Optional[dict]:
        """根据ID获取地区"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM regions WHERE id = ?", (region_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def update_region(self, region_id: int, name: str) -> bool:
        """更新地区名称"""
        now = datetime.now().isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE regions SET name = ?, updated_at = ? WHERE id = ?",
                (name, now, region_id),
            )
            await db.commit()
            return True

    async def delete_region(self, region_id: int) -> bool:
        """删除地区及其所有数据"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM regions WHERE id = ?", (region_id,))
            await db.commit()
            return True

    async def save_project_data(
        self,
        region_id: int,
        data_type: str,
        data_content: str,
        file_name: Optional[str] = None,
    ) -> int:
        """保存项目数据（覆盖已有数据）

        Args:
            region_id: 地区ID
            data_type: 数据类型 (raw_data, processed_data, chart_data 等)
            data_content: 数据内容 (JSON 字符串)
            file_name: 原始文件名

        Returns:
            数据ID
        """
        now = datetime.now().isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            # 先删除同类型的旧数据
            await db.execute(
                "DELETE FROM project_data WHERE region_id = ? AND data_type = ?",
                (region_id, data_type),
            )

            # 插入新数据
            cursor = await db.execute(
                """
                INSERT INTO project_data
                (region_id, data_type, data_content, file_name, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (region_id, data_type, data_content, file_name, now, now),
            )
            await db.commit()

            # 更新地区的更新时间
            await db.execute(
                "UPDATE regions SET updated_at = ? WHERE id = ?",
                (now, region_id),
            )
            await db.commit()

            return cursor.lastrowid or 0

    async def get_project_data(
        self, region_id: int, data_type: Optional[str] = None
    ) -> list[dict]:
        """获取项目数据"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row

            if data_type:
                cursor = await db.execute(
                    "SELECT * FROM project_data WHERE region_id = ? AND data_type = ?",
                    (region_id, data_type),
                )
            else:
                cursor = await db.execute(
                    "SELECT * FROM project_data WHERE region_id = ?", (region_id,)
                )

            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def save_project_config(self, region_id: int, config: dict) -> None:
        """保存项目配置"""
        now = datetime.now().isoformat()
        config_json = json.dumps(config, ensure_ascii=False)

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO project_config (region_id, config_json, updated_at)
                VALUES (?, ?, ?)
                """,
                (region_id, config_json, now),
            )
            await db.commit()

    async def get_project_config(self, region_id: int) -> Optional[dict]:
        """获取项目配置"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM project_config WHERE region_id = ?", (region_id,)
            )
            row = await cursor.fetchone()

            if row:
                return json.loads(row["config_json"])
            return None


# 全局数据库实例
db = Database()
