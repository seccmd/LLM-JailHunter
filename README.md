# 🛡️ LLM-JailHunter 越狱猎手 — LLM 越狱攻击检测系统

> 🔍 自动化检测多个 LLM 是否被越狱，生成可视化安全报告

`LLM-JailHunter`（越狱猎手）是一个用于评估大语言模型（LLM）在面对**越狱提示（Jailbreak Prompt）**时安全性的开源工具。它支持：

✅ 多模型并行测试（兼容 OpenAI 接口）  
✅ 自动越狱风险评分（0-10）  
✅ 支持角色扮演、绕过、伪装等 20+ 种越狱类型  
✅ 生成 HTML 可视化报告（含展开详情、分类统计）  
✅ 完全本地运行，支持 `.env` 密钥管理  

---

### 🚀 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/yourname/LLM-JailHunter.git
cd LLM-JailHunter

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置密钥
cp .env.example .env
# 编辑 .env，填入你的 API Key

# 4. 运行检测
python main.py

# 5. 查看报告
# 生成：report.html（浏览器打开）
```

### 📂 项目结构

```
LLM-JailHunter/
├── main.py                 # 主程序
├── config.py               # 配置加载（.env + JSON）
├── llm_client.py           # 调用被测 LLM
├── evaluator.py            # 越狱评估器（裁判模型）
├── reporter.py             # 报告生成（JSON + HTML）
├── prompts.json            # 越狱提示词库（含分类）
├── llm_configs.json        # 被测 LLM 配置
├── .env                    # API 密钥（本地）
├── .env.example            # 密钥模板
├── results.json            # 原始结果
├── report.json             # 安全评估报告
└── report.html             # 可视化 HTML 报告
```
