from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from libraryapp import app, db
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
    return hashlib.md5(password.encode()).hexdigest()


# Route trang chủ
@app.route('/')
def index():
    # Lấy danh sách sách mới nhất
    books = Book.query.filter_by(active=True).order_by(Book.created_date.desc()).limit(8).all()
    categories = Category.query.all()
    return render_template('index.html', books=books, categories=categories)


# Route đăng nhập
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Mã hóa password để so sánh
        hashed_password = hash_password(password)

        # Tìm user trong database
        user = User.query.filter_by(username=username, password=hashed_password, active=True).first()

        if user:
            login_user(user)
            flash(f'Chào mừng {user.name}!', 'success')

            # Chuyển hướng về trang được yêu cầu hoặc trang chủ
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
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


# Route đăng ký
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Kiểm tra username đã tồn tại
        if User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại!', 'error')
            return render_template('register.html')

        # Kiểm tra email đã tồn tại
        if User.query.filter_by(email=email).first():
            flash('Email đã tồn tại!', 'error')
            return render_template('register.html')

        # Tạo user mới
        hashed_password = hash_password(password)
        new_user = User(
            name=name,
            username=username,
            password=hashed_password,
            email=email,
            user_role=UserRole.USER
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Đăng ký thành công! Bạn có thể đăng nhập ngay bây giờ.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


# Route tìm kiếm sách
@app.route('/search')
def search():
    keyword = request.args.get('keyword', '')
    category_id = request.args.get('category_id', '')

    query = Book.query.filter_by(active=True)

    if keyword:
        query = query.filter(Book.name.contains(keyword))

    if category_id:
        query = query.filter_by(category_id=category_id)

    books = query.all()
    categories = Category.query.all()

    return render_template('search.html', books=books, categories=categories,
                           keyword=keyword, selected_category=category_id)


# Route chi tiết sách
@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book_detail.html', book=book)


# Route mượn sách
@app.route('/borrow/<int:book_id>', methods=['POST'])
@login_required
def borrow_book(book_id):
    book = Book.query.get_or_404(book_id)

    # Kiểm tra sách còn không
    if book.quantity <= 0:
        flash('Sách đã hết!', 'error')
        return redirect(url_for('book_detail', book_id=book_id))

    # Kiểm tra user đã mượn sách này chưa
    existing_request = BorrowRequest.query.filter_by(
        user_id=current_user.id,
        book_id=book_id,
        status='pending'
    ).first()

    if existing_request:
        flash('Bạn đã gửi yêu cầu mượn sách này rồi!', 'warning')
        return redirect(url_for('book_detail', book_id=book_id))

    # Tạo yêu cầu mượn sách
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



if __name__ == '__main__':
    app.run(debug=True)