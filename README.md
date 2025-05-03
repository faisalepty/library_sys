# Library Management Web Application

## Overview

The Library Management Web Application is a Django-based system designed to streamline operations for a library. Built to assist librarians in managing books, members, and transactions. The system focuses on simplicity, assuming use by librarians only.

Visit  [live site](https://flibrary.pythonanywhere.com/). login with username: admin, password: admin123
visit similar application built with frappe [Frappe library management system app](https://github.com/faisalepty/library-sys-frappe)

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
  ![Image](https://github.com/user-attachments/assets/a6651c9d-3b6b-4724-9719-bca30c43cad1)
    
### 2. Member Management

- CRUD Operations: Librarians can add, view, update, and remove members.
- Outstanding debt is monitored to enforce the KES 500 limit.
  ![Image](https://github.com/user-attachments/assets/189d0c33-de33-4d0a-a2a6-75536fc7b349)

### 3. Transaction Management

- Book Issuance: Librarians can issue books to members, ensuring stock is available and the member’s debt stays within KES 500. An initial fee of KES 150 is applied.
- Book Return: Handles returns, calculating fees (KES 150 initial, plus KES 50/day for late returns after 7 days) and updating stock and debt.
- Debt Payment: Allows members to pay off transaction balances partially or fully.
  ![Image](https://github.com/user-attachments/assets/70c51c92-8f6d-4d48-9b76-fe3ba88dd4d0)

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
   git clone https://github.com/faisalepty/library_sys.git
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
