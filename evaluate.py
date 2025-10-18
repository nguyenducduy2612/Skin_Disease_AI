import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

# =============================
# 1️⃣ Cấu hình & Load model
# =============================
classes = ["acne", "eczema", "melanoma", "psoriasis", "normal"]

test_dir = "dataset_final/test"
model_path = "mobilenetv2_skin_finetuned.h5"

print("🔄 Đang load model...")
model = load_model(model_path)
print("✅ Model đã load thành công:", model_path)

# =============================
# 2️⃣ Chuẩn bị dữ liệu test
# =============================
datagen = ImageDataGenerator(rescale=1.0/255)

test_gen = datagen.flow_from_directory(
    test_dir,
    target_size=(224, 224),
    batch_size=16,
    class_mode='categorical',
    shuffle=False  # rất quan trọng để giữ thứ tự khi vẽ confusion matrix
)

# =============================
# 3️⃣ Đánh giá mô hình tổng thể
# =============================
loss, acc = model.evaluate(test_gen)
print(f"🎯 Độ chính xác trên test set: {acc*100:.2f}%")
print(f"📉 Mất mát (Loss): {loss:.4f}")

# =============================
# 4️⃣ Biểu đồ Loss & Accuracy theo batch
# =============================
print("📊 Đang tính toán Loss/Accuracy theo batch...")

batch_losses = []
batch_accuracies = []

for i in range(len(test_gen)):
    X_batch, y_batch = test_gen[i]
    batch_loss, batch_acc = model.evaluate(X_batch, y_batch, verbose=0)
    batch_losses.append(batch_loss)
    batch_accuracies.append(batch_acc)

plt.figure(figsize=(12,5))

plt.subplot(1,2,1)
plt.plot(batch_losses, marker='o')
plt.title('Biểu đồ Loss theo batch')
plt.xlabel('Batch')
plt.ylabel('Loss')

plt.subplot(1,2,2)
plt.plot(batch_accuracies, color='green', marker='o')
plt.title('Biểu đồ Accuracy theo batch')
plt.xlabel('Batch')
plt.ylabel('Accuracy')

plt.tight_layout()
plt.show()

# =============================
# 5️⃣ Vẽ Confusion Matrix
# =============================
print("📈 Đang tính toán Confusion Matrix...")

# Dự đoán toàn bộ test set
y_true = test_gen.classes
y_pred = model.predict(test_gen)
y_pred_classes = np.argmax(y_pred, axis=1)

# Ma trận nhầm lẫn
cm = confusion_matrix(y_true, y_pred_classes)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=classes)

plt.figure(figsize=(8,6))
disp.plot(cmap='Blues', xticks_rotation=45)
plt.title("Biểu đồ Confusion Matrix mô hình")
plt.show()

print("✅ Đã hoàn tất đánh giá và trực quan hóa mô hình!")
