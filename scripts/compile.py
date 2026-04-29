#!/usr/bin/env python3
"""
知识编译脚本 v2 - Two-Step LLM 分析

改进:
1. 不是简单复制，而是 LLM 分析提炼
2. 自动发现链接关系
3. 更新知识图谱

依赖:
- anthropic SDK (pip install anthropic)
- 或使用环境变量配置其他 LLM
"""

import json
import hashlib
import os
import re
from pathlib import Path
from datetime import datetime

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    print("提示: 安装 anthropic SDK 进行真实编译: pip install anthropic")

BASE_DIR = Path(__file__).parent.parent
CURATED_DIR = BASE_DIR / "curated"
WIKI_DIR = BASE_DIR / "wiki"
GRAPH_DIR = BASE_DIR / "graph"

# 编译规则
COMPILE_RULES = {
    "core": {
        "source": "curated/*.md",
        "target": "wiki/core/",
        "must_link_to": ["AGENTS", "CODING_STANDARDS", "USER_GUIDE"]
    },
    "patterns": {
        "source": "curated/patterns/*.md",
        "target": "wiki/patterns/",
        "must_link_to": ["patterns/slp-business-development-standard"]
    },
    "tools": {
        "source": "curated/tools/*.md",
        "target": "wiki/tools/",
        "must_link_to": ["tools/slpctl-usage-guide"]
    },
    "projects": {
        "source": "curated/projects/**/*.md",
        "target": "wiki/projects/",
        "must_link_to": []
    },
    "cross-projects": {
        "source": "curated/cross-projects/**/*.md",
        "target": "wiki/cross-projects/",
        "must_link_to": []
    }
}

def get_file_hash(fpath):
    """计算文件 hash"""
    return hashlib.sha256(open(fpath, 'rb').read()).hexdigest()

def load_cached_hash(wiki_file):
    """加载缓存的 hash"""
    if not wiki_file.exists():
        return None

    content = wiki_file.read_text()
    match = re.search(r'^source_hash:\s*(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None

def call_llm_analyze(source_content, existing_nodes_preview):
    """Step 1: LLM 分析素材"""
    if not HAS_ANTHROPIC:
        # Mock 返回（无 API 时）
        return {
            "key_entities": [],
            "key_points": [],
            "suggested_links": [],
            "summary_200": "（需要 LLM API 才能生成摘要）",
            "tables": []
        }

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    prompt = f"""分析以下文档，提取结构化知识。

文档内容:
{source_content[:8000]}

现有知识库节点概览:
{existing_nodes_preview}

请输出 JSON 格式:
{
  "key_entities": [
    {"name": "实体名", "type": "concept|person|project|tool", "importance": "high|medium|low"}
  ],
  "key_points": [
    {"point": "关键点描述", "evidence": "证据/代码位置"}
  ],
  "suggested_links": [
    {"to": "节点ID", "type": "relates_to|depends_on|builds_on", "reason": "链接理由"}
  ],
  "summary_200": "200字精简摘要",
  "tables": [
    {
      "title": "表格标题",
      "headers": ["列1", "列2"],
      "rows": [["值1", "值2"]]
    }
  ]
}

只输出 JSON，不要其他内容。"""

    message = client.messages.create(
        model="claude-sonnet-4-6-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text

    # 解析 JSON
    try:
        # 清理可能的 markdown 代码块标记
        cleaned = response_text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r'^```\w*\n?', '', cleaned)
            cleaned = re.sub(r'\n?```$', '', cleaned)
        return json.loads(cleaned)
    except json.JSONDecodeError:
        print(f"LLM 返回解析失败: {response_text[:200]}")
        return None

def call_llm_generate(analysis, source_title, doc_type):
    """Step 2: LLM 生成 wiki 页面"""
    if not HAS_ANTHROPIC:
        # Mock 返回
        return f"""# {source_title}

> 此页面需要 LLM API 生成完整内容

## 概述

（摘要待生成）

## 关键内容

（内容待生成）

## 相关知识

- [[CODING_STANDARDS]]
"""

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    prompt = f"""基于以下分析结果，生成精简的 wiki 页面（Markdown 格式）。

分析结果:
{json.dumps(analysis, ensure_ascii=False, indent=2)}

要求:
1. 标题简洁
2. 内容表格化（便于 AI 快速理解）
3. 使用 [[wikilinks]] 链接到相关节点
4. 精简，去掉冗余内容
5. 保持原文的核心信息

输出 Markdown 格式，以 # 标题开始。"""

    message = client.messages.create(
        model="claude-sonnet-4-6-20250514",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text

def compile_file(source_file, target_dir, existing_nodes):
    """编译单个文件"""
    # 检查缓存
    source_hash = get_file_hash(source_file)

    # 确定目标路径
    source_name = source_file.stem
    target_file = target_dir / f"{source_name}.md"

    cached_hash = load_cached_hash(target_file)
    if cached_hash and cached_hash == source_hash:
        return {"status": "skipped", "reason": "未变更"}

    # 读取源文件
    source_content = source_file.read_text()
    source_title = source_name

    # 确定文档类型
    doc_type = "standard"
    if any(x in str(source_file) for x in ["guide", "指南"]):
        doc_type = "guide"
    elif any(x in str(source_file) for x in ["example", "示例"]):
        doc_type = "example"
    elif any(x in str(source_file) for x in ["overview", "概览"]):
        doc_type = "overview"

    # 现有节点预览
    nodes_preview = json.dumps(
        [{"id": n["id"], "label": n.get("label", "")} for n in existing_nodes[:30]],
        ensure_ascii=False
    )

    # Step 1: 分析
    print(f"  分析: {source_file.name}")
    analysis = call_llm_analyze(source_content, nodes_preview)

    if not analysis:
        return {"status": "failed", "reason": "LLM 分析失败"}

    # Step 2: 生成
    print(f"  生成: {target_file.name}")
    wiki_content = call_llm_generate(analysis, source_title, doc_type)

    # 写入 wiki 文件
    node_id = str(source_file.relative_to(CURATED_DIR)).replace(".md", "").replace("/", "/")

    frontmatter = f"""---
id: {node_id}
type: {doc_type}
source_file: {str(source_file.relative_to(BASE_DIR))}
sources: [{str(source_file.relative_to(BASE_DIR))}]
compiled: {datetime.now().isoformat()}
source_hash: {source_hash}
tags: {json.dumps(analysis.get("key_entities", [])[:5], ensure_ascii=False)}
links_to: {json.dumps([l["to"] for l in analysis.get("suggested_links", [])], ensure_ascii=False)}
---

"""

    target_dir.mkdir(parents=True, exist_ok=True)
    target_file.write_text(frontmatter + wiki_content)

    # 更新图谱
    update_graph(node_id, target_file, analysis)

    return {
        "status": "compiled",
        "analysis": analysis,
        "target": str(target_file)
    }

def update_graph(node_id, wiki_file, analysis):
    """更新知识图谱"""
    # 更新 nodes.jsonl
    node_record = {
        "id": node_id,
        "path": str(wiki_file.relative_to(BASE_DIR)),
        "type": "compiled",
        "compiled": datetime.now().isoformat(),
        "entities": [e["name"] for e in analysis.get("key_entities", [])]
    }

    # 检查是否已存在
    existing_nodes = []
    with open(GRAPH_DIR / "nodes.jsonl") as f:
        for line in f:
            if line.startswith("#"):
                continue
            existing_nodes.append(json.loads(line))

    # 移除旧记录，添加新记录
    existing_nodes = [n for n in existing_nodes if n["id"] != node_id]
    existing_nodes.append(node_record)

    with open(GRAPH_DIR / "nodes.jsonl", "w") as f:
        f.write(f"# nodes.jsonl - 节点索引\n")
        f.write(f"# 更新时间: {datetime.now().isoformat()}\n")
        f.write("#\n")
        for n in existing_nodes:
            f.write(json.dumps(n, ensure_ascii=False) + "\n")

    # 添加边
    for link in analysis.get("suggested_links", []):
        edge = {
            "from": node_id,
            "to": link["to"],
            "type": link["type"],
            "weight": 2.0 if link["type"] == "depends_on" else 1.0,
            "discovered_by": "compile_llm",
            "created": datetime.now().isoformat()
        }

        with open(GRAPH_DIR / "edges.jsonl", "a") as f:
            f.write(json.dumps(edge, ensure_ascii=False) + "\n")

def compile_category(category, existing_nodes):
    """编译一个类别"""
    rule = COMPILE_RULES.get(category)
    if not rule:
        return []

    source_dir = CURATED_DIR
    target_dir = WIKI_DIR / category

    results = []

    # 找源文件
    source_pattern = rule["source"].replace("curated/", "")
    if "*" in source_pattern:
        # glob 搜索
        source_files = list(CURATED_DIR.rglob(source_pattern.replace("*", "**")))
        # 过滤 .md
        source_files = [f for f in source_files if f.suffix == ".md"]
    else:
        source_files = [CURATED_DIR / source_pattern]

    for source_file in source_files:
        result = compile_file(source_file, target_dir, existing_nodes)
        results.append(result)

    return results

def main():
    print("=== 知识编译 v2 ===\n")

    if not HAS_ANTHROPIC:
        print("警告: 未安装 anthropic SDK，将生成占位内容")
        print("安装: pip install anthropic")
        print("配置: export ANTHROPIC_API_KEY=your-key\n")

    # 加载现有节点
    existing_nodes = []
    with open(GRAPH_DIR / "nodes.jsonl") as f:
        for line in f:
            if line.startswith("#"):
                continue
            existing_nodes.append(json.loads(line))

    print(f"现有节点: {len(existing_nodes)}\n")

    # 编译范围
    categories = ["core", "patterns", "tools", "projects", "cross-projects"]

    total_stats = {
        "compiled": 0,
        "skipped": 0,
        "failed": 0,
        "links_discovered": 0
    }

    for category in categories:
        print(f"编译 [{category}]...")
        results = compile_category(category, existing_nodes)

        for r in results:
            if r["status"] == "compiled":
                total_stats["compiled"] += 1
                links = len(r.get("analysis", {}).get("suggested_links", []))
                total_stats["links_discovered"] += links
                print(f"  ✓ {r['target']} (+{links} links)")
            elif r["status"] == "skipped":
                total_stats["skipped"] += 1
            else:
                total_stats["failed"] += 1
                print(f"  ✗ {r.get('reason', '未知错误')}")

        print()

    print("=== 编译完成 ===")
    print(f"编译: {total_stats['compiled']}")
    print(f"跳过: {total_stats['skipped']}")
    print(f"失败: {total_stats['failed']}")
    print(f"发现链接: {total_stats['links_discovered']}")

    print("\n建议: 运行 scripts/discover.py 检查知识缺口")

if __name__ == "__main__":
    main()