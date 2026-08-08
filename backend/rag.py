# 检索（文档 6.4）：query 向量化 → 余弦相似度暴力检索 → 按 category 过滤 → top_k。
# 语料就几百块，numpy 暴力算毫秒级，不装向量数据库。
import logging

import numpy as np

from . import config, db, llm

logger = logging.getLogger(__name__)

_vectors = None          # 归一化后的语料向量矩阵，行号 = corpus_chunks.id - 1
_chunks = None           # [(id, doc_name, category, chunk_text)]
_loaded_mtime = None     # 已加载的 corpus.npz 修改时间，变了就重载


def _load() -> bool:
    """懒加载语料与向量；corpus.npz 变化（重跑 build_corpus.py）时自动重载，不用重启服务。"""
    global _vectors, _chunks, _loaded_mtime
    npz_path = config.DATA_DIR / "corpus.npz"
    if not npz_path.exists():
        logger.warning("rag 语料未构建（缺 %s），检索不可用", npz_path)
        return False
    mtime = npz_path.stat().st_mtime
    if _vectors is not None and mtime == _loaded_mtime:
        return True
    if _vectors is not None:
        logger.info("rag 检测到 corpus.npz 更新，重新加载语料")
    vecs = np.load(npz_path)["vectors"]
    _vectors = vecs / np.linalg.norm(vecs, axis=1, keepdims=True)
    conn = db.get_conn()
    try:
        _chunks = conn.execute(
            "SELECT id, doc_name, category, chunk_text FROM corpus_chunks ORDER BY id"
        ).fetchall()
    finally:
        conn.close()
    if len(_chunks) != len(_vectors):
        logger.error(
            "rag 语料不一致：表 %d 行 vs 向量 %d 行，请重跑 build_corpus.py",
            len(_chunks), len(_vectors),
        )
        return False
    _loaded_mtime = mtime
    return True


def search(query: str, category: str = "any", top_k: int = 3) -> list[dict]:
    """返回 top_k 的 [{doc_name, category, chunk_text, score}]。语料缺失/出错返回空列表。"""
    if not _load():
        return []
    try:
        q = np.array(llm.embed([query])[0], dtype=np.float32)
    except Exception:
        logger.error("rag 检索时 embed 失败，返回空结果")
        return []
    q = q / np.linalg.norm(q)
    scores = _vectors @ q                      # 余弦相似度（已归一化）
    order = np.argsort(-scores)
    results = []
    for idx in order:
        row = _chunks[idx]
        if category != "any" and row["category"] != category:
            continue
        results.append({
            "doc_name": row["doc_name"],
            "category": row["category"],
            "chunk_text": row["chunk_text"],
            "score": float(scores[idx]),
        })
        if len(results) >= top_k:
            break
    logger.info(
        "rag search query=%r category=%s -> %s",
        query[:30], category, [r["doc_name"] for r in results],
    )
    return results
