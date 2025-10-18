from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chat_with_ai(message):
    """Trả lời tư vấn y tế ngắn gọn"""
    prompt = f"""
    Bạn là bác sĩ da liễu ảo. Trả lời ngắn gọn, rõ ràng, thân thiện.
    Người dùng hỏi: "{message}"
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Bạn là bác sĩ da liễu ảo thân thiện và chuyên nghiệp."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=150
    )
    return response.choices[0].message.content.strip()
