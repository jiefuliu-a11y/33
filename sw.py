# requirements:
# pip install openai requests

import os
import requests
import json
from pathlib import Path

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # 请先在环境变量设置
AUDIO_FILE = "meeting.mp3"  # 本地会议音频

def transcribe_audio(audio_path):
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    with open(audio_path, "rb") as f:
        files = {"file": ("meeting.mp3", f, "audio/mpeg")}
        data = {"model": "whisper-1"}  # 或使用最新的 speech model 名称
        r = requests.post(url, headers=headers, data=data, files=files)
    r.raise_for_status()
    return r.json()["text"]

def summarize_meeting(transcript_text):
    # 用 Chat Completion / Responses API 调用 GPT 生成结构化纪要
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    system_prompt = "你是一个专业的会议纪要助理。请从下面的逐字转录中提取：1) 会议标题 2) 会议时间 3) 参会人员 4) 主要议题 5) 每个议题的要点（带简短摘要） 6) 决议/决定 7) 行动项（含建议负责人和截止时间） 8) 关键词。输出为严格的 JSON。"
    user_prompt = transcript_text[:30000]  # 限制长度
    payload = {
        "model": "gpt-4o-mini",  # 或选择合适模型
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.0,
        "max_tokens": 1200,
    }
    r = requests.post(url, headers=headers, json=payload)
    r.raise_for_status()
    res = r.json()
    # 解析 assistant 的内容（取第一个）
    content = res["choices"][0]["message"]["content"]
    try:
        data = json.loads(content)
    except Exception as e:
        # 如果模型没有返回严格 JSON，可尝试用正则/分段解析或再次请求
        print("模型返回非 JSON，内容为：", content)
        raise
    return data

def main():
    transcript = transcribe_audio(AUDIO_FILE)
    print("转录结果（开头 200 字）：", transcript[:200])
    summary = summarize_meeting(transcript)
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
