"""属性图数据处理模块（高性能版本）

针对百万级数据优化：
1. 预处理阶段一次性完成所有数据清洗和转换
2. 使用 groupby 聚合代替逐行迭代
3. 避免不必要的 DataFrame 复制
4. 使用 NumPy 向量化操作
5. 预计算所有分组统计结果
"""

import io
from collections.abc import Callable
from pathlib import Path

import pandas as pd
from openpyxl import Workbook

from app.core.data import (
    get_land_use_class,
    load_multiple_csv,
    normalize_dlmc_column,
    normalize_soil_type_columns,
)
from app.topics.attribute_map.config import (
    SOIL_ATTR_CONFIG,
    detect_available_attributes,
    get_grade_order,
)
from app.topics.attribute_map.stats import AttributeStats, compute_attribute_stats
from app.topics.attribute_map.texture_writer import write_texture_overall
from app.topics.attribute_map.writers import (
    write_land_use_summary,
    write_overall_summary,
    write_soil_type_summary,
    write_town_summary,
)


def process_attribute_data(
    sample_paths: list[str | Path],
    area_paths: list[str | Path],
    progress_callback: Callable[[int, str], None] | None = None,
) -> tuple[bool, bytes | str]:
    """处理属性图数据（高性能版本）

    优化策略：
    1. 数据只读取和清洗一次
    2. 使用 groupby 预计算所有分组统计
    3. 避免在循环中复制 DataFrame
    4. 向量化操作代替逐行迭代
    """
    try:
        if progress_callback:
            progress_callback(0, "正在读取样点数据...")

        df_sample = load_multiple_csv(sample_paths)

        if progress_callback:
            progress_callback(10, "正在读取制图数据...")

        df_area = load_multiple_csv(area_paths)

        if progress_callback:
            progress_callback(20, "正在预处理数据...")

        # ===== 数据预处理（只做一次）=====

        # 标准化列名
        for normalize_func in [normalize_dlmc_column, normalize_soil_type_columns]:
            try:
                df_sample = normalize_func(df_sample)
            except ValueError:
                pass
            try:
                df_area = normalize_func(df_area)
            except ValueError:
                pass

        # 检测可用属性
        available_attrs = detect_available_attributes(list(df_sample.columns))
        if not available_attrs:
            available_attrs = detect_available_attributes(list(df_area.columns))

        if progress_callback:
            progress_callback(25, f"检测到 {len(available_attrs)} 个可用属性")

        # ===== 数据类型转换（只做一次）=====

        # 转换所有属性列为数值型
        attr_cols = set()
        for orig_col, attr_key in available_attrs:
            if orig_col in df_sample.columns:
                if orig_col != attr_key:
                    df_sample = df_sample.rename(columns={orig_col: attr_key})
                attr_cols.add(attr_key)
            if orig_col in df_area.columns:
                if orig_col != attr_key:
                    df_area = df_area.rename(columns={orig_col: attr_key})
                attr_cols.add(attr_key)

        for col in attr_cols:
            if col in df_sample.columns:
                df_sample[col] = pd.to_numeric(df_sample[col], errors="coerce")
            if col in df_area.columns:
                df_area[col] = pd.to_numeric(df_area[col], errors="coerce")

        # 面积列转换
        if "面积" in df_area.columns:
            df_area["面积"] = pd.to_numeric(df_area["面积"], errors="coerce")

        # 土地利用分类（只做一次）
        if "DLMC" in df_sample.columns:
            land_use = df_sample["DLMC"].apply(get_land_use_class)
            df_sample[["一级", "二级"]] = pd.DataFrame(
                land_use.tolist(), index=df_sample.index
            )
        if "DLMC" in df_area.columns:
            land_use = df_area["DLMC"].apply(get_land_use_class)
            df_area[["一级", "二级"]] = pd.DataFrame(
                land_use.tolist(), index=df_area.index
            )

        # 土壤类型列标准化
        for col in ["YL", "TS"]:
            if col in df_sample.columns:
                df_sample[col] = df_sample[col].astype(str).str.strip()
            if col in df_area.columns:
                df_area[col] = df_area[col].astype(str).str.strip()

        if progress_callback:
            progress_callback(30, "正在计算统计数据...")

        # ===== 预计算所有属性的统计结果 =====

        all_stats: list[AttributeStats] = []
        total_attrs = len(available_attrs)

        for idx, (_, attr_key) in enumerate(available_attrs):
            if attr_key not in df_sample.columns and attr_key not in df_area.columns:
                continue

            if progress_callback:
                progress = 30 + int((idx / max(total_attrs, 1)) * 40)
                attr_name = SOIL_ATTR_CONFIG.get(attr_key, {}).get("name", attr_key)
                progress_callback(progress, f"正在计算: {attr_name}")

            grade_order = get_grade_order(attr_key)
            stats = compute_attribute_stats(df_sample, df_area, attr_key, grade_order)
            all_stats.append(stats)

        if not all_stats:
            return False, "未能处理任何属性数据"

        if progress_callback:
            progress_callback(70, "正在生成Excel...")

        # ===== 生成 Excel =====

        wb = Workbook()
        if wb.active:
            wb.remove(wb.active)

        for idx, stats in enumerate(all_stats):
            if progress_callback:
                progress = 70 + int((idx / len(all_stats)) * 20)
                progress_callback(progress, f"正在写入: {stats.attr_name}")

            grade_order = get_grade_order(stats.attr_key)

            ws1 = wb.create_sheet(title=f"{stats.attr_name}总体")
            write_overall_summary(ws1, stats, grade_order)

            ws2 = wb.create_sheet(title=f"{stats.attr_name}土地利用")
            write_land_use_summary(ws2, stats)

            ws3 = wb.create_sheet(title=f"{stats.attr_name}乡镇")
            write_town_summary(ws3, stats, grade_order)

            ws4 = wb.create_sheet(title=f"{stats.attr_name}土壤类型")
            write_soil_type_summary(ws4, stats)

        # 处理土壤质地
        if "TRZD" in df_sample.columns or "TRZD" in df_area.columns:
            if progress_callback:
                progress_callback(90, "正在处理土壤质地...")

            ws_texture = wb.create_sheet(title="土壤质地总体")
            write_texture_overall(ws_texture, df_sample, df_area)

        if progress_callback:
            progress_callback(95, "正在保存文件...")

        # 保存到字节流
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        if progress_callback:
            progress_callback(100, "完成！")

        return True, output.getvalue()

    except Exception as e:
        import traceback

        error_detail = traceback.format_exc()
        error_msg = f"处理数据时发生错误：{type(e).__name__}: {e}\n\n详细错误信息：\n{error_detail}"
        return False, error_msg


# =============================================================================
# 兼容性导出（保持原有函数名可用）
# =============================================================================

# 为了兼容可能的外部调用，保留原函数名作为别名
generate_overall_summary = write_overall_summary
generate_land_use_summary = write_land_use_summary
generate_town_summary = write_town_summary
generate_soil_type_summary = write_soil_type_summary
generate_texture_overall = write_texture_overall
