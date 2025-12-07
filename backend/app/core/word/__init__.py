"""Word 生成模块

提供 Word 文档的模板渲染和图表插入功能
"""

from app.core.word.insert_chart import (
    create_document_with_charts,
    insert_image_to_document,
    insert_table_from_data,
)
from app.core.word.render_template import (
    create_inline_image,
    render_template,
    render_template_with_images,
)

__all__ = [
    # 模板渲染
    "render_template",
    "render_template_with_images",
    "create_inline_image",
    # 图表插入
    "insert_image_to_document",
    "insert_table_from_data",
    "create_document_with_charts",
]
