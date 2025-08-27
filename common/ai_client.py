import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

# 加载项目根目录的 .env 文件
load_dotenv()

def call_gitee_ai(prompt: str, model_name: str):
    """
    一个通用的函数，用于调用 Gitee AI 的任意模型。
    """
    api_key = os.getenv("GITEE_AI_API_KEY")
    if not api_key:
        print(f"错误：未在 .env 文件中找到 GITEE_AI_API_KEY！")
        return None

    # 修复URL：移除Markdown格式
    client = OpenAI(base_url="https://ai.gitee.com/v1", api_key=api_key)
    
    try:
        print(f"--- [Gitee AI Client] 正在调用模型: {model_name} ---")
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides concise and structured responses. Always respond with valid JSON format only, without any additional text or explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}  # 要求模型直接返回JSON
        )
        response_content = response.choices[0].message.content
        print(f"--- [Gitee AI Client] 模型返回: {response_content} ---")

        # 改进的JSON解析逻辑
        try:
            # 首先尝试直接解析
            return json.loads(response_content)
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试提取JSON部分
            print("--- [Gitee AI Client] 直接解析失败，尝试提取JSON部分 ---")
            json_match = re.search(r'\{[\s\S]*\}', response_content)
            if json_match:
                try:
                    json_string = json_match.group(0)
                    return json.loads(json_string)
                except json.JSONDecodeError as e:
                    print(f"--- [Gitee AI Client] JSON 解析错误: {e} ---")
                    print(f"--- 原始内容: {response_content} ---")
                    return None
            else:
                print(f"--- [Gitee AI Client] 错误: 在模型响应中未找到有效的 JSON ---")
                print(f"--- 原始内容: {response_content} ---")
                return None

    except Exception as e:
        print(f"--- [Gitee AI Client] 调用模型 {model_name} 或解析 JSON 时出错: {e} ---")
        return None