"""数据报告专题模块

处理土壤属性数据，生成包含多维度统计分析的Excel报告。
包含以下统计表：
1. 分乡镇统计
2. 土地利用类型统计
3. 土壤类型统计
4. 样点统计
5. 分行政区样点统计
6. 土地利用类型样点统计
7. 土壤类型样点统计
8. 全域属性统计汇总
9. 全域属性百分位数统计
"""

from app.topics.data_report.process import process_data_report

__all__ = ["process_data_report"]
