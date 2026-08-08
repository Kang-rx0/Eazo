# 一次性脚本（文档 6.2）：抓取 6.1 清单里的参考手册页面/PDF，清洗成 markdown 落到 data/corpus/。
# 运行：/opt/miniconda3/envs/Eazo/bin/python scripts/crawl_corpus.py
# 抓取失败（403/超时）的来源：打印警告 + 生成占位文件，由人工复制正文补齐，不阻塞流程。
import io
import re
import sys
import time
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "corpus_raw"
CORPUS_DIR = BASE_DIR / "data" / "corpus"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# 来源清单（对应文档 6.1 的表）。一个输出文件可以合并多个页面。
SOURCES = [
    {
        "file": "膳食指南2022.md",
        "doc_name": "中国居民膳食指南(2022)",
        "category": "diet",
        "pages": [
            {"url": "https://wjw.fujian.gov.cn/ztzl/jkjy/jkzgxd/202206/t20220615_5930367.htm",
             "type": "html"},
        ],
    },
    {
        "file": "身体活动指南2021.md",
        "doc_name": "中国人群身体活动指南(2021)",
        "category": "exercise",
        "pages": [
            {"url": "https://www.zgggws.com/cn/article/pdf/preview/10.11847/zgggws1137503.pdf",
             "type": "pdf"},
        ],
    },
    {
        "file": "WHO身体活动指南2020.md",
        "doc_name": "WHO 2020 身体活动指南",
        "category": "exercise",
        "pages": [
            {"url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7719906/", "type": "html"},
        ],
    },
    {
        "file": "全民健身指南.md",
        "doc_name": "全民健身指南",
        "category": "exercise",
        "pages": [
            {"url": "https://www.sport.gov.cn/n315/n331/n405/c819327/content.html", "type": "html"},
        ],
    },
    {
        "file": "办公族拉伸.md",
        "doc_name": "办公族拉伸指导",
        "category": "stretch",
        "pages": [
            {"url": "https://www.mayoclinic.org/healthy-lifestyle/adult-health/in-depth/office-stretches/art-20046041",
             "type": "html"},
            {"url": "https://www.ccohs.ca/oshanswers/ergonomics/office/stretching.html", "type": "html"},
        ],
    },
    {
        "file": "睡眠卫生.md",
        "doc_name": "睡眠卫生",
        "category": "sleep",
        "pages": [
            {"url": "https://www.cdc.gov/sleep/about/index.html", "type": "html"},
            {"url": "https://www.cdc.gov/niosh/bulletin/2020/sleep.html", "type": "html"},
        ],
    },
    # ---- V2 S5：慢病食养指南（文档 4.3.1）。主源卫健委官方 PDF，403/失效时用疾控中心转载页 ----
    # 收录疾病特点、食养原则和建议部分即可，各地食谱套餐示例可略（truncate_markers 截断）
    {
        "file": "高血压食养指南2023.md",
        "doc_name": "成人高血压食养指南(2023)",
        "category": "diet",
        "pages": [
            {"url": "https://www.nhc.gov.cn/sps/c100088/202301/f01895a06c5349ef999f25da833c166d/files/1732844468193_68545.pdf",
             "type": "pdf"},
        ],
        "backup_pages": [
            {"url": "https://www.chinacdc.cn/jkyj/yyyjk2/jswj13949/202504/t20250407_305763.html",
             "type": "html"},
        ],
        "start_markers": ["一、前言"],
        "truncate_markers": ["附录 3", "附录3", "不同地区食谱示例"],
    },
    {
        "file": "糖尿病食养指南2023.md",
        "doc_name": "成人糖尿病食养指南(2023)",
        "category": "diet",
        "pages": [
            {"url": "https://www.nhc.gov.cn/cms-search/downFiles/4fcbecd2c18e46baaf291bf46c2b79cd.pdf",
             "type": "pdf"},
        ],
        "backup_pages": [
            {"url": "https://www.chinacdc.cn/jkyj/yyyjk2/jswj13949/202504/t20250407_305766.html",
             "type": "html"},
        ],
        "start_markers": ["一、前言"],
        "truncate_markers": ["附录 3", "附录3", "不同地区食谱示例"],
    },
]

# 领域关键词表（清洗规则 3）：长段落里一个都不含 → 视为无关内容丢弃
DOMAIN_KEYWORDS = [
    "吃", "食", "餐", "膳", "营养", "动", "运动", "锻炼", "睡", "眠", "拉伸", "活动", "训练",
    "步行", "久坐", "健身", "蛋白", "蔬菜", "水果",
    "eat", "food", "diet", "meal", "exercise", "activity", "physical", "sleep",
    "stretch", "sit", "walk", "train", "muscle", "health",
]


def fetch(url: str, timeout: int = 30) -> requests.Response:
    """带 UA 抓取，失败重试 1 次。"""
    last_err = None
    for attempt in range(2):
        try:
            resp = requests.get(url, headers={"User-Agent": UA}, timeout=timeout)
            resp.raise_for_status()
            return resp
        except Exception as e:  # noqa: BLE001 一次性脚本，宽松捕获
            last_err = e
            print(f"  [警告] 第{attempt + 1}次抓取失败: {e}")
            time.sleep(2)
    raise last_err


def clean_html(html: str) -> str:
    """清洗规则 1：只取正文，剔除脚本/导航/页眉页脚等。"""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form", "button"]):
        tag.decompose()
    # 优先找正文容器
    main = (soup.find("article") or soup.find("main")
            or soup.find(class_=re.compile(r"(content|article|TRS_Editor|detail)", re.I))
            or soup.body or soup)
    text = main.get_text("\n")
    return text


def clean_pdf(content: bytes) -> str:
    """PDF 逐页提取文字，删掉跨页重复的页眉页脚行。"""
    import pdfplumber
    pages_text = []
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            pages_text.append(page.extract_text() or "")
    # 统计每行出现在多少页：出现 >=3 页的行视为页眉/页脚，删
    line_pages = {}
    for t in pages_text:
        for line in set(t.split("\n")):
            line = line.strip()
            if line:
                line_pages[line] = line_pages.get(line, 0) + 1
    repeated = {ln for ln, n in line_pages.items() if n >= 3}
    kept = []
    for t in pages_text:
        for line in t.split("\n"):
            if line.strip() not in repeated:
                kept.append(line)
    return "\n".join(kept)


def clean_text(text: str) -> str:
    """清洗规则 2-3：去页码/引用编号/碎句/无关长段。"""
    text = re.sub(r"\[\d+([-,]\d+)*\]", "", text)          # 参考文献编号 [12] [1-3]
    text = re.sub(r"^\s*[-—]?\s*\d+\s*[-—]?\s*$", "", text, flags=re.M)  # 独立页码行
    paragraphs, current = [], []
    for line in text.split("\n"):
        line = line.strip()
        if line:
            current.append(line)
        elif current:
            paragraphs.append(" ".join(current))
            current = []
    if current:
        paragraphs.append(" ".join(current))

    kept = []
    for p in paragraphs:
        if len(p) < 20:                       # 碎句
            continue
        if len(p) > 200 and not any(k in p.lower() for k in DOMAIN_KEYWORDS):
            continue                          # 长段但不含任何领域关键词 → 无关内容
        kept.append(p)
    return "\n\n".join(kept)


def crawl_page(page: dict) -> str:
    """抓一个页面并清洗，返回正文（过短抛异常）。原始文件存 corpus_raw/。"""
    url = page["url"]
    resp = fetch(url)
    ext = "pdf" if page["type"] == "pdf" else "html"
    raw_name = re.sub(r"\W+", "_", url)[-80:] + "." + ext
    (RAW_DIR / raw_name).write_bytes(resp.content)
    if page["type"] == "pdf":
        body = clean_text(clean_pdf(resp.content))
    else:
        resp.encoding = resp.apparent_encoding  # 政府站常见 GBK
        body = clean_text(clean_html(resp.text))
    if len(body) < 200:
        raise ValueError(f"清洗后正文过短({len(body)}字)，多半没抓到正文")
    return body


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    failures = []
    # 支持只抓指定文件：python scripts/crawl_corpus.py 高血压食养指南2023.md …
    # （V2 S5 只补两份新语料，不重抓已入库的旧来源——Mayo 拉伸页已改版，重抓会变差）
    only = set(sys.argv[1:])

    for src in SOURCES:
        if only and src["file"] not in only:
            continue
        print(f"== {src['file']} ({src['doc_name']}) ==")
        bodies, ok_urls = [], []
        for page in src["pages"]:
            url = page["url"]
            print(f"  抓取 {url}")
            try:
                bodies.append(crawl_page(page))
                ok_urls.append(url)
            except Exception as e:  # noqa: BLE001
                print(f"  [失败] {url} -> {e}")
                failures.append((src["file"], url, str(e)))
            time.sleep(2)  # 来源之间限速

        # 主源全失败 → 试备源（V2 文档 4.3.1：主源失效/403 则用备源）
        if not bodies:
            for page in src.get("backup_pages", []):
                url = page["url"]
                print(f"  [备源] 抓取 {url}")
                try:
                    bodies.append(crawl_page(page))
                    ok_urls.append(url)
                    break
                except Exception as e:  # noqa: BLE001
                    print(f"  [失败] {url} -> {e}")
                    failures.append((src["file"], url, str(e)))
                time.sleep(2)

        # 正文起点（跳过封面/目录）：标记在目录里也会出现，取【最后一次】出现的位置
        for marker in src.get("start_markers", []):
            for i, b in enumerate(bodies):
                pos = b.rfind(marker)
                if pos > 0:
                    bodies[i] = b[pos:]
                    print(f"  [起点] 从最后一个「{marker}」开始（跳过 {pos} 字封面/目录）")
        # 附录/食谱示例截断（V2 文档 4.3.1：各地食谱套餐示例可略）；同样取最后一次出现
        for marker in src.get("truncate_markers", []):
            for i, b in enumerate(bodies):
                pos = b.rfind(marker)
                if pos > 500:
                    bodies[i] = b[:pos]
                    print(f"  [截断] 在最后一个「{marker}」处截去附录（保留 {pos} 字）")

        out = CORPUS_DIR / src["file"]
        header = (f"<!-- doc_name: {src['doc_name']}, category: {src['category']}, "
                  f"source_url: {'; '.join(u for u in ok_urls) or src['pages'][0]['url']}, "
                  f"抓取日期: {date.today().isoformat()} -->\n\n# {src['doc_name']}\n\n")
        if bodies:
            out.write_text(header + "\n\n".join(bodies), encoding="utf-8")
            print(f"  [完成] 写入 {out}（{sum(len(b) for b in bodies)} 字）")
        else:
            out.write_text(header + "（抓取失败，待人工复制正文补齐）\n", encoding="utf-8")
            print(f"  [占位] {out} 全部来源失败，需人工补齐")

    print("\n==== 汇总 ====")
    if failures:
        print("以下来源需人工补齐：")
        for f in failures:
            print(f"  - {f[0]}: {f[1]} ({f[2][:80]})")
    else:
        print("全部来源抓取成功。")


if __name__ == "__main__":
    sys.exit(main())
