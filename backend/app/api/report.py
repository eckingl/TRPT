"""报告生成 API"""

from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

from app.config import get_settings
from app.core.data import load_multiple_csv
from app.models import (
    ReportGenerateRequest,
    ReportGenerateResponse,
)
from app.topics.attribute_map import process_attribute_data, process_mapping_data
from app.topics.attribute_map.config import (
    SOIL_ATTR_CONFIG,
    detect_available_attributes,
)
from app.topics.attribute_map.excel_reader import (
    get_available_attributes_from_excel,
)
from app.topics.attribute_map.generate import (
    ReportConfig,
    generate_attribute_report,
    generate_multi_attribute_report,
    generate_multi_report_from_excel,
    generate_report_from_excel,
)
from app.topics.attribute_map.stats import AttributeStats, compute_attribute_stats

router = APIRouter(prefix="/report")
settings = get_settings()

# 处理结果缓存（简单内存缓存，生产环境应使用 Redis）
_process_cache: dict[str, dict] = {}

# 处理记录持久化文件
PROCESS_RECORDS_FILE = settings.OUTPUT_DIR / ".process_records.json"


def _load_process_records() -> list[dict]:
    """加载处理记录"""
    import json

    if PROCESS_RECORDS_FILE.exists():
        try:
            with open(PROCESS_RECORDS_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def _save_process_records(records: list[dict]) -> None:
    """保存处理记录"""
    import json

    # 只保留最近 50 条记录
    records = records[-50:]
    with open(PROCESS_RECORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def _add_process_record(
    process_id: str,
    sample_files: list[str],
    area_files: list[str],
    preview: list[dict],
    excel_filename: str,
    excel_path: str,
) -> None:
    """添加处理记录"""
    records = _load_process_records()
    records.append(
        {
            "process_id": process_id,
            "sample_files": [Path(f).name for f in sample_files],
            "area_files": [Path(f).name for f in area_files],
            # 保存完整路径，用于重新加载统计数据
            "sample_file_paths": sample_files,
            "area_file_paths": area_files,
            "preview": preview,
            "excel_filename": excel_filename,
            "excel_path": excel_path,  # 保存Excel完整路径，用于报告生成
            "created_at": datetime.now().isoformat(),
        }
    )
    _save_process_records(records)


class AttributeDataRequest(BaseModel):
    """属性图数据处理请求"""

    sample_files: list[str] = Field(..., description="样点统计文件路径列表")
    area_files: list[str] = Field(..., description="制图统计文件路径列表")


class MappingDataRequest(BaseModel):
    """属性图上图处理请求"""

    area_files: list[str] = Field(..., description="制图统计文件路径列表")


class WordReportRequest(BaseModel):
    """Word报告生成请求"""

    sample_files: list[str] = Field(..., description="样点统计文件路径列表")
    area_files: list[str] = Field(..., description="制图统计文件路径列表")
    attributes: list[str] | None = Field(
        default=None, description="要分析的属性列表，为空则自动检测"
    )
    region_name: str = Field(default="XX县", description="区域名称")
    survey_year: int = Field(default=2024, description="调查年份")
    theme: str = Field(default="professional", description="图表主题")
    include_pie_chart: bool = Field(default=True, description="是否包含饼图")
    include_bar_chart: bool = Field(default=True, description="是否包含柱状图")
    include_town_chart: bool = Field(default=True, description="是否包含乡镇对比图")
    include_stack_chart: bool = Field(default=True, description="是否包含堆叠图")


class AttributePreview(BaseModel):
    """属性预览信息"""

    key: str = Field(..., description="属性键名")
    name: str = Field(..., description="属性名称")
    unit: str = Field(..., description="单位")
    sample_count: int = Field(..., description="样点数量")
    sample_mean: float = Field(..., description="样点均值")
    sample_min: float = Field(..., description="最小值")
    sample_max: float = Field(..., description="最大值")
    grade_distribution: dict[str, float] = Field(..., description="等级分布百分比")


class ProcessResponse(BaseModel):
    """处理响应"""

    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")
    download_url: str | None = Field(default=None, description="下载链接")
    filename: str | None = Field(default=None, description="文件名")
    # 预览数据
    preview: list[AttributePreview] | None = Field(default=None, description="属性预览")
    process_id: str | None = Field(default=None, description="处理ID，用于生成报告")


@router.post("/attribute-data", response_model=ProcessResponse)
async def process_attribute_data_api(request: AttributeDataRequest) -> ProcessResponse:
    """处理属性图数据

    Args:
        request: 包含样点文件和制图文件路径的请求

    Returns:
        处理结果，包含预览数据和处理ID
    """
    import uuid

    # 验证文件是否存在
    for file_path in request.sample_files:
        if not Path(file_path).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"样点文件不存在: {file_path}",
            )

    for file_path in request.area_files:
        if not Path(file_path).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"制图文件不存在: {file_path}",
            )

    # 处理数据
    success, result = process_attribute_data(
        sample_paths=request.sample_files,
        area_paths=request.area_files,
    )

    if not success:
        return ProcessResponse(
            success=False,
            message=f"处理失败: {result}",
        )

    # 保存结果文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"属性图数据处理_{timestamp}.xlsx"
    output_path = settings.OUTPUT_DIR / output_filename

    with open(output_path, "wb") as f:
        f.write(result)

    # 生成预览数据
    preview_list = []
    stats_list = []

    try:
        # 加载数据计算统计
        df_sample = load_multiple_csv(request.sample_files)
        df_area = load_multiple_csv(request.area_files)

        # 检测可用属性
        available = detect_available_attributes(list(df_sample.columns))

        for orig_col, attr_key in available:
            config = SOIL_ATTR_CONFIG.get(attr_key)
            if not config:
                continue

            # 重命名列
            df_s = df_sample.copy()
            df_a = df_area.copy()
            if orig_col != attr_key:
                if orig_col in df_s.columns:
                    df_s = df_s.rename(columns={orig_col: attr_key})
                if orig_col in df_a.columns:
                    df_a = df_a.rename(columns={orig_col: attr_key})

            # 计算统计
            levels = config.get("levels", [])
            grade_order = [level[1] for level in levels]

            try:
                stats = compute_attribute_stats(df_s, df_a, attr_key, grade_order)
                stats_list.append(stats)

                # 计算等级分布百分比
                total_area = sum(stats.grade_area_sums.values())
                grade_pct = {}
                if total_area > 0:
                    grade_pct = {
                        k: round(v / total_area * 100, 1)
                        for k, v in stats.grade_area_sums.items()
                    }

                preview_list.append(
                    AttributePreview(
                        key=attr_key,
                        name=stats.attr_name,
                        unit=stats.unit,
                        sample_count=stats.sample_total,
                        sample_mean=round(stats.sample_mean, 2),
                        sample_min=round(stats.sample_min, 2),
                        sample_max=round(stats.sample_max, 2),
                        grade_distribution=grade_pct,
                    )
                )
            except Exception:
                continue

    except Exception as e:
        # 预览生成失败不影响主流程
        print(f"预览生成失败: {e}")

    # 生成处理ID并缓存结果
    process_id = str(uuid.uuid4())[:8]
    _process_cache[process_id] = {
        "sample_files": request.sample_files,
        "area_files": request.area_files,
        "stats_list": stats_list,
        "created_at": datetime.now(),
    }

    # 持久化保存处理记录
    if preview_list:
        _add_process_record(
            process_id=process_id,
            sample_files=request.sample_files,
            area_files=request.area_files,
            preview=[p.model_dump() for p in preview_list],
            excel_filename=output_filename,
            excel_path=str(output_path),
        )

    return ProcessResponse(
        success=True,
        message=f"处理完成，检测到 {len(preview_list)} 个属性",
        download_url=f"/api/report/download/{quote(output_filename)}",
        filename=output_filename,
        preview=preview_list if preview_list else None,
        process_id=process_id,
    )


@router.post("/mapping-data", response_model=ProcessResponse)
async def process_mapping_data_api(request: MappingDataRequest) -> ProcessResponse:
    """处理属性图上图数据

    Args:
        request: 包含制图文件路径的请求

    Returns:
        处理结果
    """
    # 验证文件是否存在
    for file_path in request.area_files:
        if not Path(file_path).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"制图文件不存在: {file_path}",
            )

    # 处理数据
    success, result = process_mapping_data(area_paths=request.area_files)

    if not success:
        return ProcessResponse(
            success=False,
            message=f"处理失败: {result}",
        )

    # 保存结果文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"属性图上图处理_{timestamp}.xlsx"
    output_path = settings.OUTPUT_DIR / output_filename

    with open(output_path, "wb") as f:
        f.write(result)

    return ProcessResponse(
        success=True,
        message="处理完成",
        download_url=f"/api/report/download/{quote(output_filename)}",
        filename=output_filename,
    )


@router.get("/download/{filename:path}")
async def download_report_file(filename: str) -> StreamingResponse:
    """下载报告文件

    Args:
        filename: 文件名（URL编码后的）

    Returns:
        文件流响应
    """
    # 对文件名进行解码（处理URL编码的中文字符）
    from urllib.parse import unquote

    decoded_filename = unquote(filename)

    file_path = settings.OUTPUT_DIR / decoded_filename

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"文件不存在: {decoded_filename}",
        )

    def iter_file():
        with open(file_path, "rb") as f:
            yield from f

    # 设置Content-Disposition头，支持中文文件名
    encoded_filename = quote(decoded_filename)

    # 根据文件扩展名设置 MIME 类型
    if decoded_filename.endswith(".docx"):
        media_type = (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    elif decoded_filename.endswith(".xlsx"):
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        media_type = "application/octet-stream"

    return StreamingResponse(
        iter_file(),
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        },
    )


@router.get("/list")
async def list_reports() -> list[dict]:
    """获取已生成的报告列表

    Returns:
        报告文件列表
    """
    reports = []
    # 支持 xlsx 和 docx 文件
    for pattern in ["*.xlsx", "*.docx"]:
        for file_path in settings.OUTPUT_DIR.glob(pattern):
            stat = file_path.stat()
            file_type = "word" if file_path.suffix == ".docx" else "excel"
            reports.append(
                {
                    "filename": file_path.name,
                    "size": stat.st_size,
                    "type": file_type,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "download_url": f"/api/report/download/{quote(file_path.name)}",
                }
            )

    # 按创建时间倒序排列
    reports.sort(key=lambda x: x["created_at"], reverse=True)
    return reports


@router.get("/process-records")
async def get_process_records() -> list[dict]:
    """获取处理记录列表

    Returns:
        处理记录列表，包含处理ID、文件名、属性预览等
    """
    records = _load_process_records()
    # 按时间倒序
    records.reverse()
    return records


@router.get("/process-records/{process_id}")
async def get_process_record(process_id: str) -> dict:
    """获取单条处理记录详情

    Args:
        process_id: 处理ID

    Returns:
        处理记录详情
    """
    records = _load_process_records()
    for record in records:
        if record.get("process_id") == process_id:
            return record

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"处理记录不存在: {process_id}",
    )


@router.post("/generate", response_model=ReportGenerateResponse)
async def generate_report(request: ReportGenerateRequest) -> ReportGenerateResponse:
    """生成报告（旧接口，保持兼容）

    Args:
        request: 报告生成请求

    Returns:
        报告生成响应

    Raises:
        HTTPException: 专题不存在或生成失败
    """
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="请使用 /api/report/word-report 接口生成 Word 报告",
    )


@router.post("/word-report", response_model=ProcessResponse)
async def generate_word_report(request: WordReportRequest) -> ProcessResponse:
    """生成 Word 分析报告

    基于样点和制图数据，生成包含图表的 Word 分析报告。

    Args:
        request: Word报告生成请求

    Returns:
        处理结果，包含下载链接
    """
    # 验证文件是否存在
    for file_path in request.sample_files:
        if not Path(file_path).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"样点文件不存在: {file_path}",
            )

    for file_path in request.area_files:
        if not Path(file_path).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"制图文件不存在: {file_path}",
            )

    try:
        # 加载数据
        df_sample = load_multiple_csv(request.sample_files)
        df_area = load_multiple_csv(request.area_files)

        # 检测或使用指定的属性
        if request.attributes:
            attr_keys = [a for a in request.attributes if a in SOIL_ATTR_CONFIG]
        else:
            attr_keys = detect_available_attributes(df_sample)

        if not attr_keys:
            return ProcessResponse(
                success=False,
                message="未找到可分析的土壤属性",
            )

        # 计算各属性的统计数据
        stats_list: list[AttributeStats] = []
        for attr_key in attr_keys:
            config = SOIL_ATTR_CONFIG[attr_key]
            levels = config.get("levels", [])
            grade_order = [level[1] for level in levels]

            stats = compute_attribute_stats(df_sample, df_area, attr_key, grade_order)
            stats_list.append(stats)

        # 配置报告
        report_config = ReportConfig(
            region_name=request.region_name,
            survey_year=request.survey_year,
            theme=request.theme,
            include_pie_chart=request.include_pie_chart,
            include_bar_chart=request.include_bar_chart,
            include_town_chart=request.include_town_chart,
            include_stack_chart=request.include_stack_chart,
        )

        # 生成报告
        if len(stats_list) == 1:
            report_data = generate_attribute_report(stats_list[0], report_config)
            report_type = stats_list[0].attr_name
        else:
            report_data = generate_multi_attribute_report(stats_list, report_config)
            report_type = "综合"

        # 保存文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = (
            f"{request.region_name}_{report_type}分析报告_{timestamp}.docx"
        )
        output_path = settings.OUTPUT_DIR / output_filename

        output_path.write_bytes(report_data)

        return ProcessResponse(
            success=True,
            message=f"报告生成成功，包含 {len(stats_list)} 个属性分析",
            download_url=f"/api/report/download/{quote(output_filename)}",
            filename=output_filename,
        )

    except Exception as e:
        return ProcessResponse(
            success=False,
            message=f"报告生成失败: {e!s}",
        )


class GenerateFromProcessRequest(BaseModel):
    """基于处理结果生成报告请求"""

    process_id: str = Field(..., description="处理ID")
    attributes: list[str] | None = Field(
        default=None, description="要包含的属性列表，为空则包含全部"
    )
    region_name: str = Field(default="XX县", description="区域名称")
    survey_year: int = Field(default=2024, description="调查年份")
    theme: str = Field(default="professional", description="图表主题")
    report_mode: str = Field(
        default="multi",
        description="报告模式: single(单属性), multi(综合), both(两者都生成)",
    )
    use_ai: bool = Field(default=False, description="是否使用AI生成分析")
    ai_provider: str | None = Field(default=None, description="AI提供商: qwen/deepseek")


def _reload_stats_from_record(process_id: str) -> list[AttributeStats]:
    """从持久化记录重新加载统计数据"""
    # 首先检查内存缓存
    if process_id in _process_cache:
        return _process_cache[process_id].get("stats_list", [])

    # 从持久化记录获取文件信息
    records = _load_process_records()
    record = None
    for r in records:
        if r.get("process_id") == process_id:
            record = r
            break

    if not record:
        return []

    # 获取保存的文件路径
    sample_file_paths = record.get("sample_file_paths", [])
    area_file_paths = record.get("area_file_paths", [])

    if not sample_file_paths or not area_file_paths:
        return []

    # 检查文件是否仍然存在
    for path in sample_file_paths + area_file_paths:
        if not Path(path).exists():
            return []

    try:
        # 重新加载数据并计算统计
        df_sample = load_multiple_csv(sample_file_paths)
        df_area = load_multiple_csv(area_file_paths)

        # 检测可用属性
        available = detect_available_attributes(list(df_sample.columns))

        stats_list = []
        for orig_col, attr_key in available:
            config = SOIL_ATTR_CONFIG.get(attr_key)
            if not config:
                continue

            # 重命名列
            df_s = df_sample.copy()
            df_a = df_area.copy()
            if orig_col != attr_key:
                if orig_col in df_s.columns:
                    df_s = df_s.rename(columns={orig_col: attr_key})
                if orig_col in df_a.columns:
                    df_a = df_a.rename(columns={orig_col: attr_key})

            # 计算统计
            levels = config.get("levels", [])
            grade_order = [level[1] for level in levels]

            try:
                stats = compute_attribute_stats(df_s, df_a, attr_key, grade_order)
                stats_list.append(stats)
            except Exception:
                continue

        # 更新内存缓存
        if stats_list:
            _process_cache[process_id] = {
                "sample_files": sample_file_paths,
                "area_files": area_file_paths,
                "stats_list": stats_list,
                "created_at": datetime.now(),
            }

        return stats_list

    except Exception as e:
        print(f"重新加载统计数据失败: {e}")
        return []


@router.post("/generate-from-process", response_model=ProcessResponse)
async def generate_report_from_process(
    request: GenerateFromProcessRequest,
) -> ProcessResponse:
    """基于数据处理结果生成 Word 报告

    使用之前数据处理返回的 process_id，从已生成的 Excel 结果文件读取数据生成报告。

    Args:
        request: 生成报告请求，包含处理ID和报告配置

    Returns:
        处理结果，包含下载链接
    """
    # 从持久化记录获取 Excel 文件路径
    records = _load_process_records()
    record = None
    for r in records:
        if r.get("process_id") == request.process_id:
            record = r
            break

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"处理结果不存在: {request.process_id}",
        )

    # 获取 Excel 文件路径
    excel_path = record.get("excel_path")
    if not excel_path:
        # 兼容旧记录：尝试从 excel_filename 构建路径
        excel_filename = record.get("excel_filename")
        if excel_filename:
            excel_path = str(settings.OUTPUT_DIR / excel_filename)

    if not excel_path or not Path(excel_path).exists():
        return ProcessResponse(
            success=False,
            message="Excel 结果文件不存在，请重新处理数据后再生成报告",
        )

    # 获取可用的属性列表
    available_attrs = get_available_attributes_from_excel(excel_path)
    if not available_attrs:
        return ProcessResponse(
            success=False,
            message="无法从 Excel 文件读取属性信息",
        )

    # 过滤属性
    if request.attributes:
        # 将属性键名转换为属性名称
        attr_names = []
        for attr_key in request.attributes:
            config = SOIL_ATTR_CONFIG.get(attr_key)
            if config:
                attr_name = config["name"]
                if attr_name in available_attrs:
                    attr_names.append(attr_name)
        if not attr_names:
            return ProcessResponse(
                success=False,
                message="选择的属性无可用数据",
            )
    else:
        attr_names = available_attrs

    try:
        # 配置报告
        report_config = ReportConfig(
            region_name=request.region_name,
            survey_year=request.survey_year,
            theme=request.theme,
            use_ai=request.use_ai,
            ai_provider=request.ai_provider,
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        generated_files = []

        if request.report_mode == "single":
            # 生成单属性报告
            for attr_name in attr_names:
                output_filename = (
                    f"{request.region_name}_{attr_name}_分析报告_{timestamp}.docx"
                )
                output_path = settings.OUTPUT_DIR / output_filename
                generate_report_from_excel(
                    Path(excel_path),
                    attr_name,
                    report_config,
                    output_path,
                )
                generated_files.append(output_filename)

            if generated_files:
                return ProcessResponse(
                    success=True,
                    message=f"成功生成 {len(generated_files)} 份单属性报告",
                    download_url=f"/api/report/download/{quote(generated_files[0])}",
                    filename=generated_files[0],
                )

        elif request.report_mode == "both":
            # 生成单属性报告
            for attr_name in attr_names:
                output_filename = (
                    f"{request.region_name}_{attr_name}_分析报告_{timestamp}.docx"
                )
                output_path = settings.OUTPUT_DIR / output_filename
                generate_report_from_excel(
                    Path(excel_path),
                    attr_name,
                    report_config,
                    output_path,
                )
                generated_files.append(output_filename)

            # 生成综合报告
            output_filename = f"{request.region_name}_综合分析报告_{timestamp}.docx"
            output_path = settings.OUTPUT_DIR / output_filename
            generate_multi_report_from_excel(
                Path(excel_path),
                attr_names,
                report_config,
                output_path,
            )
            generated_files.append(output_filename)

            return ProcessResponse(
                success=True,
                message=f"成功生成 {len(generated_files)} 份报告（含综合报告）",
                download_url=f"/api/report/download/{quote(output_filename)}",
                filename=output_filename,
            )

        else:  # multi (默认)
            # 生成综合报告
            if len(attr_names) == 1:
                output_filename = (
                    f"{request.region_name}_{attr_names[0]}_分析报告_{timestamp}.docx"
                )
                output_path = settings.OUTPUT_DIR / output_filename
                generate_report_from_excel(
                    Path(excel_path),
                    attr_names[0],
                    report_config,
                    output_path,
                )
            else:
                output_filename = f"{request.region_name}_综合分析报告_{timestamp}.docx"
                output_path = settings.OUTPUT_DIR / output_filename
                generate_multi_report_from_excel(
                    Path(excel_path),
                    attr_names,
                    report_config,
                    output_path,
                )

            return ProcessResponse(
                success=True,
                message=f"报告生成成功，包含 {len(attr_names)} 个属性分析",
                download_url=f"/api/report/download/{quote(output_filename)}",
                filename=output_filename,
            )

    except Exception as e:
        import traceback

        error_detail = traceback.format_exc()
        return ProcessResponse(
            success=False,
            message=f"报告生成失败: {e!s}\n{error_detail}",
        )

    return ProcessResponse(
        success=False,
        message="未能生成任何报告",
    )


@router.get("/preview/{report_id}")
async def preview_report(report_id: str) -> dict:
    """预览报告

    Args:
        report_id: 报告ID

    Returns:
        预览数据

    Raises:
        HTTPException: 报告不存在
    """
    # TODO: P4 阶段实现
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="报告预览功能将在 P4 阶段实现",
    )


@router.get("/download-by-id/{report_id}")
async def download_report(report_id: str) -> FileResponse:
    """下载报告

    Args:
        report_id: 报告ID

    Returns:
        报告文件

    Raises:
        HTTPException: 报告不存在
    """
    # TODO: P4 阶段实现
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="报告下载功能将在 P4 阶段实现",
    )
