"""内容审核 - 敏感词过滤"""
import re

# 基础敏感词库（生产环境应从数据库/配置加载）
SENSITIVE_WORDS = [
    "赌博", "博彩", "色情", "毒品", "枪支", "诈骗",
    "传销", "非法集资", "洗钱", "恐怖", "暴力",
    "代开发票", "办假证", "代孕", "枪手",
]

_compiled = [re.compile(re.escape(w), re.IGNORECASE) for w in SENSITIVE_WORDS]


def check_sensitive(text: str) -> list[str]:
    """检查文本中的敏感词，返回匹配到的敏感词列表"""
    if not text:
        return []
    found = []
    for pattern in _compiled:
        matches = pattern.findall(text)
        if matches:
            found.extend(matches)
    return list(set(found))


def contains_sensitive(text: str) -> bool:
    """检查文本是否包含敏感词"""
    return len(check_sensitive(text)) > 0


def mask_sensitive(text: str) -> str:
    """将敏感词替换为 ***"""
    if not text:
        return text
    result = text
    for pattern in _compiled:
        result = pattern.sub("***", result)
    return result
