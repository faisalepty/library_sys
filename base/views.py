from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q
from django.utils.timezone import now
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from decimal import Decimal
from .models import Book, Member, Transaction

# User Authentication
def user_login(request):
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True, 'redirect_url': '/'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid username or password.'})
    else:
        return render(request, 'base.html')
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

def user_logout(request):
    
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'success': True, 'message': 'Logout successful.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

# Dashboard
@login_required(login_url='/login/')
def dashboard(request):
    
    overdue_history = Transaction.objects.filter(
    )[:5]

    recent_checkouts = Transaction.objects.filter(
        return_date__isnull=True
    ).select_related('book', 'member').order_by('-issue_date').values(
        'id', 'book__isbn', 'book__title', 'book__author', 'member__name', 'issue_date'
    )[:5]

    checkout_stats = Transaction.objects.all().values('issue_date', 'return_date')
    monthly_stats = {}
    for entry in checkout_stats:
        month_key = entry['issue_date'].strftime('%b %Y')
        if month_key not in monthly_stats:
            monthly_stats[month_key] = {'borrowed': 0, 'returned': 0}
        if entry['return_date'] is None:
            monthly_stats[month_key]['borrowed'] += 1
        else:
            monthly_stats[month_key]['returned'] += 1

    months = sorted(monthly_stats.keys())
    borrowed_data = [monthly_stats[month]['borrowed'] for month in months]
    returned_data = [monthly_stats[month]['returned'] for month in months]

    members_count = Member.objects.all().count()
    books_count = Book.objects.all().count()
    issued_books = Transaction.objects.filter(return_date__isnull=True).count()
    overdue_books = Transaction.objects.filter(
        return_date__isnull=True,
        issue_date__lt=now().date() - timedelta(days=7)
    ).count()
    new_arrivals = Book.objects.all().order_by('-id')[:3]

    context = {
        'members_count': members_count,
        'books_count': books_count,
        'issued_books': issued_books,
        'overdue_books': overdue_books,
        'overdue_history': overdue_history,
        'recent_checkouts': recent_checkouts,
        'new_arrivals': new_arrivals,
        'checkout_stats_months': months,
        'checkout_stats_borrowed': borrowed_data,
        'checkout_stats_returned': returned_data,
        'd': 'd'
    }
    return render(request, 'dashboard.html', context)

# Search
@login_required(login_url='/login/')
def general_search(request):
    
    search_type = request.GET.get('search_type', '')
    search_query = request.GET.get('search_query', '')
    results = []
    if search_type == 'book_title':
        results = list(Book.objects.filter(title__icontains=search_query).values('id', 'title', 'author'))
    elif search_type == 'book_author':
        results = list(Book.objects.filter(author__icontains=search_query).values('id', 'title', 'author'))
    elif search_type == 'member_name':
        results = list(Member.objects.filter(name__icontains=search_query).values('id', 'name', 'email'))
    for result in results:
        if 'author' in result:
            result['type'] = 'book'
        elif 'email' in result:
            result['type'] = 'member'
    return JsonResponse(results, safe=False)

# Book Management
@login_required(login_url='/login/')
def book_list(request):
    
    page = request.GET.get('page', 1)
    search_type = request.GET.get('search_type', '')
    search_query = request.GET.get('search_query', '')
    books = Book.objects.all()
    if search_type == 'title':
        books = books.filter(title__icontains=search_query)
    elif search_type == 'author':
        books = books.filter(author__icontains=search_query)
    paginator = Paginator(books, 10)
    books_page = paginator.get_page(page)
    data = {
        'books': [
            {
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'genre': book.genre,
                'stock': book.stock,
            }
            for book in books_page
        ],
        'pagination': {
            'has_previous': books_page.has_previous(),
            'has_next': books_page.has_next(),
            'previous_page_number': books_page.previous_page_number() if books_page.has_previous() else None,
            'next_page_number': books_page.next_page_number() if books_page.has_next() else None,
            'current_page': books_page.number,
            'total_pages': paginator.num_pages,
        },
    }
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(data)
    return render(request, 'book_list.html', {'books': books_page})

@login_required(login_url='/login/')
def create_book(request):
    
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        genre = request.POST.get('genre', '')
        isbn = request.POST.get('isbn', '')
        stock = request.POST.get('stock', 0)
        if not title or not author:
            return JsonResponse({'success': False, 'message': 'Title and Author are required.'})
        try:
            Book.objects.create(
                title=title,
                author=author,
                genre=genre,
                isbn=isbn,
                stock=stock
            )
            return JsonResponse({'success': True, 'message': 'Book created successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

@login_required(login_url='/login/')
def update_book(request, book_id):
    
    if request.method == 'POST':
        book = get_object_or_404(Book, id=book_id)
        book.title = request.POST.get('title', book.title)
        book.author = request.POST.get('author', book.author)
        book.genre = request.POST.get('genre', book.genre)
        book.isbn = request.POST.get('isbn', book.isbn)
        book.stock = request.POST.get('stock', book.stock)
        try:
            book.save()
            return JsonResponse({'success': True, 'message': 'Book updated successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

@login_required(login_url='/login/')
def delete_book(request, book_id):
    
    if request.method == 'POST':
        book = get_object_or_404(Book, id=book_id)
        try:
            book.delete()
            return JsonResponse({'success': True, 'message': 'Book deleted successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

@login_required(login_url='/login/')
def fetch_book_details(request, book_id):
   
    if request.method == 'GET':
        book = get_object_or_404(Book, id=book_id)
        data = {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'genre': book.genre,
            'isbn': book.isbn,
            'stock': book.stock,
        }
        return JsonResponse(data)

@login_required(login_url='/login/')
def fetch_all_books(request):
    
    books = Book.objects.all()
    data = {'books': [{'id': book.id,
                'title': book.title,
                'author': book.author,
                'genre': book.genre,
                'stock': book.stock,} for book in books]}
    return JsonResponse(data)

@login_required(login_url='/login/')
def book_details_page(request, book_id):
    
    book = get_object_or_404(Book, id=book_id)
    transactions = Transaction.objects.filter(book=book).order_by('-issue_date')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'genre': book.genre,
            'isbn': book.isbn,
            'publication_date': book.publication_date.strftime('%Y-%m-%d') if book.publication_date else '-',
            'description': book.description or '-',
            'stock': book.stock,
            'transactions': [
                {
                    'transaction_id': t.id,
                    'member_name': t.member.name,
                    'issue_date': t.issue_date.strftime('%Y-%m-%d'),
                    'return_date': t.return_date.strftime('%Y-%m-%d') if t.return_date else '-',
                    'amount_paid': str(t.amount_paid) if t.amount_paid else 0,
                    'balance': t.balance if t.balance else 0,
                }
                for t in transactions
            ],
        }
        return JsonResponse(data)
    for transaction in transactions:
        print(transaction.id, transaction.return_date)
    return render(request, 'book_details.html', {'book': book, 'transactions': transactions, 'b_d': 'b_d'})



# Member Management
@login_required(login_url='/login/')
def member_list(request):
    
    page = request.GET.get('page', 1)
    search_query = request.GET.get('search', '')
    members = Member.objects.filter(
        name__icontains=search_query) | Member.objects.filter(email__icontains=search_query)
    members = members.order_by('id')
    paginator = Paginator(members, 10)
    members_page = paginator.get_page(page)
    data = {
        'members': [
            {
                'id': member.id,
                'name': member.name,
                'email': member.email,
                'phone_number': member.phone_number or '-',
                'outstanding_debt': str(member.outstanding_debt),
                
            }
            for member in members_page
        ],
        'pagination': {
            'has_previous': members_page.has_previous(),
            'has_next': members_page.has_next(),
            'previous_page_number': members_page.previous_page_number() if members_page.has_previous() else None,
            'next_page_number': members_page.next_page_number() if members_page.has_next() else None,
            'current_page': members_page.number,
            'total_pages': paginator.num_pages,
        },
    }
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(data)
    return render(request, 'member_list.html')

@login_required(login_url='/login/')
def add_or_edit_member(request):
    
    if request.method == 'POST':
        member_id = request.POST.get('id')
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number', '')
        address = request.POST.get('address', '')
        outstanding_debt = request.POST.get('outstanding_debt') or 0
        if not name or not email:
            return JsonResponse({'success': False, 'message': 'Name and Email are required.'})
        try:
            if member_id:
                member = get_object_or_404(Member, id=member_id)
                member.name = name
                member.email = email
                member.phone_number = phone_number
                member.address = address
                member.outstanding_debt = outstanding_debt
                member.save()
                return JsonResponse({'success': True, 'message': 'Member updated successfully.'})
            else:
                Member.objects.create(
                    name=name,
                    email=email,
                    phone_number=phone_number,
                    address=address,
                    outstanding_debt=outstanding_debt
                )
                return JsonResponse({'success': True, 'message': 'Member created successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

@login_required(login_url='/login/')
def delete_member(request, member_id):
    
    if request.method == 'POST':
        member = get_object_or_404(Member, id=member_id)
        try:
            member.delete()
            return JsonResponse({'success': True, 'message': 'Member deleted successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

@login_required(login_url='/login/')
def fetch_member_details(request, member_id):
   
    if request.method == 'GET':
        member = get_object_or_404(Member, id=member_id)
        data = {
            'id': member.id,
            'name': member.name,
            'email': member.email,
            'phone_number': member.phone_number or '',
            'address': member.address or '',
            'outstanding_debt': str(member.outstanding_debt),
            'is_active': member.is_active,
        }
        return JsonResponse(data)

@login_required(login_url='/login/')
def fetch_all_members(request):

    members = Member.objects.all()
    data = {'members':
            [{
                'id': member.id,
                'name': member.name,
                'email': member.email,
                'phone_number': member.phone_number or '-',
                'outstanding_debt': str(member.outstanding_debt),
                'is_active': member.is_active, } for member in members]}
    return JsonResponse(data)

@login_required(login_url='/login/')
def member_details_page(request, member_id):
   
    member = get_object_or_404(Member, id=member_id)
    transactions = Transaction.objects.filter(member=member).order_by('-issue_date')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = {
            'id': member.id,
            'name': member.name,
            'email': member.email,
            'phone_number': member.phone_number or '-',
            'address': member.address or '-',
            'outstanding_debt': str(member.outstanding_debt),
            'is_active': member.is_active,
            'transactions': [
                {
                    'transaction_id': t.id,
                    'book_title': t.book.title,
                    'issue_date': t.issue_date.strftime('%Y-%m-%d'),
                    'return_date': t.return_date.strftime('%Y-%m-%d') if t.return_date else '-',
                    'fee': str(t.fee) if t.fee else '0.00',
                    'amount_paid': str(t.amount_paid) if t.amount_paid else '0.00',
                    'balance': t.balance,
                }
                for t in transactions
            ],
        }
        return JsonResponse(data)
    return render(request, 'member_details.html', {'member': member, 'transactions': transactions, 'm_d': 'm_d'})

# Transaction Management
@login_required(login_url='/login/')
def issue_book(request):
    
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        member_id = request.POST.get('member_id')
        book = get_object_or_404(Book, id=book_id)
        member = get_object_or_404(Member, id=member_id)
        if book.stock <= 0:
            return JsonResponse({'success': False, 'message': 'Book is out of stock.'})
        if member.outstanding_debt + 150 >= 500:
            return JsonResponse({'success': False, 'message': 'Transaction denied. Member’s total debt cannot exceed KES 500.'})
        try:
            Transaction.objects.create(book=book, member=member)
            book.stock -= 1
            book.save()
            member.outstanding_debt += 150
            member.save()
            return JsonResponse({'success': True, 'message': 'Book issued successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

@login_required(login_url='/login/')
def return_book(request):
   
    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id')
        try:
            amount_paid = Decimal(request.POST.get('amount_paid', 0))
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid amount paid.'})
        if amount_paid < 0:
            return JsonResponse({'success': False, 'message': 'Amount paid cannot be negative.'})
        transaction = get_object_or_404(Transaction, id=transaction_id)
        issue_date = transaction.issue_date
        return_date = date.today()
        days_borrowed = (return_date - issue_date).days
        initial_fee = Decimal(150)
        late_fee = Decimal(max(0, (days_borrowed - 7) * 50))
        total_fee = Decimal(initial_fee + late_fee)
        remaining_fee = total_fee - amount_paid
        try:
            transaction.return_date = return_date
            transaction.fee = total_fee
            transaction.amount_paid = amount_paid
            transaction.save()
            transaction.book.stock += 1
            transaction.book.save()
            transaction.member.outstanding_debt += max(remaining_fee, 0)
            transaction.member.save()
            return JsonResponse({
                'success': True,
                'message': 'Book returned successfully.',
                'total_fee': str(total_fee),
                'amount_paid': str(amount_paid),
                'remaining_fee': str(max(remaining_fee, 0))
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {str(e)}'})

@login_required(login_url='/login/')
def transaction_list(request):
    
    page = request.GET.get('page', 1)
    member_id = request.GET.get('member_id', '')
    book_id = request.GET.get('book_id', '')
    search_type = request.GET.get('search_type', '')
    search_query = request.GET.get('search_query', '')
    transactions = Transaction.objects.all()
    if member_id:
        transactions = transactions.filter(member_id=member_id)
    if book_id:
        transactions = transactions.filter(book_id=book_id)
    if search_type == 'title':
        transactions = transactions.filter(book__title__icontains=search_query)
    elif search_type == 'member':
        transactions = transactions.filter(member__name__icontains=search_query)
    transactions = transactions.order_by('-id')
    paginator = Paginator(transactions, 10)
    transactions_page = paginator.get_page(page)
    data = {
        'transactions': [
            {
                'id': t.id,
                'book_title': t.book.title,
                'member_name': t.member.name,
                'issue_date': t.issue_date.strftime('%Y-%m-%d'),
                'return_date': t.return_date.strftime('%Y-%m-%d') if t.return_date else '-',
                'fee': str(t.fee) if t.fee else '-',
                'amount_paid': str(t.amount_paid) if t.amount_paid else '-',
                'balance': t.balance if t.balance else 0
            }
            for t in transactions_page
        ],
        'pagination': {
            'has_previous': transactions_page.has_previous(),
            'has_next': transactions_page.has_next(),
            'previous_page_number': transactions_page.previous_page_number() if transactions_page.has_previous() else None,
            'next_page_number': transactions_page.next_page_number() if transactions_page.has_next() else None,
            'current_page': transactions_page.number,
            'total_pages': paginator.num_pages,
        },
    }
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(data)
    return render(request, 'transaction_list.html', {'transactions': transactions_page, 'filters': {'member_id': member_id, 'book_id': book_id}})

@login_required(login_url='/login/')
def pay_debt(request):
    
    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id')
        payment_amount = request.POST.get('payment_amount')
        try:
            transaction = get_object_or_404(Transaction, id=transaction_id)
            payment_amount = Decimal(payment_amount)
            if payment_amount <= 0:
                return JsonResponse({'success': False, 'message': 'Payment amount must be greater than zero.'})
            if payment_amount > transaction.balance:
                return JsonResponse({'success': False, 'message': 'Payment amount exceeds the remaining balance.'})
            transaction.amount_paid += payment_amount
            transaction.save()
            member = transaction.member
            member.outstanding_debt -= payment_amount
            member.save()
            return JsonResponse({
                'success': True,
                'message': f'Payment of {payment_amount} successfully applied.',
                'new_balance': str(transaction.balance),
                'outstanding_debt': str(member.outstanding_debt)
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

# Librarian Management
@login_required(login_url='/login/')
def librarian_list(request):
    
    page = request.GET.get('page', 1)
    search_query = request.GET.get('search', '')
    librarians = User.objects.filter(
        Q(username__icontains=search_query) |
        Q(email__icontains=search_query)
    ).order_by('id')
    paginator = Paginator(librarians, 10)
    librarians_page = paginator.get_page(page)
    data = {
        'librarians': [
            {
                'id': librarian.id,
                'username': librarian.username,
                'email': librarian.email,
            }
            for librarian in librarians_page
        ],
        'pagination': {
            'has_previous': librarians_page.has_previous(),
            'has_next': librarians_page.has_next(),
            'previous_page_number': librarians_page.previous_page_number() if librarians_page.has_previous() else None,
            'next_page_number': librarians_page.next_page_number() if librarians_page.has_next() else None,
            'current_page': librarians_page.number,
            'total_pages': paginator.num_pages,
        },
    }
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(data)
    return render(request, 'librarian_list.html', {'librarians': librarians_page})

@login_required(login_url='/login/')
def add_or_edit_librarian(request):
    
    if request.method == 'POST':
        librarian_id = request.POST.get('librarian_id')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            if librarian_id:
                librarian = get_object_or_404(User, id=librarian_id)
                librarian.username = username
                librarian.email = email
                if password:
                    librarian.set_password(password)
                librarian.save()
                return JsonResponse({'success': True, 'message': 'Librarian updated successfully.'})
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                return JsonResponse({'success': True, 'message': 'Librarian added successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@login_required(login_url='/login/')
def get_librarian_details(request, pk):
    
    librarian = get_object_or_404(User, pk=pk)
    data = {
        'id': librarian.id,
        'username': librarian.username,
        'email': librarian.email,
    }
    return JsonResponse(data)

@login_required(login_url='/login/')
def delete_librarian(request, pk):
    
    librarian = get_object_or_404(User, pk=pk)
    librarian.delete()
    return JsonResponse({'success': True, 'message': 'Librarian deleted successfully.'})