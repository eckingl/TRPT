"""专题模块"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.topics.base import BaseTopic

# 注册的专题列表
REGISTERED_TOPICS: list[type["BaseTopic"]] = []


def register_topic(topic_class: type["BaseTopic"]) -> type["BaseTopic"]:
    """注册专题装饰器"""
    REGISTERED_TOPICS.append(topic_class)
    return topic_class


def get_available_topics() -> list[dict[str, str]]:
    """获取所有可用专题列表"""
    return [
        {"id": topic.topic_id, "name": topic.topic_name} for topic in REGISTERED_TOPICS
    ]
