import os
from openai import OpenAI
from dotenv import load_dotenv

# --- Load biến môi trường từ file .env ---
load_dotenv()

# --- Lấy API key ---
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("❌ Không tìm thấy OPENAI_API_KEY. Hãy kiểm tra file .env!")

# --- Khởi tạo client ---
client = OpenAI(api_key=api_key)

def analyze_symptoms(description: str) -> str:
    """Phân tích mô tả triệu chứng bằng GPT"""
    prompt = f"""
    Hãy đọc phần mô tả triệu chứng sau và phân tích giúp tôi:
    1. Bệnh da liễu có thể là gì?
    2. Mức độ nghiêm trọng
    3. Gợi ý chẩn đoán hoặc hướng xử lý cơ bản.

    Triệu chứng: {description}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Bạn là bác sĩ da liễu ảo có kinh nghiệm."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()


# --- Test ---
if __name__ == "__main__":
    print("🩺 Nhập mô tả triệu chứng da liễu của bạn:")
    user_input = input("➡️  Triệu chứng: ").strip()

    if not user_input:
        print("⚠️ Bạn chưa nhập mô tả!")
    else:
        print("\n📋 Kết quả phân tích:")
        print(analyze_symptoms(user_input))
