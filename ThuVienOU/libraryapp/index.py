
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash

from libraryapp import app, db, mail
from libraryapp.models import User, UserRole, Book, Category, Author, Publisher, BorrowRequest
from libraryapp.admin import admin  # Import admin để kích hoạt
import hashlib

# Cấu hình Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Bạn cần đăng nhập để truy cập trang này.'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Hàm mã hóa password (đơn giản)
def hash_password(password):
    return generate_password_hash(password)


# Route trang chủ
@app.route('/')
def index():
    # Lấy danh sách sách mới nhất
    books = Book.query.filter_by(active=True).order_by(Book.created_date.desc()).limit(8).all()
    categories = Category.query.all()
    return render_template('index.html', books=books, categories=categories)


@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.user_role != UserRole.ADMIN:
        flash('Bạn không có quyền truy cập trang này.', 'error')
        return redirect(url_for('index'))

    # Lấy dữ liệu thống kê
    total_books = Book.query.count()
    total_users = User.query.count()
    pending_requests = BorrowRequest.query.filter_by(status='pending').count()
    borrowed_books = BorrowRequest.query.filter_by(status='approved').count()

    # Yêu cầu mượn gần đây
    recent_requests = BorrowRequest.query.order_by(BorrowRequest.request_date.desc()).limit(10).all()

    return render_template('admin.html',
                           total_books=total_books,
                           total_users=total_users,
                           pending_requests=pending_requests,
                           borrowed_books=borrowed_books,
                           recent_requests=recent_requests)


@app.route('/admin/update-request-status/<int:request_id>', methods=['POST'])
@login_required
def update_request_status(request_id):
    if current_user.user_role != UserRole.ADMIN:
        return {'success': False, 'message': 'Không có quyền truy cập'}

    borrow_request = BorrowRequest.query.get_or_404(request_id)
    data = request.get_json()

    borrow_request.status = data['status']
    db.session.commit()

    return {'success': True, 'message': 'Cập nhật thành công'}


# Route đăng nhập
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = True if 'remember' in request.form else False

        user = User.query.filter_by(username=username, active=True).first()

        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember)
            flash(f'Chào mừng {user.name}!', 'success')

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            elif user.user_role == UserRole.ADMIN:
                return redirect('/admin/')
            else:
                return redirect(url_for('index'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'error')

    return render_template('login.html')


# Route đăng xuất
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Đã đăng xuất thành công!', 'info')
    return redirect(url_for('index'))

import cloudinary
import cloudinary.uploader


# Route đăng ký
import random
import random, time

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        file = request.files.get('avatar')

        # Check username/email trùng
        if User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại!', 'error')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('Email đã tồn tại!', 'error')
            return render_template('register.html')

        # Upload avatar
        avatar_url = None
        if file and file.filename:
            upload_result = cloudinary.uploader.upload(file)
            avatar_url = upload_result["secure_url"]

        # Sinh OTP
        otp_code = str(random.randint(100000, 999999))
        now = int(time.time())

        # Lưu tạm vào session
        session['pending_user'] = {
            'name': name,
            'username': username,
            'password': hash_password(password),
            'email': email,
            'avatar': avatar_url,
            'otp': otp_code,
            'expires_at': now + 300,   # OTP hết hạn sau 5 phút
            'last_sent': now
        }

        # Gửi mail OTP
        msg = Message("Mã OTP xác thực đăng ký", recipients=[email])
        msg.body = f"Mã OTP của bạn là: {otp_code}. Mã có hiệu lực trong 5 phút."
        mail.send(msg)

        flash('Mã OTP đã được gửi đến email của bạn. Vui lòng kiểm tra hộp thư!', 'info')
        return redirect(url_for('verify_otp'))

    return render_template('register.html')


@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    pending_user = session.get('pending_user')

    if not pending_user:
        flash("Không có thông tin đăng ký. Vui lòng thử lại!", "error")
        return redirect(url_for('register'))

    if request.method == 'POST':
        entered_otp = request.form['otp']
        now = int(time.time())

        if now > pending_user['expires_at']:
            flash("Mã OTP đã hết hạn. Vui lòng yêu cầu gửi lại mã.", "error")
            return redirect(url_for('verify_otp'))

        if entered_otp == pending_user['otp']:
            # Lưu user vào DB
            new_user = User(
                name=pending_user['name'],
                username=pending_user['username'],
                password=pending_user['password'],
                email=pending_user['email'],
                avatar=pending_user['avatar'],
                user_role=UserRole.USER
            )
            db.session.add(new_user)
            db.session.commit()

            session.pop('pending_user')
            flash("Xác thực thành công! Bạn có thể đăng nhập ngay.", "success")
            return redirect(url_for('login'))
        else:
            flash("Mã OTP không đúng. Vui lòng thử lại!", "error")

    return render_template('verify_otp.html')


@app.route('/resend_otp')
def resend_otp():
    pending_user = session.get('pending_user')
    if not pending_user:
        flash("Không có thông tin đăng ký.", "error")
        return redirect(url_for('register'))

    now = int(time.time())
    if now - pending_user['last_sent'] < 30:  # hạn chế spam
        flash("Bạn chỉ có thể yêu cầu gửi lại mã sau 30 giây.", "warning")
        return redirect(url_for('verify_otp'))

    otp_code = str(random.randint(100000, 999999))
    pending_user['otp'] = otp_code
    pending_user['expires_at'] = now + 300  # reset 5 phút
    pending_user['last_sent'] = now
    session['pending_user'] = pending_user

    msg = Message("Mã OTP mới", recipients=[pending_user['email']])
    msg.body = f"Mã OTP mới của bạn là: {otp_code}. Mã có hiệu lực trong 5 phút."
    mail.send(msg)

    flash("Mã OTP mới đã được gửi!", "info")
    return redirect(url_for('verify_otp'))


# Route tìm kiếm sách
from sqlalchemy import or_, func


@app.route('/search')
def search():
    keyword = request.args.get('keyword', '')
    category_id = request.args.get('category_id', '')

    # Tìm kiếm theo tên sách hoặc tên tác giả
    query = Book.query.filter(Book.active == True)

    if keyword:
        # join với bảng Author để có thể lọc theo tên tác giả
        query = query.join(Book.author).filter(
            or_(
                Book.name.ilike(f'%{keyword}%'),
                Author.first_name.ilike(f'%{keyword}%'),
                Author.last_name.ilike(f'%{keyword}%'),
                func.concat(Author.first_name, ' ', Author.last_name).ilike(f'%{keyword}%')

            )
        )

    if category_id:
        query = query.filter(Book.category_id == category_id)

    books = query.all()
    categories = Category.query.all()

    return render_template('index.html', books=books, categories=categories,
                           keyword=keyword, selected_category=category_id)


# Route chi tiết sách
@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book_detail.html', book=book)


# Route mượn sách
@app.route('/borrow/<int:book_id>', methods=['GET', 'POST'])
@login_required
def borrow_book(book_id):
    book = Book.query.get_or_404(book_id)

    if request.method == 'GET':
        flash('Vui lòng sử dụng form để mượn sách!', 'warning')
        return redirect(url_for('book_detail', book_id=book_id))

    # Logic POST
    if book.quantity <= 0:
        flash('Sách đã hết!', 'error')
        return redirect(url_for('book_detail', book_id=book_id))

    existing_request = BorrowRequest.query.filter_by(
        user_id=current_user.id,
        book_id=book_id,
        status='pending'
    ).first()

    if existing_request:
        flash('Bạn đã gửi yêu cầu mượn sách này rồi!', 'warning')
        return redirect(url_for('book_detail', book_id=book_id))

    borrow_request = BorrowRequest(
        user_id=current_user.id,
        book_id=book_id,
        status='pending'
    )

    db.session.add(borrow_request)
    db.session.commit()

    flash('Yêu cầu mượn sách đã được gửi!', 'success')
    return redirect(url_for('book_detail', book_id=book_id))

# Route xem lịch sử mượn sách
@app.route('/my-borrows')
@login_required
def my_borrows():
    borrows = BorrowRequest.query.filter_by(user_id=current_user.id) \
        .order_by(BorrowRequest.request_date.desc()).all()
    return render_template('my_borrows.html', borrows=borrows)


from flask import jsonify

@app.route('/cancel-borrow/<int:request_id>', methods=['DELETE'])
@login_required
def cancel_borrow(request_id):
    # Tìm yêu cầu mượn
    borrow_request = BorrowRequest.query.get_or_404(request_id)

    # Kiểm tra quyền sở hữu
    if borrow_request.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Bạn không có quyền hủy yêu cầu này!'}), 403

    # Kiểm tra trạng thái
    if borrow_request.status == 'approved':
        return jsonify({'success': False, 'message': 'Không thể hủy yêu cầu đã được duyệt!'}), 400

    # Xóa yêu cầu
    db.session.delete(borrow_request)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Yêu cầu mượn sách đã được hủy!'})

if __name__ == '__main__':
    app.run(debug=True)
