import hashlib
import secrets
import string
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from pathlib import Path


def generate_random_string(length: int = 32) -> str:
    """生成随机字符串"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_filename(original_filename: str, prefix: str = "") -> str:
    """生成唯一文件名"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_str = generate_random_string(8)
    
    # 获取文件扩展名
    file_suffix = Path(original_filename).suffix
    
    if prefix:
        return f"{prefix}_{timestamp}_{random_str}{file_suffix}"
    else:
        return f"{timestamp}_{random_str}{file_suffix}"


def calculate_md5(content: bytes) -> str:
    """计算MD5哈希值"""
    return hashlib.md5(content).hexdigest()


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def is_allowed_file_type(filename: str, allowed_extensions: List[str]) -> bool:
    """检查文件类型是否允许"""
    file_ext = Path(filename).suffix.lower()
    return file_ext in [ext.lower() for ext in allowed_extensions]


def paginate_query(query, page: int, page_size: int):
    """分页查询"""
    offset = (page - 1) * page_size
    return query.offset(offset).limit(page_size)


def build_pagination_response(
    items: List[Any], 
    total: int, 
    page: int, 
    page_size: int
) -> Dict[str, Any]:
    """构建分页响应"""
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "data": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


def format_datetime(dt: Optional[datetime], format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[str]:
    """格式化日期时间"""
    if dt is None:
        return None
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """解析日期时间字符串"""
    return datetime.strptime(dt_str, format_str)


def get_chinese_grade_name(grade_level: int, study_level: str) -> str:
    """获取中文年级名称"""
    grade_mapping = {
        "primary": {
            1: "一年级", 2: "二年级", 3: "三年级",
            4: "四年级", 5: "五年级", 6: "六年级"
        },
        "junior": {
            7: "初一", 8: "初二", 9: "初三"
        },
        "senior": {
            10: "高一", 11: "高二", 12: "高三"
        }
    }
    
    return grade_mapping.get(study_level, {}).get(grade_level, f"{grade_level}年级")


def calculate_score_grade(score: float) -> str:
    """计算分数等级"""
    if score >= 90:
        return "优秀"
    elif score >= 80:
        return "良好"
    elif score >= 70:
        return "中等"
    elif score >= 60:
        return "及格"
    else:
        return "不及格"


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """安全除法，避免除零错误"""
    if denominator == 0:
        return default
    return numerator / denominator


def remove_sensitive_data(data: Dict[str, Any], sensitive_fields: List[str]) -> Dict[str, Any]:
    """移除敏感数据字段"""
    return {k: v for k, v in data.items() if k not in sensitive_fields}


def mask_sensitive_string(value: str, mask_char: str = "*", keep_prefix: int = 3, keep_suffix: int = 3) -> str:
    """遮蔽敏感字符串"""
    if len(value) <= keep_prefix + keep_suffix:
        return mask_char * len(value)
    
    prefix = value[:keep_prefix]
    suffix = value[-keep_suffix:] if keep_suffix > 0 else ""
    mask_length = len(value) - keep_prefix - keep_suffix
    
    return prefix + mask_char * mask_length + suffix
