# 一次性脚本（文档 6.3）：语料切块 + 向量化。
# 运行：/opt/miniconda3/envs/Eazo/bin/python scripts/build_corpus.py
# 幂等：重跑先清空 corpus_chunks 表和 corpus.npz 再建。
import re
import sys
from pathlib import Path

import numpy as np

# 让脚本能 import backend 包
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend import config, db, llm  # noqa: E402
from backend.logging_setup import setup_logging  # noqa: E402

CHUNK_MIN, CHUNK_MAX = 300, 500   # 每块 300–500 字
EMBED_BATCH = 10                  # 百炼 embedding 单次批量上限


def parse_header(text: str) -> dict:
    """读文件头注释：<!-- doc_name: xxx, category: xxx, ... -->"""
    m = re.search(r"<!--(.*?)-->", text, re.S)
    meta = {}
    if m:
        for part in m.group(1).split(","):
            if ":" in part:
                k, v = part.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta


def split_chunks(text: str, doc_name: str) -> list[str]:
    """按标题/空行切块，攒到 300–500 字一块，块首拼上文档名（提高检索质量）。"""
    body = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    # 按标题行或空行切成段
    parts = [p.strip() for p in re.split(r"\n#{1,3} |\n\n", body) if p.strip()]
    chunks, current = [], ""
    for p in parts:
        if len(current) + len(p) <= CHUNK_MAX:
            current = f"{current}\n{p}".strip()
        else:
            if current:
                chunks.append(current)
            current = p
        # 单段过长直接成块
        while len(current) > CHUNK_MAX:
            chunks.append(current[:CHUNK_MAX])
            current = current[CHUNK_MAX:]
    if current:
        chunks.append(current)
    # 过短的尾块并入前一块
    merged = []
    for c in chunks:
        if merged and len(c) < CHUNK_MIN / 3:
            merged[-1] += "\n" + c
        else:
            merged.append(c)
    return [f"《{doc_name}》\n{c}" for c in merged]


def main() -> None:
    setup_logging()
    db.init_db()

    all_chunks = []  # (doc_name, category, chunk_text)
    for md in sorted((config.DATA_DIR / "corpus").glob("*.md")):
        text = md.read_text(encoding="utf-8")
        meta = parse_header(text)
        doc_name = meta.get("doc_name", md.stem)
        category = meta.get("category", "any")
        chunks = split_chunks(text, doc_name)
        print(f"{md.name}: doc_name={doc_name} category={category} 切成 {len(chunks)} 块")
        all_chunks += [(doc_name, category, c) for c in chunks]

    print(f"共 {len(all_chunks)} 块，开始向量化…")
    vectors = []
    for i in range(0, len(all_chunks), EMBED_BATCH):
        batch = [c[2] for c in all_chunks[i:i + EMBED_BATCH]]
        vectors += llm.embed(batch)
        print(f"  向量化 {min(i + EMBED_BATCH, len(all_chunks))}/{len(all_chunks)}")

    # 写库（先清空，幂等）；向量按 id 顺序存 npz，行号 = id - 1
    conn = db.get_conn()
    try:
        conn.execute("DELETE FROM corpus_chunks")
        conn.execute("DELETE FROM sqlite_sequence WHERE name='corpus_chunks'")
        for doc_name, category, chunk in all_chunks:
            conn.execute(
                "INSERT INTO corpus_chunks (doc_name, category, chunk_text) VALUES (?, ?, ?)",
                (doc_name, category, chunk),
            )
        conn.commit()
    finally:
        conn.close()

    np.savez(config.DATA_DIR / "corpus.npz", vectors=np.array(vectors, dtype=np.float32))
    print(f"完成：corpus_chunks 表 {len(all_chunks)} 行，向量存 {config.DATA_DIR / 'corpus.npz'}")


if __name__ == "__main__":
    main()
