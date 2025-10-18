import os
import shutil
from sklearn.model_selection import train_test_split

# Đường dẫn dataset hiện tại
dataset_dir = "dataset"
output_dir = "dataset_final"

# Tỷ lệ chia
val_ratio = 0.15
test_ratio = 0.15

# Các lớp
classes = ["acne", "eczema", "melanoma", "psoriasis", "normal"]

# Tạo thư mục train/val/test mới
for split in ["train", "val", "test"]:
    for cls in classes:
        os.makedirs(os.path.join(output_dir, split, cls), exist_ok=True)

# Chia ảnh cho từng lớp
for cls in classes:
    cls_path = os.path.join(dataset_dir, cls)
    images = os.listdir(cls_path)

    # Chia test + train_val
    train_val, test = train_test_split(images, test_size=test_ratio, random_state=42)
    # Chia train + val
    train, val = train_test_split(train_val, test_size=val_ratio / (1 - test_ratio), random_state=42)

    # Copy ảnh vào folder mới
    for img in train:
        shutil.copy(os.path.join(cls_path, img), os.path.join(output_dir, "train", cls, img))
    for img in val:
        shutil.copy(os.path.join(cls_path, img), os.path.join(output_dir, "val", cls, img))
    for img in test:
        shutil.copy(os.path.join(cls_path, img), os.path.join(output_dir, "test", cls, img))

print("Chia dataset xong!")
