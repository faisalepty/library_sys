from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from .models import Book, Member, Transaction
from datetime import date

from decimal import Decimal 

def book_list(request):
    # Get query parameters
    page = request.GET.get('page', 1)
    search_query = request.GET.get('search', '')

    # Filter books based on search query and order them
    books = Book.objects.filter(
        title__icontains=search_query) | Book.objects.filter(author__icontains=search_query)
    books = books.order_by('id') 

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
    return render(request, 'book_list.html')


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Book

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

def delete_book(request, book_id):
    if request.method == 'POST':
        book = get_object_or_404(Book, id=book_id)

        # Delete the book
        try:
            book.delete()
            return JsonResponse({'success': True, 'message': 'Book deleted successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})


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
                    'amount_paid': str(t.amount_paid) if t.amount_paid else '0.00',
                    'balance': t.balance,
                }
                for t in transactions
            ],
        }
        return JsonResponse(data)

    # Render the template for non-AJAX requests
    return render(request, 'book_details.html', {'book': book, 'transactions': transactions, 'b_d': 'b_d'})

def fetch_all_books(request):

    books = Book.objects.all()

    data = {'books': [{'id': book.id,
                'title': book.title,
                'author': book.author,
                'genre': book.genre,
                'stock': book.stock,} for book in books]}

    return JsonResponse(data)



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


def delete_member(request, member_id):
    if request.method == 'POST':
        member = get_object_or_404(Member, id=member_id)

        try:
            member.delete()
            return JsonResponse({'success': True, 'message': 'Member deleted successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

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


def transaction_list(request):
    page = request.GET.get('page', 1)
    member_id = request.GET.get('member_id', '')
    book_id = request.GET.get('book_id', '')

    # Filter transactions
    transactions = Transaction.objects.all()
    if member_id:
        transactions = transactions.filter(member_id=member_id)
    if book_id:
        transactions = transactions.filter(book_id=book_id)

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