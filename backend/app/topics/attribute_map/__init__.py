"""属性图专题模块"""

from app.topics.attribute_map.data_process import process_attribute_data
from app.topics.attribute_map.mapping_process import process_mapping_data
from app.topics.attribute_map.topic import AttributeMapTopic

__all__ = ["process_attribute_data", "process_mapping_data", "AttributeMapTopic"]
