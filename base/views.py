from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from .models import Book, Member, Transaction
from datetime import date

from decimal import Decimal 



from django.shortcuts import render
from django.db.models import Count, Q
from datetime import date
from .models import Book, Member, Transaction
from datetime import timedelta
from django.utils.timezone import now
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required

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

@login_required(login_url='/login/')
def dashboard(request):
    

    #  uncomment the filters
    overdue_history = Transaction.objects.filter(
            # return_date__isnull=True,
            # issue_date__lt=timezone.now() - timedelta(days=7)
    ).select_related('book', 'member').values(
        'member__id', 'book__title', 'book__isbn'
    )[:5]

    # Fetch data for the "Recent Check-out’s" table
    recent_checkouts = Transaction.objects.filter(
        return_date__isnull=True
    ).select_related('book', 'member').order_by('-issue_date').values(
        'id', 'book__isbn', 'book__title', 'book__author', 'member__name', 'issue_date'
    )[:5]

    # Fetch raw data for borrowed and returned books
    checkout_stats = Transaction.objects.all().values('issue_date', 'return_date')

    # Initialize a single dictionary to store counts for both borrowed and returned books
    monthly_stats = {}

    # Process each transaction
    for entry in checkout_stats:
        month_key = entry['issue_date'].strftime('%b %Y')  # Format: "Jan 2023"
        
        # Initialize the month if not already present
        if month_key not in monthly_stats:
            monthly_stats[month_key] = {'borrowed': 0, 'returned': 0}
        
        # Count borrowed books (return_date is null)
        if entry['return_date'] is None:
            monthly_stats[month_key]['borrowed'] += 1
        
        # Count returned books (return_date is not null)
        else:
            monthly_stats[month_key]['returned'] += 1

    # Extract sorted months and prepare data for Chart.js
    months = sorted(monthly_stats.keys())  # Sort months chronologically
    borrowed_data = [monthly_stats[month]['borrowed'] for month in months]
    returned_data = [monthly_stats[month]['returned'] for month in months]

    members_count = Member.objects.all().count()
    books_count = Book.objects.all().count()
    issued_books = Transaction.objects.filter(return_date__isnull=True).count()
    overdue_books = Transaction.objects.filter(
                    return_date__isnull=True, 
                    issue_date__lt=now().date() - timedelta(days=7)).count()
    new_arrivals = Book.objects.all().order_by('-id')[:3]

    # Pass data to the template
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

@login_required(login_url='/login/')
def general_search(request):
    search_type = request.GET.get('search_type', '')
    search_query = request.GET.get('search_query', '')

    # Initialize results
    results = []

    if search_type == 'book_title':
        results = list(Book.objects.filter(title__icontains=search_query).values('id', 'title', 'author'))
    elif search_type == 'book_author':
        results = list(Book.objects.filter(author__icontains=search_query).values('id', 'title', 'author'))
    elif search_type == 'member_name':
        results = list(Member.objects.filter(name__icontains=search_query).values('id', 'name', 'email'))

    # Add a "type" field to distinguish between books and members
    for result in results:
        if 'author' in result:
            result['type'] = 'book'
        elif 'email' in result:
            result['type'] = 'member'

    return JsonResponse(results, safe=False)

@login_required(login_url='/login/')
def book_list(request):
    page = request.GET.get('page', 1)
    search_type = request.GET.get('search_type', '')
    search_query = request.GET.get('search_query', '')

    # Filter books
    books = Book.objects.all()

    if search_type == 'title':
        books = books.filter(title__icontains=search_query)
    elif search_type == 'author':
        books = books.filter(author__icontains=search_query)

    # Paginate results
    paginator = Paginator(books, 10)  # 10 books per page
    books_page = paginator.get_page(page)

    # Prepare data for response
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

    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(data)

    # Render the template for non-AJAX requests
    return render(request, 'book_list.html', {'books': books_page})

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Book

@login_required(login_url='/login/')
def create_book(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        genre = request.POST.get('genre', '')
        isbn = request.POST.get('isbn', '')
        stock = request.POST.get('stock', 0)

        # Validate input (basic validation)
        if not title or not author:
            return JsonResponse({'success': False, 'message': 'Title and Author are required.'})

        # Create the book
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

        # Save the updated book
        try:
            book.save()
            return JsonResponse({'success': True, 'message': 'Book updated successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

@login_required(login_url='/login/')
def delete_book(request, book_id):
    if request.method == 'POST':
        book = get_object_or_404(Book, id=book_id)

        # Delete the book
        try:
            book.delete()
            return JsonResponse({'success': True, 'message': 'Book deleted successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

@login_required(login_url='/login/')
def fetch_book_details(request, book_id):
    if request.method == 'GET':
        # Fetch the book by ID
        book = get_object_or_404(Book, id=book_id)

        # Prepare the response data
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
def book_details(request, book_id):
    # Fetch the book
    book = get_object_or_404(Book, id=book_id)

    # Fetch related transactions (borrow history)
    transactions = Transaction.objects.filter(book=book).order_by('-issue_date')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return JSON response for AJAX requests
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
    # Render the template for non-AJAX requests
    return render(request, 'book_details.html', {'book': book, 'transactions': transactions, 'b_d': 'b_d'})

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
def member_list(request):
    page = request.GET.get('page', 1)
    search_query = request.GET.get('search', '')

    # Filter members based on search query
    members = Member.objects.filter(
        name__icontains=search_query) | Member.objects.filter(email__icontains=search_query)

    # Add explicit ordering to avoid UnorderedObjectListWarning
    members = members.order_by('id')  # Order by primary key (or any other field like 'name')

    # Paginate results
    paginator = Paginator(members, 10)  # 10 members per page
    members_page = paginator.get_page(page)

    # Prepare data for response
    data = {
        'members': [
            {
                'id': member.id,
                'name': member.name,
                'email': member.email,
                'phone_number': member.phone_number or '-',
                'outstanding_debt': str(member.outstanding_debt),
                'is_active': member.is_active,
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

    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(data)

    # Render the template for non-AJAX requests
    return render(request, 'member_list.html')

@login_required(login_url='/login/')
def add_or_edit_member(request):
    if request.method == 'POST':
        member_id = request.POST.get('id')  # ID will be empty for "Add"
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number', '')
        address = request.POST.get('address', '')
        outstanding_debt = request.POST.get('outstanding_debt') or 0

        # Validate input
        if not name or not email:
            return JsonResponse({'success': False, 'message': 'Name and Email are required.'})

        try:
            if member_id:  # Edit existing member
                member = get_object_or_404(Member, id=member_id)
                member.name = name
                member.email = email
                member.phone_number = phone_number
                member.address = address
                member.outstanding_debt = outstanding_debt
                member.save()
                return JsonResponse({'success': True, 'message': 'Member updated successfully.'})
            else:  # Create new member
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
def member_details(request, member_id):
    # Fetch the member
    member = get_object_or_404(Member, id=member_id)

    # Fetch related transactions (borrow history)
    transactions = Transaction.objects.filter(member=member).order_by('-issue_date')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return JSON response for AJAX requests
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

    # Render the template for non-AJAX requests
    return render(request, 'member_details.html', {'member': member, 'transactions': transactions, 'm_d': 'm_d'})

@login_required(login_url='/login/')
def issue_book(request):
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        member_id = request.POST.get('member_id')

        # Fetch book and member
        book = get_object_or_404(Book, id=book_id)
        member = get_object_or_404(Member, id=member_id)

        # Validate stock availability
        if book.stock <= 0:
            return JsonResponse({'success': False, 'message': 'Book is out of stock.'})

        # Validate outstanding debt limit
        if member.outstanding_debt >= 500:
            return JsonResponse({'success': False, 'message': 'Member has exceeded the debt limit of KES 500.'})

        try:
            # Create the transaction
            Transaction.objects.create(book=book, member=member)

            # Update book stock
            book.stock -= 1
            book.save()

            # Add initial fee to member's outstanding debt
            member.outstanding_debt += 150  # Initial fee of KES 150
            member.save()

            return JsonResponse({'success': True, 'message': 'Book issued successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

@login_required(login_url='/login/')
def return_book(request):
    if request.method == 'POST':
        # Get transaction ID and amount paid from the request
        transaction_id = request.POST.get('transaction_id')
        try:
            amount_paid = Decimal(request.POST.get('amount_paid', 0))  # Convert to Decimal
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid amount paid.'})

        # Validate amount paid
        if amount_paid < 0:
            return JsonResponse({'success': False, 'message': 'Amount paid cannot be negative.'})

        # Fetch the transaction
        transaction = get_object_or_404(Transaction, id=transaction_id)

        # Calculate total fee
        issue_date = transaction.issue_date
        return_date = date.today()
        days_borrowed = (return_date - issue_date).days

        # Initial fee: KES 150
        initial_fee = Decimal(150)

        # Late fee: KES 50 per day after 7 days
        late_fee = Decimal(max(0, (days_borrowed - 7) * 50))

        total_fee = initial_fee + late_fee

        # Calculate remaining fee
        remaining_fee = total_fee - amount_paid

        try:
            # Update the transaction
            transaction.return_date = return_date
            transaction.fee = total_fee
            transaction.amount_paid = amount_paid
            transaction.save()

            # Update book stock
            transaction.book.stock += 1
            transaction.book.save()

            # Update member's outstanding debt
            # Ensure outstanding debt doesn't go below zero
            transaction.member.outstanding_debt += max(remaining_fee, 0)
            transaction.member.save()

            return JsonResponse({
                'success': True,
                'message': 'Book returned successfully.',
                'total_fee': str(total_fee),  # Convert Decimal to string for JSON serialization
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

    # Filter transactions
    transactions = Transaction.objects.all()

    if member_id:
        transactions = transactions.filter(member_id=member_id)
    if book_id:
        transactions = transactions.filter(book_id=book_id)

    # Apply search filters
    if search_type == 'title':
        transactions = transactions.filter(book__title__icontains=search_query)
    elif search_type == 'member':
        transactions = transactions.filter(member__name__icontains=search_query)

    transactions = transactions.order_by('-id')
    # Paginate results
    paginator = Paginator(transactions, 10)  # 10 transactions per page
    transactions_page = paginator.get_page(page)

    # Prepare data for response
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

    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(data)

    # Render the template for non-AJAX requests
    return render(request, 'transaction_list.html', {'transactions': transactions_page, 'filters': {'member_id': member_id, 'book_id': book_id}})

@login_required(login_url='/login/')
def pay_debt(request):
    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id')
        payment_amount = request.POST.get('payment_amount')

        try:
            # Fetch the transaction and validate payment amount
            transaction = get_object_or_404(Transaction, id=transaction_id)
            payment_amount = Decimal(payment_amount)

            if payment_amount <= 0:
                return JsonResponse({'success': False, 'message': 'Payment amount must be greater than zero.'})

            # Ensure the payment does not exceed the remaining balance
            if payment_amount > transaction.balance:
                return JsonResponse({'success': False, 'message': 'Payment amount exceeds the remaining balance.'})

            # Update the transaction
            transaction.amount_paid += payment_amount
            transaction.save()  # This will recalculate the balance

            # Update the member's outstanding debt
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


@login_required(login_url='/login/')
def librarian_list(request):
    # Get query parameters
    page = request.GET.get('page', 1)
    search_query = request.GET.get('search', '')

    # Filter librarians based on search query
    librarians = User.objects.filter(
        Q(username__icontains=search_query) | 
        Q(email__icontains=search_query)
    ).order_by('id')

    # Paginate results
    from django.core.paginator import Paginator
    paginator = Paginator(librarians, 10)  # 10 librarians per page
    librarians_page = paginator.get_page(page)

    # Prepare data for response
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

    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(data)

    # Render the template for non-AJAX requests
    return render(request, 'librarian_list.html', {'librarians': librarians_page})



@login_required(login_url='/login/')
def add_or_edit_librarian(request):
    if request.method == 'POST':
        librarian_id = request.POST.get('librarian_id')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            if librarian_id:  # Edit existing librarian
                librarian = get_object_or_404(User, id=librarian_id)
                librarian.username = username
                librarian.email = email
                if password:  # Only update password if provided
                    librarian.set_password(password)
                librarian.save()

                return JsonResponse({'success': True, 'message': 'Librarian updated successfully.'})
            else:  # Add new librarian
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