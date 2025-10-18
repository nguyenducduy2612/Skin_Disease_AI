import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import os

# Cấu hình
IMG_SIZE = 224
classes = ["acne", "eczema", "melanoma", "psoriasis", "normal"]

# Load model
model = load_model("mobilenetv2_skin_finetuned.h5")
print("✅ Loaded model từ mobilenetv2_skin_new.h5")

# Thư mục chứa ảnh cần dự đoán
predict_dir = "predict_images"

def predict_image(img_path):
    img = image.load_img(img_path, target_size=(IMG_SIZE, IMG_SIZE))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    preds = model.predict(img_array)
    pred_class = classes[np.argmax(preds[0])]
    confidence = np.max(preds[0])
    print(f"Ảnh: {os.path.basename(img_path)} ➝ {pred_class} ({confidence:.2f})")

# Dự đoán hàng loạt
if os.path.exists(predict_dir):
    files = [f for f in os.listdir(predict_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    print(f"📸 Tìm thấy {len(files)} ảnh trong {predict_dir}")
    for f in files:
        predict_image(os.path.join(predict_dir, f))
else:
    print("❌ Không tìm thấy thư mục predict_images!")
