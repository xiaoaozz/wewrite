"""主题 / 写作人格目录。"""
from __future__ import annotations

from fastapi import APIRouter

from ..config import get_settings
from ..models import CatalogItem

router = APIRouter(prefix="/api/catalog", tags=["catalog"])

# 与 README 一致的人格说明
_PERSONA_LABELS = {
    "midnight-friend": ("午夜朋友", "极度口语化、高自我怀疑、第一人称 —— 个人号/自媒体"),
    "warm-editor": ("温暖编辑", "温暖叙事、故事嵌套数据、柔和情绪弧 —— 生活/文化/情感"),
    "industry-observer": ("行业观察者", "中性分析、数据先行、稳中带刺 —— 行业媒体/分析"),
    "sharp-journalist": ("犀利记者", "犀利简洁、数据驱动、强观点 —— 新闻/评论"),
    "cold-analyst": ("冷静分析师", "冷静克制、逻辑链条、风险意识强 —— 财经/投研"),
    "humor-storyteller": ("幽默讲述者", "轻松幽默、画面感强、故事化表达"),
    "tech-coder": ("技术极客", "工程视角、术语精准、结构清晰 —— 技术/开发者"),
}

_THEME_GROUPS = {
    "professional-clean": "通用 · 默认",
    "minimal": "通用",
    "newspaper": "通用 · 报刊",
    "tech-modern": "科技",
    "bytedance": "科技",
    "github": "科技",
    "warm-editorial": "文艺",
    "sspai": "文艺",
    "ink": "文艺 · 水墨",
    "elegant-rose": "文艺",
    "bold-navy": "商务",
    "minimal-gold": "商务",
    "bold-green": "商务",
    "bauhaus": "风格",
    "focus-red": "风格",
    "midnight": "风格 · 暗黑",
}


@router.get("/personas", response_model=list[CatalogItem])
def personas() -> list[CatalogItem]:
    settings = get_settings()
    persona_dir = settings.skill_dir / "personas"
    items: list[CatalogItem] = []
    seen: set[str] = set()
    if persona_dir.exists():
        for p in sorted(persona_dir.glob("*.yaml")):
            pid = p.stem
            seen.add(pid)
            label, desc = _PERSONA_LABELS.get(pid, (pid, ""))
            items.append(CatalogItem(id=pid, label=label, description=desc))
    # 兜底：即便没有 personas 目录也给出已知人格
    for pid, (label, desc) in _PERSONA_LABELS.items():
        if pid not in seen:
            items.append(CatalogItem(id=pid, label=label, description=desc))
    return items


@router.get("/themes", response_model=list[CatalogItem])
def themes() -> list[CatalogItem]:
    settings = get_settings()
    theme_dir = settings.skill_dir / "toolkit" / "themes"
    items: list[CatalogItem] = []
    if theme_dir.exists():
        for p in sorted(theme_dir.glob("*.yaml")):
            tid = p.stem
            items.append(CatalogItem(id=tid, label=tid, description=_THEME_GROUPS.get(tid, "")))
    return items


@router.get("/platforms", response_model=list[CatalogItem])
def platforms() -> list[CatalogItem]:
    from ..platforms import all_profiles
    return [CatalogItem(id=p.id, label=p.label, description=p.output_kind)
            for p in all_profiles().values()]
