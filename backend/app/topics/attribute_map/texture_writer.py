"""土壤质地统计写入函数"""

import pandas as pd

from app.topics.attribute_map.config import SOIL_TEXTURE_MAPPING
from app.topics.attribute_map.styles import (
    BOLD_FONT,
    CENTER,
    TITLE_FONT,
    apply_excel_styles,
    format_percentage,
    format_value,
)


def write_texture_overall(ws, df_sample: pd.DataFrame, df_area: pd.DataFrame) -> None:
    """写入土壤质地总体情况表（优化版）"""
    ws.title = "土壤质地总体情况"

    # 向量化映射 TRZD
    def map_trzd(trzd_series: pd.Series) -> pd.DataFrame:
        """向量化映射 TRZD 到质地信息"""
        results = []
        for val in trzd_series:
            if pd.isna(val) or str(val).strip() in {"0", "/", ""}:
                results.append((None, None, None))
            else:
                s = str(val).strip()
                results.append(SOIL_TEXTURE_MAPPING.get(s, ("其他", f"未知({s})", 99)))
        return pd.DataFrame(results, columns=["质地类别", "质地名称", "分级"])

    # 处理样点数据
    if "TRZD" in df_sample.columns:
        mapped = map_trzd(df_sample["TRZD"])
        df_sample = df_sample.copy()
        df_sample[["质地类别", "质地名称", "分级"]] = mapped.values
        df_sample = df_sample.dropna(subset=["质地类别"])

    # 处理面积数据
    if "TRZD" in df_area.columns:
        mapped = map_trzd(df_area["TRZD"])
        df_area = df_area.copy()
        df_area[["质地类别", "质地名称", "分级"]] = mapped.values
        df_area = df_area.dropna(subset=["质地类别"])
        if "面积" in df_area.columns:
            df_area["面积"] = pd.to_numeric(df_area["面积"], errors="coerce")
            df_area = df_area.dropna(subset=["面积"])

    total_sample_all = len(df_sample)
    total_area_all = df_area["面积"].sum() if "面积" in df_area.columns else 0

    # 预计算所有统计（使用 groupby）
    sample_counts = {}
    area_sums = {}

    if "质地名称" in df_sample.columns and len(df_sample) > 0:
        sample_counts = df_sample["质地名称"].value_counts().to_dict()

    if "质地名称" in df_area.columns and "面积" in df_area.columns and len(df_area) > 0:
        area_sums = df_area.groupby("质地名称", observed=True)["面积"].sum().to_dict()

    grade_to_roman = {1: "Ⅰ", 2: "Ⅱ", 3: "Ⅲ", 4: "Ⅳ", 5: "Ⅴ", 6: "Ⅵ", 7: "Ⅶ"}

    # 写入表头
    ws.merge_cells("A1:G1")
    ws["A1"] = "土壤质地分级分布统计"
    ws["A1"].font = TITLE_FONT
    ws["A1"].alignment = CENTER

    headers = ["分级", "质地类别", "质地名称", "频数/个", "频率/%", "面积/亩", "比例/%"]
    for i, h in enumerate(headers, 1):
        ws.cell(row=2, column=i, value=h)
        ws.cell(row=2, column=i).font = BOLD_FONT

    current_row = 3
    valid_grades = sorted({info[2] for info in SOIL_TEXTURE_MAPPING.values()})

    for grade in valid_grades:
        names_in_grade = [
            n for n, (_, _, g) in SOIL_TEXTURE_MAPPING.items() if g == grade
        ]
        cat_name = SOIL_TEXTURE_MAPPING[names_in_grade[0]][0]
        roman_grade = grade_to_roman.get(grade, str(grade))

        grade_sample_total = 0
        grade_area_total = 0.0

        for name in names_in_grade:
            count = sample_counts.get(name, 0)
            area_sum = area_sums.get(name, 0)
            freq = (
                round(count / total_sample_all * 100, 3) if total_sample_all > 0 else 0
            )
            area_pct = (
                round(area_sum / total_area_all * 100, 3) if total_area_all > 0 else 0
            )

            grade_sample_total += count
            grade_area_total += area_sum

            ws.cell(row=current_row, column=1, value=roman_grade)
            ws.cell(row=current_row, column=2, value=cat_name)
            ws.cell(row=current_row, column=3, value=name)
            ws.cell(row=current_row, column=4, value=count)
            ws.cell(row=current_row, column=5, value=format_percentage(freq))
            ws.cell(row=current_row, column=6, value=format_value(area_sum))
            ws.cell(row=current_row, column=7, value=format_percentage(area_pct))
            current_row += 1

        # 合计行（多名称时）
        if len(names_in_grade) > 1:
            freq = (
                round(grade_sample_total / total_sample_all * 100, 3)
                if total_sample_all > 0
                else 0
            )
            area_pct = (
                round(grade_area_total / total_area_all * 100, 3)
                if total_area_all > 0
                else 0
            )

            ws.cell(row=current_row, column=1, value=roman_grade)
            ws.cell(row=current_row, column=2, value=cat_name)
            ws.cell(row=current_row, column=3, value="合计")
            ws.cell(row=current_row, column=4, value=grade_sample_total)
            ws.cell(row=current_row, column=5, value=format_percentage(freq))
            ws.cell(row=current_row, column=6, value=format_value(grade_area_total))
            ws.cell(row=current_row, column=7, value=format_percentage(area_pct))
            current_row += 1

    # 全市合计
    ws.cell(row=current_row, column=1, value="全市")
    ws.cell(row=current_row, column=2, value="全市")
    ws.cell(row=current_row, column=3, value="全市")
    ws.cell(row=current_row, column=4, value=total_sample_all)
    ws.cell(row=current_row, column=5, value=100.0)
    ws.cell(row=current_row, column=6, value=format_value(total_area_all))
    ws.cell(row=current_row, column=7, value=100.0)

    apply_excel_styles(ws, current_row, 7)
