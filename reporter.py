# reporter.py
import json
from datetime import datetime


def generate_report(results: list, json_path: str = "report.json", html_path: str = "report.html"):
    """
    生成 JSON 和 HTML 报告
    :param results: 测试结果列表
    :param json_path: JSON 报告路径
    :param html_path: HTML 报告路径
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    year = datetime.now().year

    # 统计数据
    total = len(results)
    jailbreak_count = sum(1 for r in results if r.get("evaluation", {}).get("is_jailbreak", False))
    jailbreak_rate = round(jailbreak_count / total * 100 if total > 0 else 0, 1)

    # === 按 category 统计 ===
    category_stats = {}
    for r in results:
        cat = r.get("category", "unknown")
        if cat not in category_stats:
            category_stats[cat] = {"total": 0, "jailbreak": 0}
        category_stats[cat]["total"] += 1
        if r["evaluation"]["is_jailbreak"]:
            category_stats[cat]["jailbreak"] += 1

    category_rows = ""
    for cat, stats in category_stats.items():
        rate = round(stats["jailbreak"] / stats["total"] * 100, 1)
        category_rows += f"""
                <tr>
                    <td>{cat}</td>
                    <td>{stats['total']}</td>
                    <td>{stats['jailbreak']}</td>
                    <td>{rate}%</td>
                </tr>"""

    # === 生成 JSON 报告 ===
    report_data = {
        "generated_time": now,
        "total_tests": total,
        "jailbreak_success": jailbreak_count,
        "jailbreak_rate_percent": jailbreak_rate,
        "category_breakdown": {
            cat: {
                "total": stats["total"],
                "jailbreak": stats["jailbreak"],
                "success_rate_percent": round(stats["jailbreak"] / stats["total"] * 100, 1)
            }
            for cat, stats in category_stats.items()
        },
        "results": results
    }

    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        print(f"📊 JSON 报告已生成：{json_path}")
    except Exception as e:
        print(f"❌ 保存 JSON 报告失败：{e}")

    # === 转义 HTML 特殊字符 ===
    def escape_html(text):
        return (str(text)
                .replace("&", "&amp;")
                .replace("<", "<")
                .replace(">", ">")
                .replace("\"", "&quot;"))

    # === 排序：高风险在前 ===
    sorted_results = sorted(
        results,
        key=lambda x: {"high": 2, "medium": 1, "low": 0}.get(x["evaluation"]["risk_level"], 0),
        reverse=True
    )

    # === 生成折叠式表格行（行内展开）===
    table_rows = ""
    for idx, r in enumerate(sorted_results):
        llm = escape_html(r['llm'])
        category = escape_html(r['category'])
        prompt_short = escape_html(r['prompt'][:60] + "..." if len(r['prompt']) > 60 else r['prompt'])
        score = r['evaluation']['score']
        risk = r['evaluation']['risk_level']
        risk_class = f"risk-{risk}"
        risk_text = risk.upper()

        # 详情内容
        full_prompt = escape_html(r['prompt'])
        description = escape_html(r.get('description', 'N/A'))
        response_full = escape_html(r['response'])
        reason = escape_html(r['evaluation']['reason'])

        # 主行（带展开按钮）
        main_row = f"""
                <tr class="main-row">
                    <td>{llm}</td>
                    <td class="category">{category}</td>
                    <td class="prompt" title="{full_prompt}">{prompt_short}</td>
                    <td><span class="{risk_class}">{risk_text}</span></td>
                    <td>{score}</td>
                    <td><button onclick="toggleDetail('detail-{idx}')">展开详情</button></td>
                </tr>"""

        # 详情行（隐藏，点击后显示）
        detail_row = f"""
                <tr id="detail-{idx}" style="display: none;">
                    <td colspan="6" style="background: #f1f8ff; padding: 15px; border-top: none;">
                        <div style="font-size: 0.95em; line-height: 1.7;">
                            <p><strong>完整提示词：</strong><br><em>{full_prompt}</em></p>
                            <p><strong>说明：</strong> {description}</p>
                            <p><strong>模型响应：</strong><br><pre style="background:#fff; padding:10px; border-radius:4px; overflow:auto; max-height:200px; margin:0;">{response_full}</pre></p>
                            <p><strong>评估理由：</strong> {reason}</p>
                        </div>
                    </td>
                </tr>"""

        table_rows += main_row + detail_row

    # === HTML 模板（添加 JavaScript 控制展开）===
    HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>LLM 越狱攻击检测报告</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script>
        function toggleDetail(id) {{
            const row = document.getElementById(id);
            const button = event.target;
            if (row.style.display === "none") {{
                row.style.display = "";
                button.textContent = "收起详情";
            }} else {{
                row.style.display = "none";
                button.textContent = "展开详情";
            }}
        }}
    </script>
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; background: #f8f9fa; }}
    .container {{ max-width: 1000px; margin: 0 auto; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
    header {{ text-align: center; margin-bottom: 30px; }}
    h1 {{ color: #d6336c; }}
    .meta {{ color: #6c757d; font-size: 0.9em; margin-bottom: 20px; }}
    .summary, .category-summary {{ background: #f8f9fa; padding: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 30px; border: 1px solid #eee; }}
    .summary-item {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee; }}
    .summary-label {{ font-weight: bold; }}
    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; border: 1px solid #eee; }}
    th, td {{ padding: 12px 12px; text-align: left; border-bottom: 1px solid #eee; }}
    th {{ background-color: #007bff; color: white; font-weight: 600; }}
    tr:hover {{ background-color: #f1f8ff; }}
    .risk-high {{ color: #d6336c; font-weight: bold; }}
    .risk-medium {{ color: #fd7e14; }}
    .risk-low {{ color: #198754; }}
    .prompt {{ max-width: 250px; overflow: hidden; text-overflow: ellipsis; }}
    button {{ background: #007bff; color: white; border: none; padding: 6px 10px; border-radius: 4px; font-size: 0.85em; cursor: pointer; }}
    button:hover {{ background: #0056b3; }}
    pre {{ 
        white-space: pre-wrap; 
        word-wrap: break-word; 
        word-break: break-word; 
        overflow-wrap: break-word; 
        overflow: auto; 
        max-height: 200px; 
        margin: 0; 
        padding: 10px; 
        background: #fff; 
        border: 1px solid #eee; 
        border-radius: 4px; 
        font-family: 'Courier New', monospace; 
        font-size: 0.9em; 
        line-height: 1.5; 
    }}
    footer {{ text-align: center; margin-top: 50px; color: #adb5bd; font-size: 0.8em; padding-top: 20px; border-top: 1px solid #eee; }}
</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🛡️ LLM 越狱攻击检测报告</h1>
            <div class="meta"><strong>生成时间：</strong>{generated_time}</div>
        </header>

        <div class="summary">
            <div class="summary-item"><span class="summary-label">总测试数：</span><span>{total}</span></div>
            <div class="summary-item"><span class="summary-label">越狱成功数：</span><span>{jailbreak_count}</span></div>
            <div class="summary-item"><span class="summary-label">越狱成功率：</span><span>{jailbreak_rate}%</span></div>
        </div>

        <h2>📊 按攻击类型统计</h2>
        <div class="category-summary">
            <table>
                <thead>
                    <tr>
                        <th>攻击类型 (category)</th>
                        <th>测试数</th>
                        <th>成功数</th>
                        <th>成功率</th>
                    </tr>
                </thead>
                <tbody>
{category_rows}
                </tbody>
            </table>
        </div>

        <h2>📋 详细测试结果（高风险优先）</h2>
        <table>
            <thead>
                <tr>
                    <th>LLM</th>
                    <th>类型</th>
                    <th>提示词（预览）</th>
                    <th>风险等级</th>
                    <th>评分</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
{table_rows}
            </tbody>
        </table>

        <footer>
            &copy; {year} LLM 安全评估系统
        </footer>
    </div>
</body>
</html>
"""

    try:
        html_content = HTML_TEMPLATE.format(
            generated_time=now,
            total=total,
            jailbreak_count=jailbreak_count,
            jailbreak_rate=jailbreak_rate,
            category_rows=category_rows,
            table_rows=table_rows,
            year=year
        )

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"📊 HTML 报告已生成：{html_path}")
    except Exception as e:
        print(f"❌ 生成 HTML 报告失败：{e}")