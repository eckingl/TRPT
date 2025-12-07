"""AI 客户端模块

支持通义千问和 DeepSeek 两种 AI 接口
"""

import os
from dataclasses import dataclass
from enum import Enum

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class AIProvider(Enum):
    """AI 提供商"""

    QWEN = "qwen"
    DEEPSEEK = "deepseek"


@dataclass
class AIConfig:
    """AI 配置"""

    provider: AIProvider
    api_key: str
    model: str


def get_ai_config(provider: str | None = None) -> AIConfig:
    """获取 AI 配置

    Args:
        provider: AI 提供商，为 None 时使用环境变量配置

    Returns:
        AIConfig: AI 配置对象
    """
    if provider is None:
        provider = os.getenv("AI_PROVIDER", "deepseek")

    if provider == "qwen":
        return AIConfig(
            provider=AIProvider.QWEN,
            api_key=os.getenv("DASHSCOPE_API_KEY", ""),
            model="qwen-plus",
        )
    else:  # deepseek
        return AIConfig(
            provider=AIProvider.DEEPSEEK,
            api_key=os.getenv("DEEPSEEK_API_KEY", ""),
            model="deepseek-chat",
        )


def _call_qwen(prompt: str, config: AIConfig) -> str:
    """调用通义千问 API"""
    import dashscope
    from dashscope import Generation

    dashscope.api_key = config.api_key

    response = Generation.call(
        model=config.model,
        prompt=prompt,
        result_format="message",
    )

    if response.status_code == 200:
        return response.output.choices[0].message.content
    else:
        raise RuntimeError(f"通义千问调用失败: {response.code} - {response.message}")


def _call_deepseek(prompt: str, config: AIConfig) -> str:
    """调用 DeepSeek API"""
    from openai import OpenAI

    client = OpenAI(
        api_key=config.api_key,
        base_url="https://api.deepseek.com",
        timeout=60.0,  # 60秒超时
    )

    response = client.chat.completions.create(
        model=config.model,
        messages=[
            {"role": "system", "content": "你是一位专业的土壤学专家，擅长分析土壤普查数据并撰写专业报告。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=2000,
    )

    return response.choices[0].message.content


def call_ai(prompt: str, provider: str | None = None) -> str:
    """调用 AI 接口

    Args:
        prompt: 提示词
        provider: AI 提供商（qwen/deepseek），为 None 时使用默认配置

    Returns:
        str: AI 生成的内容
    """
    config = get_ai_config(provider)

    if config.provider == AIProvider.QWEN:
        return _call_qwen(prompt, config)
    else:
        return _call_deepseek(prompt, config)


def generate_analysis(
    attr_name: str,
    unit: str,
    sample_total: int,
    sample_mean: float,
    sample_median: float,
    sample_min: float,
    sample_max: float,
    grade_distribution: dict[str, float],
    region_name: str = "本地区",
    provider: str | None = None,
) -> str:
    """生成属性分析文字

    Args:
        attr_name: 属性名称
        unit: 单位
        sample_total: 样点总数
        sample_mean: 平均值
        sample_median: 中位值
        sample_min: 最小值
        sample_max: 最大值
        grade_distribution: 等级分布 {等级: 占比%}
        region_name: 地区名称
        provider: AI 提供商

    Returns:
        str: 分析文字
    """
    # 构建等级分布描述
    grade_desc = "、".join([f"{k}占{v:.1f}%" for k, v in grade_distribution.items() if v > 0])

    prompt = f"""请根据以下土壤{attr_name}检测数据，撰写一段专业的分析描述（150-250字）：

地区：{region_name}
属性：{attr_name}
单位：{unit}
样点数：{sample_total}
平均值：{sample_mean:.2f} {unit}
中位值：{sample_median:.2f} {unit}
范围：{sample_min:.2f} ~ {sample_max:.2f} {unit}
等级分布：{grade_desc}

要求：
1. 使用专业的土壤学术语
2. 描述整体水平和分布特征
3. 与全国或区域平均水平对比（如有必要）
4. 语言简洁、客观
5. 不需要标题，直接输出正文"""

    return call_ai(prompt, provider)


def generate_conclusion(
    attr_name: str,
    sample_mean: float,
    unit: str,
    grade_distribution: dict[str, float],
    region_name: str = "本地区",
    provider: str | None = None,
) -> str:
    """生成分析结论

    Args:
        attr_name: 属性名称
        sample_mean: 平均值
        unit: 单位
        grade_distribution: 等级分布
        region_name: 地区名称
        provider: AI 提供商

    Returns:
        str: 结论文字
    """
    # 找出主要等级
    main_grade = max(grade_distribution.items(), key=lambda x: x[1])[0] if grade_distribution else "中等"

    prompt = f"""请根据以下{attr_name}分析结果，撰写简短的结论（50-80字）：

地区：{region_name}
{attr_name}平均值：{sample_mean:.2f} {unit}
主要等级：{main_grade}

要求：
1. 一句话总结整体水平
2. 指出需要关注的问题（如有）
3. 不需要标题"""

    return call_ai(prompt, provider)


def generate_suggestion(
    attr_name: str,
    sample_mean: float,
    unit: str,
    grade_distribution: dict[str, float],
    region_name: str = "本地区",
    provider: str | None = None,
) -> str:
    """生成改良建议

    Args:
        attr_name: 属性名称
        sample_mean: 平均值
        unit: 单位
        grade_distribution: 等级分布
        region_name: 地区名称
        provider: AI 提供商

    Returns:
        str: 建议文字
    """
    # 计算低等级占比
    low_grade_pct = sum(v for k, v in grade_distribution.items() if "4" in k or "5" in k or "6" in k)

    prompt = f"""请根据以下{attr_name}分析结果，提出土壤改良建议（100-150字）：

地区：{region_name}
{attr_name}平均值：{sample_mean:.2f} {unit}
较低等级（4级及以下）占比：{low_grade_pct:.1f}%

要求：
1. 针对性的改良措施
2. 具体可操作的建议
3. 分点列出（2-3点）
4. 不需要标题"""

    return call_ai(prompt, provider)


def generate_comprehensive_summary(
    region_name: str,
    survey_year: int,
    attr_summaries: list[dict],
    provider: str | None = None,
) -> str:
    """生成综合报告摘要

    Args:
        region_name: 地区名称
        survey_year: 调查年份
        attr_summaries: 各属性摘要列表，每项包含 {name, mean, unit, main_grade}
        provider: AI 提供商

    Returns:
        str: 综合摘要文字
    """
    attr_desc = "\n".join([
        f"- {a['name']}：均值 {a['mean']:.2f} {a['unit']}，主要为{a['main_grade']}"
        for a in attr_summaries
    ])

    prompt = f"""请根据以下土壤普查结果，撰写综合分析摘要（200-300字）：

地区：{region_name}
调查年份：{survey_year}年
分析属性数量：{len(attr_summaries)}个

各属性概况：
{attr_desc}

要求：
1. 总体评价该地区土壤质量状况
2. 指出优势和不足
3. 提出综合性建议
4. 语言专业、简洁
5. 不需要标题，直接输出正文"""

    return call_ai(prompt, provider)


def generate_traceability_analysis(
    attr_name: str,
    unit: str,
    sample_mean: float,
    area_mean: float,
    grade_distribution: dict[str, float],
    region_name: str = "本地区",
    provider: str | None = None,
) -> str:
    """生成溯源分析

    结合样点和制图数据，分析属性的可能成因和影响因素

    Args:
        attr_name: 属性名称
        unit: 单位
        sample_mean: 样点平均值
        area_mean: 制图平均值
        grade_distribution: 等级分布
        region_name: 地区名称
        provider: AI 提供商

    Returns:
        str: 溯源分析文字
    """
    grade_desc = "、".join([f"{k}占{v:.1f}%" for k, v in grade_distribution.items() if v > 0])

    prompt = f"""请根据以下土壤{attr_name}数据，进行溯源分析（150-200字）：

地区：{region_name}
属性：{attr_name}
单位：{unit}
样点平均值：{sample_mean:.2f} {unit}
制图平均值：{area_mean:.2f} {unit}
等级分布：{grade_desc}

要求：
1. 分析该属性数值水平的可能成因
2. 考虑自然因素（地质、气候、地形等）
3. 考虑人为因素（耕作方式、施肥习惯等）
4. 结合样点和制图数据差异说明问题
5. 语言专业、客观
6. 不需要标题，直接输出正文"""

    return call_ai(prompt, provider)


def generate_land_use_analysis(
    attr_name: str,
    unit: str,
    land_use_data: dict[str, dict],
    region_name: str = "本地区",
    provider: str | None = None,
) -> str:
    """生成土地利用类型分析

    Args:
        attr_name: 属性名称
        unit: 单位
        land_use_data: 土地利用数据 {类型: {area: 面积, mean: 均值}}
        region_name: 地区名称
        provider: AI 提供商

    Returns:
        str: 分析文字
    """
    if not land_use_data:
        return "暂无土地利用类型数据可供分析。"

    land_desc = "\n".join([
        f"- {k}：面积{v['area']:.1f}亩，均值{v['mean']:.2f}{unit}"
        for k, v in land_use_data.items()
    ])

    prompt = f"""请根据以下不同土地利用类型的土壤{attr_name}数据，进行分析（100-150字）：

地区：{region_name}
属性：{attr_name}
单位：{unit}

各土地利用类型数据：
{land_desc}

要求：
1. 比较不同土地利用类型之间的差异
2. 分析差异的可能原因
3. 提出针对性建议
4. 语言专业、简洁
5. 不需要标题，直接输出正文"""

    return call_ai(prompt, provider)


def generate_soil_type_analysis(
    attr_name: str,
    unit: str,
    soil_data: dict[str, dict],
    region_name: str = "本地区",
    provider: str | None = None,
) -> str:
    """生成土壤类型分析

    Args:
        attr_name: 属性名称
        unit: 单位
        soil_data: 土壤类型数据 {亚类: {area: 面积, mean: 均值}}
        region_name: 地区名称
        provider: AI 提供商

    Returns:
        str: 分析文字
    """
    if not soil_data:
        return "暂无土壤类型数据可供分析。"

    soil_desc = "\n".join([
        f"- {k}：面积{v['area']:.1f}亩，均值{v['mean']:.2f}{unit}"
        for k, v in soil_data.items()
    ])

    prompt = f"""请根据以下不同土壤类型的{attr_name}数据，进行分析（100-150字）：

地区：{region_name}
属性：{attr_name}
单位：{unit}

各土壤类型（按亚类）数据：
{soil_desc}

要求：
1. 比较不同土壤类型之间的差异
2. 分析土壤类型与{attr_name}的关系
3. 指出需要关注的土壤类型
4. 语言专业、简洁
5. 不需要标题，直接输出正文"""

    return call_ai(prompt, provider)


def generate_town_analysis(
    attr_name: str,
    unit: str,
    town_data: dict[str, dict],
    region_name: str = "本地区",
    provider: str | None = None,
) -> str:
    """生成乡镇分析

    Args:
        attr_name: 属性名称
        unit: 单位
        town_data: 乡镇数据 {乡镇: {samples: 样点数, area: 面积, mean: 均值}}
        region_name: 地区名称
        provider: AI 提供商

    Returns:
        str: 分析文字
    """
    if not town_data:
        return "暂无乡镇数据可供分析。"

    # 找出均值最高和最低的乡镇
    valid_towns = {k: v for k, v in town_data.items() if v.get("mean") is not None}
    if not valid_towns:
        return "乡镇数据不完整，无法进行分析。"

    max_town = max(valid_towns.items(), key=lambda x: x[1]["mean"])
    min_town = min(valid_towns.items(), key=lambda x: x[1]["mean"])

    town_desc = "\n".join([
        f"- {k}：样点{v['samples']}个，面积{v['area']:.1f}亩，均值{v['mean']:.2f}{unit}"
        for k, v in list(town_data.items())[:10]  # 只取前10个
    ])

    prompt = f"""请根据以下各乡镇的土壤{attr_name}数据，进行分析（100-150字）：

地区：{region_name}
属性：{attr_name}
单位：{unit}
最高均值乡镇：{max_town[0]}（{max_town[1]['mean']:.2f}{unit}）
最低均值乡镇：{min_town[0]}（{min_town[1]['mean']:.2f}{unit}）

部分乡镇数据：
{town_desc}

要求：
1. 描述乡镇间的空间分布特征
2. 指出高值和低值区域
3. 分析可能的原因（地理位置、种植结构等）
4. 语言专业、简洁
5. 不需要标题，直接输出正文"""

    return call_ai(prompt, provider)
