from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

# --- Khởi tạo ---
db = SQLAlchemy()
bcrypt = Bcrypt()

# =======================
#  BẢNG NGƯỜI DÙNG
# =======================
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- Mã hóa mật khẩu ---
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    # --- Cần cho Flask-Login ---
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f"<User {self.username}>"


# =======================
#  BẢNG LỊCH SỬ PHÂN TÍCH
# =======================
class AnalysisHistory(db.Model):
    __tablename__ = "analysis_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    image_path = db.Column(db.String(255))
    symptom_text = db.Column(db.Text)
    cnn_result = db.Column(db.String(50))
    confidence = db.Column(db.Float)
    gpt_result = db.Column(db.Text)
    final_conclusion = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- Quan hệ 1-n ---
    user = db.relationship("User", backref=db.backref("analyses", lazy=True))

    def __repr__(self):
        return f"<Analysis {self.id} - {self.cnn_result}>"
