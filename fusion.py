import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from openai import OpenAI
from dotenv import load_dotenv

# --- Load biến môi trường ---
load_dotenv()

# --- Lấy API key ---
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ Không tìm thấy OPENAI_API_KEY trong file .env")

# --- Khởi tạo OpenAI client ---
client = OpenAI(api_key=api_key)

# --- Load model CNN ---
IMG_SIZE = 224
CLASSES = ["acne", "eczema", "melanoma", "psoriasis", "normal"]

model = load_model("mobilenetv2_skin_finetuned.h5")
print("✅ Đã load model CNN: mobilenetv2_skin_finetuned.h5")

# --- Hàm dự đoán ảnh ---
def predict_image(img_path):
    """Dự đoán lớp bệnh từ ảnh bằng CNN"""
    img = image.load_img(img_path, target_size=(IMG_SIZE, IMG_SIZE))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    preds = model.predict(img_array)
    pred_class = CLASSES[np.argmax(preds[0])]
    confidence = np.max(preds[0])
    return pred_class, float(confidence)

# --- Hàm GPT phân tích text ---
def analyze_symptoms(description: str) -> str:
    """GPT phân tích mô tả triệu chứng"""
    prompt = f"""
    Bạn là bác sĩ da liễu có kinh nghiệm.
    Hãy đọc phần mô tả sau và trả lời thật ngắn gọn:
    1️⃣ Dự đoán bệnh da liễu thuộc 1 trong 5 lớp: acne, eczema, melanoma, psoriasis, normal.
    2️⃣ Đánh giá mức độ nghiêm trọng (nhẹ, trung bình, nặng).
    3️⃣ Gợi ý hướng xử lý hoặc điều trị cơ bản (1 câu).
    4️⃣ Nếu là 'normal', nói rõ là da bình thường, khỏe mạnh.

    Triệu chứng: {description}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Bạn là bác sĩ da liễu ảo, trả lời ngắn gọn, chuyên môn và dễ hiểu."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        temperature=0.4
    )
    return response.choices[0].message.content.strip()

# --- Hàm GPT kết hợp kết quả CNN + text ---
def combine_results(cnn_result, gpt_result):
    """Kết hợp kết quả CNN và GPT thành chẩn đoán cuối cùng"""
    final_prompt = f"""
    Tôi có 2 nguồn chẩn đoán bệnh da liễu:
    - Mô hình CNN dự đoán: {cnn_result}
    - GPT phân tích mô tả: {gpt_result}

    Hãy tổng hợp và đưa ra kết luận ngắn gọn (1-2 câu):
    - Bệnh có khả năng cao nhất là gì (chỉ chọn 1 trong: acne, eczema, melanoma, psoriasis, normal).
    - Mức độ nghiêm trọng (nhẹ, trung bình, nặng).
    - Gợi ý hành động hoặc hướng xử lý cơ bản.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Bạn là bác sĩ da liễu ảo, trả lời cực kỳ ngắn gọn và thực tế."},
            {"role": "user", "content": final_prompt}
        ],
        max_tokens=120,
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

# ✅ Không cần đoạn test main nữa, Flask sẽ gọi các hàm này.
