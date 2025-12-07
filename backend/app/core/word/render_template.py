"""Word 模板渲染模块

使用 python-docx-template 渲染 Word 模板
"""

from io import BytesIO
from pathlib import Path
from typing import Any

from docx.shared import Mm
from docxtpl import DocxTemplate, InlineImage


def render_template(
    template_path: Path,
    context: dict[str, Any],
    output_path: Path | None = None,
) -> bytes:
    """渲染 Word 模板

    Args:
        template_path: 模板文件路径
        context: 渲染上下文数据
        output_path: 输出路径，为 None 时返回字节数据

    Returns:
        bytes: 渲染后的 Word 文档字节数据

    Raises:
        FileNotFoundError: 模板文件不存在
        ValueError: 模板渲染失败
    """
    if not template_path.exists():
        raise FileNotFoundError(f"模板文件不存在: {template_path}")

    doc = DocxTemplate(template_path)
    doc.render(context)

    # 保存到字节流
    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    data = buf.read()

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(data)

    return data


def render_template_with_images(
    template_path: Path,
    context: dict[str, Any],
    images: dict[str, bytes | Path],
    image_width_mm: int = 150,
    output_path: Path | None = None,
) -> bytes:
    """渲染带图片的 Word 模板

    Args:
        template_path: 模板文件路径
        context: 渲染上下文数据
        images: 图片字典，格式为 {占位符名: 图片字节或路径}
        image_width_mm: 图片宽度（毫米）
        output_path: 输出路径

    Returns:
        bytes: 渲染后的 Word 文档字节数据
    """
    if not template_path.exists():
        raise FileNotFoundError(f"模板文件不存在: {template_path}")

    doc = DocxTemplate(template_path)

    # 处理图片
    image_context = {}
    for name, img_data in images.items():
        if isinstance(img_data, Path):
            if not img_data.exists():
                continue
            image_context[name] = InlineImage(
                doc, str(img_data), width=Mm(image_width_mm)
            )
        elif isinstance(img_data, bytes) and len(img_data) > 0:
            # 字节数据需要先写入临时文件
            img_buf = BytesIO(img_data)
            image_context[name] = InlineImage(doc, img_buf, width=Mm(image_width_mm))

    # 合并上下文
    full_context = {**context, **image_context}
    doc.render(full_context)

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    data = buf.read()

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(data)

    return data


def create_inline_image(
    doc: DocxTemplate,
    image_data: bytes | Path,
    width_mm: int = 150,
) -> InlineImage | None:
    """创建内联图片对象

    Args:
        doc: DocxTemplate 文档对象
        image_data: 图片字节数据或路径
        width_mm: 图片宽度（毫米）

    Returns:
        InlineImage 对象，创建失败返回 None
    """
    if isinstance(image_data, Path):
        if not image_data.exists():
            return None
        return InlineImage(doc, str(image_data), width=Mm(width_mm))
    elif isinstance(image_data, bytes) and len(image_data) > 0:
        img_buf = BytesIO(image_data)
        return InlineImage(doc, img_buf, width=Mm(width_mm))
    return None
