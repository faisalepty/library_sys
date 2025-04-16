# Library Management Web Application

## Overview

The Library Management Web Application is a Django-based system designed to streamline operations for a local library. Built to assist librarians in managing books, members, and transactions, this application eliminates manual tracking by providing a user-friendly interface for core library tasks. The system focuses on simplicity, assuming use by librarians only, without complex session or role management.

Visit  [live site](https://flibrary.pythonanywhere.com/). login with username: admin, password: admin123

The project fulfills the following objectives:

- Maintain an inventory of books with stock quantities.
- Manage member information.
- Track book transactions, including issuance and returns.
- Enforce financial rules, such as limiting members’ outstanding debts to KES 500.
- Enable searching for books by title and author.
- Calculate and apply rental fees upon book returns.

## Features

### 1. Book Management

- CRUD Operations: Librarians can create, read, update, and delete books.
- Stock is maintained to prevent issuing books when unavailable.
  
### 2. Member Management

- CRUD Operations: Librarians can add, view, update, and remove members.
- Outstanding debt is monitored to enforce the KES 500 limit.
- 
### 3. Transaction Management

- Book Issuance: Librarians can issue books to members, ensuring stock is available and the member’s debt stays within KES 500. An initial fee of KES 150 is applied.
- Book Return: Handles returns, calculating fees (KES 150 initial, plus KES 50/day for late returns after 7 days) and updating stock and debt.
- Debt Payment: Allows members to pay off transaction balances partially or fully.

### 4. Search Functionality

- General Search: Librarians can search for books by title or author to quickly locate inventory.

### 5. Financial Rules

- Debt Limit: Prevents book issuance if a member’s outstanding debt would exceed KES 500.
- Rent Fees: Applied automatically on book returns, including late fees for overdue books.

### 6. Librarian Management

- Account Management: Librarians can manage user accounts to control system access.

### 7. Authentication

- Login/Logout: Provides secure access for librarians to perform all operations.

## Setup Instructions

1. Clone the Repository:

   ```bash
   git clone <repository-url>
   cd library
2. Set Up Virtual Environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
3. Install Dependencies:
    ```bash
    pip install -r requirements.txt
4. Apply Migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
5. Create a Superuser (for login):
   ```bash
   python manage.py createsuperuser
6. Run the Server:
   ```bash
   python manage.py runserver
Access at http://127.0.0.1:8000/.
