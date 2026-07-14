# Digital Library Manager 📚

A modern, responsive, and fully-featured Digital Library Management System built with Python (Flask) and SQLite. This application allows students to browse, borrow, and return books while empowering administrators to manage the library's catalog, track transactions, calculate fines, and manage user accounts.

---

## 🌟 Features

### 👨‍🎓 Student Dashboard
- **Browse Catalog**: Search and view all available books in the library by title, author, or category.
- **Issue Books**: Seamlessly borrow available books with an automatic 14-day due date calculation.
- **My Issued Books**: Track currently borrowed books, their due dates, and return them with a single click.
- **Fines Management**: Automatically calculated fines for overdue books (₹5.0 per day).
- **Account Management**: Securely change account passwords.

### 🛡️ Admin Dashboard
- **Book Management**: Add new books to the system, update stock, or remove damaged/lost books.
- **Transaction History**: View a complete log of all books issued and returned across all users.
- **Fines Oversight**: View all pending and paid fines. Admins can manually mark fines as "Paid" or revert them to "Unpaid".
- **User Management**: 
  - Register new Admin accounts securely.
  - View a directory of all registered users (Admins & Students).
  - Soft-delete users to revoke their access without corrupting past transaction history.

---

## 🛠️ Technology Stack

- **Backend**: Python 3, Flask, Flask-SQLAlchemy, Werkzeug
- **Database**: SQLite (Local, lightweight database)
- **Frontend**: HTML5, Vanilla CSS, Vanilla JavaScript
- **UI/UX**: GSAP (GreenSock) for smooth micro-animations, AOS (Animate On Scroll) for scroll transitions.

---

## 🚀 Quick Start Guide

Follow these steps to get the project running locally on your machine.

### 1. Prerequisites
Make sure you have [Python 3.x](https://www.python.org/downloads/) installed on your system.

### 2. Installation
Clone the repository and open your terminal in the project directory:

```bash
# Clone the repository
git clone https://github.com/your-username/digital-library-manager.git
cd digital-library-manager

# Create a virtual environment (optional but recommended)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install the required dependencies
pip install -r requirements.txt
```

### 3. Running the Application
Start the Flask server:
```bash
python app.py
```

The application will now be running on `http://127.0.0.1:5000` (or `http://localhost:5000`).

---

## 🗄️ Database & Default Credentials

There is no need to run complex database migrations. When you start `app.py` for the first time, the application automatically builds the SQLite database (`instance/database.db`) and seeds it with **28 sample books** (including classics, non-fiction, and the entire Harry Potter series) so you can start testing immediately!

It also automatically generates the following default accounts for you:

**Admin Account:**
- **Email:** `admin@library.com`
- **Password:** `admin123`

**Student Account:**
- **Email:** `student@library.com`
- **Password:** `student123`

*(Note: It is highly recommended to log in and change these passwords or create a new admin account if deploying to production).*

---

## 🔒 Security Features
- **Session Management**: Secure server-side sessions with strict `@login_required` enforcement on all private routes.
- **Role-based Access Control (RBAC)**: Custom decorators ensuring students cannot access admin API endpoints or dashboards.
- **Cache Prevention**: Advanced HTTP headers preventing browsers from serving cached sensitive pages after a user logs out.
- **Password Hashing**: All passwords are cryptographically hashed using `Werkzeug` before entering the database.

---

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! 
Feel free to check [issues page](https://github.com/your-username/digital-library-manager/issues) if you want to contribute.

## 📝 License
This project is open-source and available under the [MIT License](LICENSE).
