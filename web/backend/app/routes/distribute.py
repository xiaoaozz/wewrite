"""多平台分发：把一份源内容改写到多个平台（异步 agent 任务，SSE 复用 jobs 流）。"""
from __future__ import annotations

import asyncio
import subprocess

from fastapi import APIRouter, Depends, HTTPException

from ..agent_runner import run_distribute_job
from ..config import get_settings
from ..models import DistributeRequest, JobSummary
from ..store import STORE
from . import current_user

router = APIRouter(prefix="/api/distribute", tags=["distribute"])


def _fetch_url(url: str) -> str:
    settings = get_settings()
    try:
        r = subprocess.run(
            ["python3", "scripts/fetch_article.py", url],
            cwd=str(settings.skill_dir), capture_output=True, timeout=120,
            check=False, text=True,
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"抓取文章失败：{exc}") from exc
    raise HTTPException(status_code=502, detail="抓取文章失败或内容为空")


def _resolve_source(req: DistributeRequest, user_id: str) -> tuple[str, list[str]]:
    """返回 (源 markdown, 源图片本机路径列表)。"""
    if req.source_job_id:
        job = STORE.get_job(req.source_job_id)
        if not job or job.user_id != user_id:
            raise HTTPException(status_code=404, detail="源任务不存在")
        if not job.article_markdown:
            raise HTTPException(status_code=400, detail="源任务还没有成稿")
        return job.article_markdown, list(getattr(job, "image_paths", []))
    if req.source_text:
        return req.source_text, []
    if req.source_url:
        return _fetch_url(req.source_url), []
    raise HTTPException(status_code=400, detail="需提供 source_job_id / source_text / source_url 之一")


@router.post("", response_model=JobSummary)
async def distribute(req: DistributeRequest, user_id: str = Depends(current_user)) -> JobSummary:
    source_md, source_imgs = _resolve_source(req, user_id)
    job = STORE.create_job(
        user_id=user_id, prompt=f"分发到 {', '.join(req.platforms)}",
        kind="distribute", source_markdown=source_md,
        target_platforms=req.platforms, persona=req.persona, theme=req.theme,
        source_image_paths=source_imgs,
    )
    asyncio.create_task(run_distribute_job(job))
    return JobSummary(id=job.id, status=job.status, prompt=job.prompt,
                      created_at=job.created_at, completion=job.completion, kind=job.kind)
