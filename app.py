import os
import math
import re
from functools import wraps
from datetime import datetime, timedelta, timezone

from flask import Flask, request, jsonify, session, render_template, redirect, url_for
from models import db, User, Book, Transaction, Fine

app = Flask(__name__)
# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')

# Initialize db with app
db.init_app(app)

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({"error": "Authentication required"}), 401
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                if request.path.startswith('/api/'):
                    return jsonify({"error": "Authentication required"}), 401
                return redirect(url_for('login_page'))
            if session.get('role') != role:
                if request.path.startswith('/api/'):
                    return jsonify({"error": "Unauthorized access"}), 403
                return redirect(url_for('login_page'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def seed_database():
    print("Seeding database...")
    
    # Create Admin
    if not User.query.filter_by(email='admin@library.com').first():
        admin = User(name='Admin', email='admin@library.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
    
    # Create Student
    if not User.query.filter_by(email='student@library.com').first():
        student = User(name='Student', email='student@library.com', role='student')
        student.set_password('student123')
        db.session.add(student)
    
    # Create Books
    books_data = [
        {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "category": "Fiction", "isbn": "9780743273565", "copies": 3},
        {"title": "To Kill a Mockingbird", "author": "Harper Lee", "category": "Fiction", "isbn": "9780060935467", "copies": 5},
        {"title": "1984", "author": "George Orwell", "category": "Science Fiction", "isbn": "9780451524935", "copies": 4},
        {"title": "Pride and Prejudice", "author": "Jane Austen", "category": "Romance", "isbn": "9780141439518", "copies": 2},
        {"title": "The Catcher in the Rye", "author": "J.D. Salinger", "category": "Fiction", "isbn": "9780316769174", "copies": 3},
        {"title": "A Brief History of Time", "author": "Stephen Hawking", "category": "Science", "isbn": "9780553380163", "copies": 2},
        {"title": "Sapiens: A Brief History of Humankind", "author": "Yuval Noah Harari", "category": "History", "isbn": "9780062316097", "copies": 6},
        {"title": "The Hobbit", "author": "J.R.R. Tolkien", "category": "Fantasy", "isbn": "9780547928227", "copies": 4},
        {"title": "Harry Potter and the Sorcerer's Stone", "author": "J.K. Rowling", "category": "Fantasy", "isbn": "9780590353427", "copies": 7},
        {"title": "Harry Potter and the Chamber of Secrets", "author": "J.K. Rowling", "category": "Fantasy", "isbn": "9780439064873", "copies": 6},
        {"title": "Harry Potter and the Prisoner of Azkaban", "author": "J.K. Rowling", "category": "Fantasy", "isbn": "9780439136365", "copies": 6},
        {"title": "Harry Potter and the Goblet of Fire", "author": "J.K. Rowling", "category": "Fantasy", "isbn": "9780439139601", "copies": 5},
        {"title": "Harry Potter and the Order of the Phoenix", "author": "J.K. Rowling", "category": "Fantasy", "isbn": "9780439358071", "copies": 5},
        {"title": "Harry Potter and the Half-Blood Prince", "author": "J.K. Rowling", "category": "Fantasy", "isbn": "9780439785969", "copies": 5},
        {"title": "Harry Potter and the Deathly Hallows", "author": "J.K. Rowling", "category": "Fantasy", "isbn": "9780545010221", "copies": 5},
        {"title": "The Alchemist", "author": "Paulo Coelho", "category": "Fiction", "isbn": "9780061122415", "copies": 8},
        {"title": "The Lord of the Rings", "author": "J.R.R. Tolkien", "category": "Fantasy", "isbn": "9780544003415", "copies": 4},
        {"title": "The Da Vinci Code", "author": "Dan Brown", "category": "Thriller", "isbn": "9780307474278", "copies": 6},
        {"title": "Twilight", "author": "Stephenie Meyer", "category": "Fantasy", "isbn": "9780316015844", "copies": 3},
        {"title": "The Hunger Games", "author": "Suzanne Collins", "category": "Science Fiction", "isbn": "9780439023481", "copies": 5},
        {"title": "Catch-22", "author": "Joseph Heller", "category": "Fiction", "isbn": "9781451626650", "copies": 2},
        {"title": "The Kite Runner", "author": "Khaled Hosseini", "category": "Fiction", "isbn": "9781594480003", "copies": 4},
        {"title": "Life of Pi", "author": "Yann Martel", "category": "Fiction", "isbn": "9780156027328", "copies": 3},
        {"title": "Animal Farm", "author": "George Orwell", "category": "Fiction", "isbn": "9780451526342", "copies": 7},
        {"title": "The Diary of a Young Girl", "author": "Anne Frank", "category": "Biography", "isbn": "9780553296983", "copies": 4},
        {"title": "Brave New World", "author": "Aldous Huxley", "category": "Science Fiction", "isbn": "9780060850524", "copies": 4},
        {"title": "Fahrenheit 451", "author": "Ray Bradbury", "category": "Science Fiction", "isbn": "9781451673319", "copies": 3},
        {"title": "The Little Prince", "author": "Antoine de Saint-Exupéry", "category": "Fiction", "isbn": "9780156012195", "copies": 6}
    ]
    
    for b_data in books_data:
        if not Book.query.filter_by(isbn=b_data["isbn"]).first():
            book = Book(
                title=b_data["title"],
                author=b_data["author"],
                category=b_data["category"],
                isbn=b_data["isbn"],
                total_copies=b_data["copies"],
                available_copies=b_data["copies"]
            )
            db.session.add(book)
        
    db.session.commit()
    print("Database seeded successfully!")

@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('student_dashboard'))
    return render_template('landing.html')

@app.route('/login')
def login_page():
    session.clear()
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/student')
@login_required
def student_dashboard():
    return render_template('student_dashboard.html')

@app.route('/admin')
@login_required
@role_required('admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON payload"}), 400
        
    name = str(data.get('name', '')).strip()
    email = str(data.get('email', '')).strip()
    password = str(data.get('password', '')).strip()
    
    if not name or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400
        
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return jsonify({"error": "Invalid email format"}), 400
        
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400
        
    # Only student signup is allowed via this endpoint
    new_user = User(
        name=name,
        email=email,
        role='student'
    )
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "Registration successful", "user_id": new_user.id}), 201

@app.route('/api/register-admin', methods=['POST'])
@login_required
@role_required('admin')
def register_admin():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON payload"}), 400
        
    name = str(data.get('name', '')).strip()
    email = str(data.get('email', '')).strip()
    password = str(data.get('password', '')).strip()
    
    if not name or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400
        
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return jsonify({"error": "Invalid email format"}), 400
        
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400
        
    new_user = User(
        name=name,
        email=email,
        role='admin'
    )
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "Admin registration successful", "user_id": new_user.id}), 201

@app.route('/api/users', methods=['GET'])
@login_required
@role_required('admin')
def get_users():
    users = User.query.all()
    result = []
    for user in users:
        result.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        })
    return jsonify(result), 200

@app.route('/api/users/<int:id>', methods=['DELETE'])
@login_required
@role_required('admin')
def remove_user(id):
    if id == session.get('user_id'):
        return jsonify({"error": "You cannot remove yourself"}), 400
    user = User.query.get_or_404(id)
    user.name = "Deleted User"
    user.email = f"deleted_{id}@library.com"
    user.password_hash = "DELETED"
    db.session.commit()
    return jsonify({"message": "User details removed successfully"}), 200

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON payload"}), 400
        
    email = str(data.get('email', '')).strip()
    password = str(data.get('password', '')).strip()
    
    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400
        
    user = User.query.filter_by(email=email).first()
    
    if user and user.check_password(password):
        session['user_id'] = user.id
        session['role'] = user.role
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            }
        }), 200
        
    return jsonify({"error": "Invalid email or password"}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logout successful"}), 200

@app.route('/api/change-password', methods=['POST'])
@login_required
def change_password():
    data = request.get_json(silent=True)
    if not data or not data.get('old_password') or not data.get('new_password'):
        return jsonify({"error": "Missing old or new password"}), 400
        
    user = User.query.get(session['user_id'])
    if not user.check_password(data['old_password']):
        return jsonify({"error": "Incorrect old password"}), 400
        
    user.set_password(data['new_password'])
    db.session.commit()
    return jsonify({"message": "Password changed successfully"}), 200

@app.route('/api/books', methods=['GET'])
def get_books():
    search = request.args.get('search', '')
    query = Book.query
    if search:
        search_term = f"%{search}%"
        query = query.filter(db.or_(
            Book.title.ilike(search_term),
            Book.author.ilike(search_term),
            Book.category.ilike(search_term)
        ))
    books = query.all()
    return jsonify([{
        "id": b.id, "title": b.title, "author": b.author,
        "category": b.category, "isbn": b.isbn,
        "total_copies": b.total_copies, "available_copies": b.available_copies
    } for b in books]), 200

@app.route('/api/books', methods=['POST'])
@login_required
@role_required('admin')
def add_book():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON payload"}), 400
        
    title = str(data.get('title', '')).strip()
    author = str(data.get('author', '')).strip()
    category = str(data.get('category', '')).strip()
    isbn = str(data.get('isbn', '')).strip()
    
    if not title or not author or not category or not isbn:
        return jsonify({"error": "Missing required fields"}), 400
        
    total_copies = data.get('total_copies', 1)
    if not isinstance(total_copies, int) or total_copies < 0:
        return jsonify({"error": "Total copies must be a non-negative integer"}), 400
        
    new_book = Book(
        title=title,
        author=author,
        category=category,
        isbn=isbn,
        total_copies=total_copies,
        available_copies=total_copies
    )
    db.session.add(new_book)
    db.session.commit()
    return jsonify({"message": "Book added successfully", "book_id": new_book.id}), 201

@app.route('/api/books/<int:id>', methods=['PUT'])
@login_required
@role_required('admin')
def update_book(id):
    book = Book.query.get_or_404(id)
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    if 'total_copies' in data:
        total_copies = data['total_copies']
        if not isinstance(total_copies, int) or total_copies < 0:
            return jsonify({"error": "Total copies must be a non-negative integer"}), 400
        diff = total_copies - book.total_copies
        book.total_copies = total_copies
        book.available_copies += diff
        if book.available_copies < 0:
            return jsonify({"error": "Cannot reduce copies below currently issued"}), 400
            
    if 'title' in data:
        title = str(data['title']).strip()
        if not title: return jsonify({"error": "Title cannot be empty"}), 400
        book.title = title
    if 'author' in data:
        author = str(data['author']).strip()
        if not author: return jsonify({"error": "Author cannot be empty"}), 400
        book.author = author
    if 'category' in data:
        category = str(data['category']).strip()
        if not category: return jsonify({"error": "Category cannot be empty"}), 400
        book.category = category
    if 'isbn' in data:
        isbn = str(data['isbn']).strip()
        if not isbn: return jsonify({"error": "ISBN cannot be empty"}), 400
        book.isbn = isbn
    
    db.session.commit()
    return jsonify({"message": "Book updated successfully"}), 200

@app.route('/api/books/<int:id>', methods=['DELETE'])
@login_required
@role_required('admin')
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted successfully"}), 200

@app.route('/api/issue', methods=['POST'])
@login_required
def issue_book():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON payload"}), 400
        
    book_id = data.get('book_id')
    if not isinstance(book_id, int):
        return jsonify({"error": "Valid book_id is required"}), 400
        
    user_id = session['user_id']
    
    active_issue = Transaction.query.filter_by(user_id=user_id, book_id=book_id, status='issued').first()
    if active_issue:
        return jsonify({"error": "You have already issued this book"}), 400
        
    # Atomically check and decrement available copies to prevent race conditions
    updated_rows = db.session.query(Book).filter(
        Book.id == book_id,
        Book.available_copies > 0
    ).update({Book.available_copies: Book.available_copies - 1}, synchronize_session=False)
    
    if updated_rows == 0:
        db.session.rollback()
        book = Book.query.get(book_id)
        if not book:
            return jsonify({"error": "Book not found"}), 404
        return jsonify({"error": "No copies available"}), 400
        
    issue_date = datetime.now(timezone.utc)
    due_date = issue_date + timedelta(days=14)
    
    transaction = Transaction(
        user_id=user_id,
        book_id=book_id,
        issue_date=issue_date,
        due_date=due_date,
        status='issued'
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({"message": "Book issued successfully", "transaction_id": transaction.id}), 200

@app.route('/api/return', methods=['POST'])
@login_required
def return_book():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON payload"}), 400
        
    transaction_id = data.get('transaction_id')
    if not isinstance(transaction_id, int):
        return jsonify({"error": "Valid transaction_id is required"}), 400
    
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return jsonify({"error": "Transaction not found"}), 404
        
    if transaction.status == 'returned':
        return jsonify({"error": "Book already returned"}), 400
        
    if session['role'] != 'admin' and transaction.user_id != session['user_id']:
        return jsonify({"error": "Unauthorized"}), 403
        
    return_date = datetime.now(timezone.utc)
    transaction.return_date = return_date
    transaction.status = 'returned'
    
    book = Book.query.get(transaction.book_id)
    if book:
        book.available_copies += 1
        
    due = transaction.due_date.replace(tzinfo=timezone.utc) if transaction.due_date.tzinfo is None else transaction.due_date
    if return_date > due:
        diff = return_date - due
        days_overdue = math.ceil(diff.total_seconds() / 86400)
        if days_overdue > 0:
            fine_amount = days_overdue * 5.0
            fine = Fine(transaction_id=transaction.id, amount=fine_amount, paid_status=False)
            db.session.add(fine)
            db.session.commit()
            return jsonify({"message": "Book returned successfully with fine", "fine_amount": fine_amount}), 200
            
    db.session.commit()
    return jsonify({"message": "Book returned successfully"}), 200

@app.route('/api/transactions', methods=['GET'])
@login_required
def get_transactions():
    if session['role'] == 'admin':
        transactions = Transaction.query.all()
    else:
        transactions = Transaction.query.filter_by(user_id=session['user_id']).all()
        
    result = []
    for t in transactions:
        result.append({
            "id": t.id,
            "book_title": t.book.title if t.book else "Unknown",
            "user_name": t.user.name if t.user else "Unknown",
            "issue_date": t.issue_date.strftime("%Y-%m-%d %H:%M:%S") if t.issue_date else None,
            "due_date": t.due_date.strftime("%Y-%m-%d %H:%M:%S") if t.due_date else None,
            "return_date": t.return_date.strftime("%Y-%m-%d %H:%M:%S") if t.return_date else None,
            "status": t.status
        })
    return jsonify(result), 200

@app.route('/api/fines', methods=['GET'])
@login_required
def get_fines():
    if session['role'] == 'admin':
        fines = Fine.query.all()
    else:
        fines = Fine.query.join(Transaction).filter(Transaction.user_id == session['user_id']).all()
        
    result = []
    for f in fines:
        result.append({
            "id": f.id,
            "transaction_id": f.transaction_id,
            "book_title": f.transaction.book.title if f.transaction and f.transaction.book else "Unknown",
            "user_name": f.transaction.user.name if f.transaction and f.transaction.user else "Unknown",
            "amount": f.amount,
            "paid_status": f.paid_status
        })
    return jsonify(result), 200

@app.route('/api/fines/<int:id>/pay', methods=['POST'])
@login_required
@role_required('admin')
def mark_fine_paid(id):
    fine = Fine.query.get_or_404(id)
    fine.paid_status = True
    db.session.commit()
    return jsonify({"message": "Fine marked as paid successfully"}), 200

@app.route('/api/fines/<int:id>/unpay', methods=['POST'])
@login_required
@role_required('admin')
def mark_fine_unpaid(id):
    fine = Fine.query.get_or_404(id)
    fine.paid_status = False
    db.session.commit()
    return jsonify({"message": "Fine marked as unpaid successfully"}), 200

if __name__ == '__main__':
    with app.app_context():
        # Create tables on first run
        db.create_all()
        # Seed database
        seed_database()
    
    # Run the Flask app
    app.run(host='0.0.0.0', debug=True, port=5000)
