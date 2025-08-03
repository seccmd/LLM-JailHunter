# main.py
import asyncio
import json
from typing import List, Dict
from config import ConfigLoader
from llm_client import query_target_llm
from evaluator import evaluate_jailbreak
from reporter import generate_report

# 配置
PROMPTS_FILE = "prompts.json"
LLM_CONFIGS_FILE = "llm_configs.json"
RESULTS_FILE = "results.json"


async def evaluate_single_case(prompt_data: Dict, llm_config: Dict) -> Dict:
    """
    对单个 prompt + 单个 LLM 进行越狱检测
    :param prompt_data: 包含 prompt, category, description 的字典
    :param llm_config: LLM 配置
    :return: 测试结果
    """
    prompt_text = prompt_data["prompt"]
    print(f"\n🔍 测试 LLM: {llm_config['name']} | 类型: {prompt_data['category']} | 提示: {prompt_text[:50]}...")

    # 1. 查询目标模型
    response = await query_target_llm(prompt_text, llm_config)

    # 2. 越狱评估
    eval_result = await evaluate_jailbreak(prompt_text, response)

    # 3. 返回结构化结果（包含分类信息）
    return {
        "prompt": prompt_text,
        "category": prompt_data["category"],
        "description": prompt_data["description"],
        "llm": llm_config["name"],
        "model": llm_config["model"],
        "response": response,
        "evaluation": eval_result
    }


async def main():
    print("🛡️ 启动 LLM 越狱攻击检测系统...")

    try:
        # 加载配置
        prompts: List[Dict] = ConfigLoader.load_prompts(PROMPTS_FILE)  # 现在是 dict 列表
        llm_configs: List[Dict] = ConfigLoader.load_llm_configs(LLM_CONFIGS_FILE)

        if not prompts:
            print("❌ 没有加载到任何提示词，程序退出。")
            return
        if not llm_configs:
            print("❌ 没有启用的 LLM 配置，程序退出。")
            return

        # 生成所有测试任务（每个 LLM × 每个 prompt）
        tasks = [
            evaluate_single_case(prompt_data, llm_config)
            for llm_config in llm_configs
            for prompt_data in prompts
        ]

        # 并行执行所有任务
        results = await asyncio.gather(*tasks)

        # 保存原始结果
        with open(RESULTS_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"✅ 原始结果已保存至 {RESULTS_FILE}")

        # ✅ 生成增强报告（含分类信息）
        generate_report(results, json_path="report.json", html_path="report.html")

        # 汇总统计
        total = len(results)
        jailbreak_count = sum(1 for r in results if r["evaluation"]["is_jailbreak"])
        success_rate = jailbreak_count / total if total > 0 else 0

        print(f"\n📈 最终统计")
        print(f"   总测试数: {total}")
        print(f"   越狱成功: {jailbreak_count}")
        print(f"   成功率: {success_rate:.1%}")
        print(f"✅ 所有结果已保存至:")
        print(f"   - {RESULTS_FILE}")
        print(f"   - report.json")
        print(f"   - report.html")

    except Exception as e:
        print(f"💥 系统异常：{e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())