# config.py
import os
import json
from typing import List, Dict
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class ConfigLoader:
    @staticmethod
    def _ensure_file_exists(path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"配置文件未找到: {path}")

    @staticmethod
    def load_prompts(file_path: str = "prompts.json") -> List[str]:
        """加载越狱提示词列表"""
        ConfigLoader._ensure_file_exists(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError(f"{file_path} 必须是一个数组")
        print(f"✅ 已加载 {len(data)} 条越狱测试提示")
        return data

    @staticmethod
    def load_llm_configs(file_path: str = "llm_configs.json") -> List[Dict]:
        """加载被测 LLM 配置，并注入 API Key"""
        ConfigLoader._ensure_file_exists(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            configs = json.load(f)

        if not isinstance(configs, list):
            raise ValueError(f"{file_path} 必须是一个数组")

        valid_configs = []
        for cfg in configs:
            name = cfg.get("name")
            enabled = cfg.get("enabled", False)
            base_url = cfg.get("base_url")
            model = cfg.get("model")
            api_key_env = cfg.get("api_key_env")

            if not enabled:
                print(f"🟡 跳过 LLM: {name} (已禁用)")
                continue

            required = ["name", "base_url", "model", "api_key_env"]
            missing = [k for k in required if not cfg.get(k)]
            if missing:
                print(f"❌ 跳过 {name}：缺少字段 {missing}")
                continue

            api_key = os.getenv(api_key_env)
            if not api_key:
                print(f"❌ 跳过 {name}：环境变量 {api_key_env} 未设置")
                continue

            cfg_with_key = cfg.copy()
            cfg_with_key["api_key"] = api_key
            valid_configs.append(cfg_with_key)

        if not valid_configs:
            raise RuntimeError("❌ 没有有效的被测 LLM 配置")

        print(f"✅ 成功加载 {len(valid_configs)} 个启用的被测 LLM")
        return valid_configs

    @staticmethod
    def get_judge_model() -> ChatOpenAI:
        """获取裁判模型实例（用于越狱评估）"""
        JUDGE_API_KEY = os.getenv("JUDGE_API_KEY")
        JUDGE_BASE_URL = os.getenv("JUDGE_BASE_URL", "https://api.openai.com/v1")
        JUDGE_MODEL_NAME = os.getenv("JUDGE_MODEL_NAME", "gpt-4o")

        if not JUDGE_API_KEY:
            raise EnvironmentError("❌ 请在 .env 中设置 JUDGE_API_KEY")

        print(f"🧠 初始化裁判模型: {JUDGE_MODEL_NAME}")

        return ChatOpenAI(
            model=JUDGE_MODEL_NAME,
            base_url=JUDGE_BASE_URL,
            api_key=JUDGE_API_KEY,
            temperature=0,
            timeout=30,
            max_retries=2,
        )