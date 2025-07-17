import json
import os
from datetime import datetime
from libraryapp import create_app
from libraryapp.extensions import db
from libraryapp.models import User, UserRole, Author, Publisher, Category, Book


def load_json_file(filename):
    """Load dữ liệu từ file JSON"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Không tìm thấy file: {filename}")
        return []
    except json.JSONDecodeError:
        print(f"❌ Lỗi đọc file JSON: {filename}")
        return []


def import_authors():
    """Import dữ liệu tác giả"""
    authors_data = load_json_file('data/auth.json')

    for author_data in authors_data:
        # Kiểm tra xem tác giả đã tồn tại chưa
        existing_author = Author.query.filter_by(id=author_data['id']).first()
        if existing_author:
            print(f"⚠️  Tác giả {author_data['first_name']} {author_data['last_name']} đã tồn tại")
            continue

        author = Author(
            id=author_data['id'],
            first_name=author_data['first_name'],
            last_name=author_data['last_name']
        )
        db.session.add(author)

    db.session.commit()
    print(f"✅ Đã import {len(authors_data)} tác giả")


def import_categories():
    """Import dữ liệu danh mục"""
    categories_data = load_json_file('data/cate.json')

    for category_data in categories_data:
        # Kiểm tra xem danh mục đã tồn tại chưa
        existing_category = Category.query.filter_by(id=category_data['id']).first()
        if existing_category:
            print(f"⚠️  Danh mục {category_data['name']} đã tồn tại")
            continue

        category = Category(
            id=category_data['id'],
            name=category_data['name']
        )
        db.session.add(category)

    db.session.commit()
    print(f"✅ Đã import {len(categories_data)} danh mục")


def import_publishers():
    """Import dữ liệu nhà xuất bản"""
    publishers_data = load_json_file('data/pub.json')

    for publisher_data in publishers_data:
        # Kiểm tra xem nhà xuất bản đã tồn tại chưa
        existing_publisher = Publisher.query.filter_by(id=publisher_data['id']).first()
        if existing_publisher:
            print(f"⚠️  Nhà xuất bản {publisher_data['name']} đã tồn tại")
            continue

        publisher = Publisher(
            id=publisher_data['id'],
            name=publisher_data['name']
        )
        db.session.add(publisher)

    db.session.commit()
    print(f"✅ Đã import {len(publishers_data)} nhà xuất bản")


def import_books():
    """Import dữ liệu sách"""
    books_data = load_json_file('data/books.json')

    for book_data in books_data:
        # Kiểm tra xem sách đã tồn tại chưa
        existing_book = Book.query.filter_by(id=book_data['id']).first()
        if existing_book:
            print(f"⚠️  Sách {book_data['name']} đã tồn tại")
            continue

        # Chuyển đổi created_date từ string sang datetime
        created_date = datetime.strptime(book_data['created_date'], '%Y-%m-%d %H:%M:%S')

        book = Book(
            id=book_data['id'],
            name=book_data['name'],
            description=book_data['description'],
            price=book_data['price'],
            image=book_data['image'],
            active=bool(book_data['active']),
            category_id=book_data['category_id'],
            created_date=created_date,
            author_id=book_data['author_id'],
            publisher_id=book_data['publisher_id'],
            quantity=book_data['quantity']
        )
        db.session.add(book)

    db.session.commit()
    print(f"✅ Đã import {len(books_data)} sách")


def check_data_integrity():
    """Kiểm tra tính toàn vẹn dữ liệu"""
    print("\n📊 Kiểm tra dữ liệu:")
    print(f"- Tác giả: {Author.query.count()}")
    print(f"- Danh mục: {Category.query.count()}")
    print(f"- Nhà xuất bản: {Publisher.query.count()}")
    print(f"- Sách: {Book.query.count()}")
    print(f"- Người dùng: {User.query.count()}")

    # Kiểm tra foreign key
    orphaned_books = Book.query.filter(
        ~Book.author_id.in_(db.session.query(Author.id)) |
        ~Book.category_id.in_(db.session.query(Category.id)) |
        ~Book.publisher_id.in_(db.session.query(Publisher.id))
    ).count()

    if orphaned_books > 0:
        print(f"⚠️  Có {orphaned_books} sách có vấn đề về khóa ngoại")
    else:
        print("✅ Tất cả dữ liệu đều hợp lệ")


def main():
    """Hàm chính để import tất cả dữ liệu"""
    app = create_app()

    with app.app_context():
        print("🚀 Bắt đầu import dữ liệu...")

        # Kiểm tra xem thư mục data có tồn tại không
        if not os.path.exists('data'):
            print("❌ Thư mục 'data' không tồn tại. Vui lòng tạo thư mục và đặt các file JSON vào đó.")
            return

        # Import theo thứ tự (quan trọng vì có foreign key)
        try:
            # 1. Import authors trước
            print("\n1️⃣ Import tác giả...")
            import_authors()

            # 2. Import categories
            print("\n2️⃣ Import danh mục...")
            import_categories()

            # 3. Import publishers
            print("\n3️⃣ Import nhà xuất bản...")
            import_publishers()

            # 4. Import books cuối cùng
            print("\n4️⃣ Import sách...")
            import_books()

            # 5. Kiểm tra dữ liệu
            check_data_integrity()

            print("\n🎉 Hoàn thành import dữ liệu!")

        except Exception as e:
            print(f"❌ Lỗi khi import dữ liệu: {e}")
            db.session.rollback()


if __name__ == '__main__':
    main()