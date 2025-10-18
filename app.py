import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import (
    LoginManager, login_user, logout_user, login_required,
    current_user
)
from models import db, bcrypt, User, AnalysisHistory
from fusion import predict_image, analyze_symptoms, combine_results
from chat import chat_with_ai

# ==========================================================
# ⚙️ CẤU HÌNH FLASK CƠ BẢN
# ==========================================================
app = Flask(__name__)
app.secret_key = "super_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["UPLOAD_FOLDER"] = "static/uploads"

# --- Khởi tạo các extension ---
db.init_app(app)
bcrypt.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message = "⚠️ Vui lòng đăng nhập để tiếp tục."
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    """Hàm lấy thông tin người dùng theo ID"""
    return User.query.get(int(user_id))


# --- Khởi tạo cơ sở dữ liệu lần đầu ---
with app.app_context():
    db.create_all()
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


# ==========================================================
# 🔐 AUTHENTICATION
# ==========================================================
@app.route("/register", methods=["GET", "POST"])
def register():
    """Trang đăng ký tài khoản"""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("⚠️ Vui lòng nhập đầy đủ thông tin!", "warning")
            return redirect(url_for("register"))

        # Kiểm tra trùng lặp email hoặc username
        if User.query.filter((User.email == email) | (User.username == username)).first():
            flash("❌ Tên đăng nhập hoặc email đã được sử dụng!", "danger")
            return redirect(url_for("register"))

        # Tạo người dùng mới
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("✅ Đăng ký thành công! Vui lòng đăng nhập để sử dụng hệ thống.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Trang đăng nhập bằng email hoặc tên đăng nhập"""
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")

        if not identifier or not password:
            flash("⚠️ Vui lòng nhập đầy đủ thông tin đăng nhập!", "warning")
            return redirect(url_for("login"))

        # Tìm người dùng theo email hoặc username
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f"🎉 Xin chào {user.username}! Bạn đã đăng nhập thành công.", "success")
            return redirect(url_for("index"))
        else:
            flash("❌ Tên đăng nhập hoặc mật khẩu không chính xác!", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """Đăng xuất người dùng"""
    username = current_user.username
    logout_user()
    flash(f"👋 Tạm biệt {username}, hẹn gặp lại!", "info")
    return redirect(url_for("login"))


# ==========================================================
# 🩺 TRANG CHÍNH - CHẨN ĐOÁN ẢNH DA LIỄU
# ==========================================================
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Trang chính: upload ảnh và mô tả triệu chứng"""
    if request.method == "POST":
        img = request.files.get("image")
        symptom = request.form.get("symptom", "").strip()

        if not img or not symptom:
            flash("⚠️ Vui lòng chọn ảnh và nhập mô tả triệu chứng!", "warning")
            return redirect(url_for("index"))

        # Lưu ảnh upload
        img_path = os.path.join(app.config["UPLOAD_FOLDER"], img.filename)
        img.save(img_path)

        # Gọi mô hình AI
        disease, conf = predict_image(img_path)
        gpt_result = analyze_symptoms(symptom)
        final_conclusion = combine_results(disease, gpt_result)

        # Lưu vào cơ sở dữ liệu
        record = AnalysisHistory(
            user_id=current_user.id,
            image_path=img_path,
            symptom_text=symptom,
            cnn_result=disease,
            confidence=conf,
            gpt_result=gpt_result,
            final_conclusion=final_conclusion
        )
        db.session.add(record)
        db.session.commit()

        flash("✅ Phân tích hoàn tất!", "success")

        return render_template(
            "index.html",
            image=img_path,
            cnn=disease,
            conf=round(conf, 2),
            gpt=gpt_result,
            final=final_conclusion
        )

    return render_template("index.html")


@app.route("/history")
@login_required
def history():
    """Lịch sử các lần phân tích"""
    records = (
        AnalysisHistory.query.filter_by(user_id=current_user.id)
        .order_by(AnalysisHistory.created_at.desc())
        .all()
    )
    return render_template("history.html", records=records)


# ==========================================================
# 💬 CHATBOT (TRANG RIÊNG + API)
# ==========================================================
@app.route("/chatbot")
@login_required
def chatbot():
    """Trang giao diện chatbot riêng biệt"""
    return render_template("chatbot.html")


@app.route("/chat", methods=["POST"])
@login_required
def chat():
    """API xử lý tin nhắn chat"""
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"response": "⚠️ Vui lòng nhập câu hỏi của bạn!"})

    ai_reply = chat_with_ai(user_message)
    return jsonify({"response": ai_reply})


# ==========================================================
# 🚀 KHỞI CHẠY ỨNG DỤNG
# ==========================================================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
