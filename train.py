import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers, models, optimizers, callbacks
import os

# --- 1️⃣ Cấu hình cơ bản ---
train_dir = "dataset_final/train"
val_dir = "dataset_final/val"
classes = ["acne", "eczema", "melanoma", "psoriasis", "normal"]

IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 30  # tăng số epoch vì có early stopping

# --- 2️⃣ Data augmentation mạnh hơn, giúp mô hình tổng quát tốt hơn ---
train_datagen = ImageDataGenerator(
    rescale=1.0/255,
    rotation_range=25,
    width_shift_range=0.15,
    height_shift_range=0.15,
    shear_range=0.1,
    zoom_range=0.25,
    horizontal_flip=True,
    brightness_range=[0.7, 1.3],
    fill_mode='nearest'
)

val_datagen = ImageDataGenerator(rescale=1.0/255)

train_gen = train_datagen.flow_from_directory(
    train_dir,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical'
)

val_gen = val_datagen.flow_from_directory(
    val_dir,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical'
)

# --- 3️⃣ Sử dụng MobileNetV2 với fine-tuning ---
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, 3))
base_model.trainable = False  # Giai đoạn đầu: đóng băng để train phần head

# --- 4️⃣ Xây phần head ---
model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.BatchNormalization(),
    layers.Dropout(0.4),
    layers.Dense(256, activation='relu'),
    layers.BatchNormalization(),
    layers.Dropout(0.4),
    layers.Dense(len(classes), activation='softmax')
])

# --- 5️⃣ Compile lần đầu ---
model.compile(
    optimizer=optimizers.Adam(learning_rate=1e-4),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# --- 6️⃣ Callback để tự điều chỉnh ---
early_stop = callbacks.EarlyStopping(
    monitor='val_loss', patience=5, restore_best_weights=True
)

reduce_lr = callbacks.ReduceLROnPlateau(
    monitor='val_loss', factor=0.3, patience=3, verbose=1, min_lr=1e-6
)

checkpoint = callbacks.ModelCheckpoint(
    "mobilenetv2_best_model.h5", monitor='val_accuracy',
    save_best_only=True, mode='max', verbose=1
)

# --- 7️⃣ Train giai đoạn 1: chỉ train phần head ---
history1 = model.fit(
    train_gen,
    epochs=EPOCHS,
    validation_data=val_gen,
    callbacks=[early_stop, reduce_lr, checkpoint]
)

# --- 8️⃣ Fine-tune: mở khóa phần cuối của MobileNetV2 ---
base_model.trainable = True
fine_tune_at = len(base_model.layers) - 40  # chỉ train 40 lớp cuối cùng

for layer in base_model.layers[:fine_tune_at]:
    layer.trainable = False

# Giảm learning rate cho fine-tuning
model.compile(
    optimizer=optimizers.Adam(learning_rate=1e-5),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# --- 9️⃣ Train giai đoạn 2: fine-tune ---
history2 = model.fit(
    train_gen,
    epochs=10,
    validation_data=val_gen,
    callbacks=[early_stop, reduce_lr, checkpoint]
)

# --- 🔟 Lưu model cuối cùng ---
model.save("mobilenetv2_skin_finetuned.h5")
print("✅ Đã train xong và lưu model fine-tuned thành công!")
