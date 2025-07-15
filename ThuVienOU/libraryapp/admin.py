from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from libraryapp import app, db
from libraryapp.models import User, Author, Publisher, Category, Book, BorrowRequest, UserRole
from wtforms import IntegerField
from flask_login import current_user
from flask import redirect, url_for, request, flash


class BaseModelView(ModelView):
    can_view_details = True
    can_export = True
    page_size = 20
    column_display_pk = True

    def is_accessible(self):
        # Kiểm tra quyền truy cập
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        # Chuyển hướng nếu không có quyền
        flash('Bạn không có quyền truy cập trang này.', 'error')
        return redirect(url_for('login', next=request.url))


class UserModelView(BaseModelView):
    column_list = ['id', 'name', 'username', 'email', 'joined_date', 'user_role', 'active']
    column_filters = ['user_role', 'active', 'joined_date']
    column_searchable_list = ['name', 'username', 'email']
    form_excluded_columns = ['borrowrequest']
    column_labels = {
        'name': 'Họ tên',
        'username': 'Tên đăng nhập',
        'joined_date': 'Ngày tham gia',
        'user_role': 'Vai trò',
        'active': 'Trạng thái',
        'email': 'Email'
    }


class AuthorModelView(BaseModelView):
    column_list = ['id', 'first_name', 'last_name']
    column_searchable_list = ['first_name', 'last_name']
    form_excluded_columns = ['books']
    column_labels = {
        'first_name': 'Tên',
        'last_name': 'Họ'
    }


class PublisherModelView(BaseModelView):
    column_list = ['id', 'name']
    form_excluded_columns = ['books']
    column_searchable_list = ['name']
    column_labels = {
        'name': 'Tên nhà xuất bản'
    }


class CategoryModelView(BaseModelView):
    column_list = ['id', 'name']
    form_excluded_columns = ['books']
    column_searchable_list = ['name']
    column_labels = {
        'name': 'Tên danh mục'
    }


class BookModelView(BaseModelView):
    column_list = ['id', 'name', 'price', 'quantity', 'category', 'author', 'publisher', 'active', 'created_date']
    column_filters = ['price', 'active', 'created_date', 'category']
    column_searchable_list = ['name', 'description']
    form_excluded_columns = ['borrowrequest']
    form_columns = ['name', 'description', 'price', 'quantity', 'category', 'author', 'publisher', 'image', 'active']
    column_labels = {
        'name': 'Tên sách',
        'description': 'Mô tả',
        'price': 'Giá',
        'quantity': 'Số lượng',
        'category': 'Danh mục',
        'author': 'Tác giả',
        'publisher': 'Nhà xuất bản',
        'active': 'Trạng thái',
        'created_date': 'Ngày tạo',
        'image': 'Hình ảnh'
    }

    # Định dạng giá tiền
    def _format_price(view, context, model, name):
        return f"{model.price:,.0f} VND" if model.price else "0 VND"

    column_formatters = {
        'price': _format_price
    }

    form_overrides = {
        'quantity': IntegerField
    }


class BorrowRequestModelView(BaseModelView):
    column_list = ['id', 'user', 'book', 'request_date', 'status', 'return_date']
    column_filters = ['status', 'request_date']
    form_columns = ['user', 'book', 'status', 'return_date']
    column_labels = {
        'user': 'Người mượn',
        'book': 'Sách',
        'request_date': 'Ngày yêu cầu',
        'status': 'Trạng thái',
        'return_date': 'Ngày trả'
    }


# Tạo AdminIndexView tùy chỉnh với kiểm tra quyền
class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        # Kiểm tra user đã đăng nhập và có quyền admin
        if not current_user.is_authenticated:
            flash('Bạn cần đăng nhập để truy cập trang admin.', 'error')
            return redirect(url_for('login', next=request.url))

        if current_user.user_role != UserRole.ADMIN:
            flash('Bạn không có quyền truy cập trang admin.', 'error')
            return redirect(url_for('index'))

        return super(MyAdminIndexView, self).index()


# Khởi tạo Admin với IndexView tùy chỉnh
admin = Admin(app=app, name='Quản lý Thư viện', template_mode='bootstrap4',
              index_view=MyAdminIndexView())

# Đăng ký các model vào Flask-Admin
admin.add_view(UserModelView(User, db.session, name='Người dùng'))
admin.add_view(AuthorModelView(Author, db.session, name='Tác giả'))
admin.add_view(PublisherModelView(Publisher, db.session, name='Nhà xuất bản'))
admin.add_view(CategoryModelView(Category, db.session, name='Danh mục'))
admin.add_view(BookModelView(Book, db.session, name='Sách'))
admin.add_view(BorrowRequestModelView(BorrowRequest, db.session, name='Yêu cầu mượn sách'))