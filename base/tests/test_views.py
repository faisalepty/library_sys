from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import date, timedelta
from decimal import Decimal
from base.models import Book, Member, Transaction

class LibraryViewsTestCase(TestCase):
    def setUp(self):
        """Set up test data and client."""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123', email='test@example.com')
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            genre='Fiction',
            isbn='1234567890123',
            stock=5
        )
        self.member = Member.objects.create(
            name='Test Member',
            email='member@example.com',
            phone_number='1234567890',
            outstanding_debt=0.00
        )
        self.transaction = Transaction.objects.create(
            book=self.book,
            member=self.member,
            issue_date=date.today() - timedelta(days=10),
            fee=Decimal('150.00'),
            amount_paid=Decimal('0.00'),
            balance=Decimal('150.00')
        )

    # Authentication Tests
    def test_user_login_success(self):
        """Test successful user login."""
        response = self.client.post(reverse('user_login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True, 'redirect_url': '/'})

    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = self.client.post(reverse('user_login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': False, 'message': 'Invalid username or password.'})

    def test_user_login_get_request(self):
        """Test GET request to login renders base.html."""
        response = self.client.get(reverse('user_login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base.html')

    def test_user_logout(self):
        """Test user logout."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('user_logout'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True, 'message': 'Logout successful.'})

    def test_user_logout_invalid_method(self):
        """Test logout with invalid method."""
        response = self.client.get(reverse('user_logout'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': False, 'message': 'Invalid request method.'})

    # Book Management Tests
    def test_create_book_success(self):
        """Test creating a new book."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('create_book'), {
            'title': 'New Book',
            'author': 'New Author',
            'genre': 'Non-Fiction',
            'isbn': '9876543210987',
            'stock': 10
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True, 'message': 'Book created successfully.'})
        self.assertTrue(Book.objects.filter(title='New Book').exists())

    def test_create_book_missing_fields(self):
        """Test creating a book with missing title."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('create_book'), {
            'author': 'New Author',
            'genre': 'Non-Fiction'
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': False, 'message': 'Title and Author are required.'})

    def test_create_book_unauthenticated(self):
        """Test creating a book without authentication."""
        response = self.client.post(reverse('create_book'), {
            'title': 'New Book',
            'author': 'New Author'
        })
        self.assertEqual(response.status_code, 302)  # Redirects to login

    def test_update_book_success(self):
        """Test updating an existing book."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('update_book', args=[self.book.id]), {
            'title': 'Updated Book',
            'author': 'Updated Author',
            'stock': 3
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True, 'message': 'Book updated successfully.'})
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, 'Updated Book')
        self.assertEqual(self.book.author, 'Updated Author')
        self.assertEqual(self.book.stock, 3)

    def test_update_book_not_found(self):
        """Test updating a non-existent book."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('update_book', args=[999]), {
            'title': 'Updated Book'
        })
        self.assertEqual(response.status_code, 404)

    def test_delete_book_success(self):
        """Test deleting a book."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('delete_book', args=[self.book.id]))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True, 'message': 'Book deleted successfully.'})
        self.assertFalse(Book.objects.filter(id=self.book.id).exists())

    def test_delete_book_not_found(self):
        """Test deleting a non-existent book."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('delete_book', args=[999]))
        self.assertEqual(response.status_code, 404)

    # Member Management Tests
    def test_add_member_success(self):
        """Test creating a new member."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('add_or_edit_member'), {
            'name': 'New Member',
            'email': 'newmember@example.com',
            'phone_number': '0987654321',
            'address': '123 Test St',
            'outstanding_debt': '0.00'
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True, 'message': 'Member created successfully.'})
        self.assertTrue(Member.objects.filter(email='newmember@example.com').exists())

    def test_edit_member_success(self):
        """Test updating an existing member."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('add_or_edit_member'), {
            'id': self.member.id,
            'name': 'Updated Member',
            'email': 'updated@example.com',
            'phone_number': '1112223333'
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True, 'message': 'Member updated successfully.'})
        self.member.refresh_from_db()
        self.assertEqual(self.member.name, 'Updated Member')
        self.assertEqual(self.member.email, 'updated@example.com')

    def test_add_member_missing_fields(self):
        """Test adding a member with missing email."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('add_or_edit_member'), {
            'name': 'New Member'
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': False, 'message': 'Name and Email are required.'})

    def test_delete_member_success(self):
        """Test deleting a member."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('delete_member', args=[self.member.id]))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True, 'message': 'Member deleted successfully.'})
        self.assertFalse(Member.objects.filter(id=self.member.id).exists())

    def test_delete_member_not_found(self):
        """Test deleting a non-existent member."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('delete_member', args=[999]))
        self.assertEqual(response.status_code, 404)

    # Transaction Management Tests
    def test_issue_book_success(self):
        """Test issuing a book to a member."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('issue_book'), {
            'book_id': self.book.id,
            'member_id': self.member.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True, 'message': 'Book issued successfully.'})
        self.book.refresh_from_db()
        self.member.refresh_from_db()
        self.assertEqual(self.book.stock, 4)
        self.assertEqual(self.member.outstanding_debt, Decimal('150.00'))
        self.assertTrue(Transaction.objects.filter(book=self.book, member=self.member).exists())

    def test_issue_book_no_stock(self):
        """Test issuing a book with no stock."""
        self.book.stock = 0
        self.book.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('issue_book'), {
            'book_id': self.book.id,
            'member_id': self.member.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': False, 'message': 'Book is out of stock.'})

    def test_issue_book_exceeds_debt_limit(self):
        """Test issuing a book when member's debt exceeds limit."""
        self.member.outstanding_debt = Decimal('400.00')
        self.member.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('issue_book'), {
            'book_id': self.book.id,
            'member_id': self.member.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'success': False,
            'message': 'Transaction denied. Member’s total debt cannot exceed KES 500.'
        })

    def test_return_book_success(self):
        """Test returning a book with partial payment."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('return_book'), {
            'transaction_id': self.transaction.id,
            'amount_paid': '100.00'
        })
        self.assertEqual(response.status_code, 200)
        expected_response = {
            'success': True,
            'message': 'Book returned successfully.',
            'total_fee': '150',
            'amount_paid': '100.00',
            'remaining_fee': '50.00'
        }
        self.assertJSONEqual(response.content, expected_response)
        self.transaction.refresh_from_db()
        self.book.refresh_from_db()
        self.member.refresh_from_db()
        self.assertEqual(self.transaction.return_date, date.today())
        self.assertEqual(self.transaction.fee, Decimal('150.00'))
        self.assertEqual(self.transaction.amount_paid, Decimal('100.00'))
        self.assertEqual(self.book.stock, 6)
        self.assertEqual(self.member.outstanding_debt, Decimal('50.00'))

    def test_return_book_negative_amount(self):
        """Test returning a book with negative amount paid."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('return_book'), {
            'transaction_id': self.transaction.id,
            'amount_paid': '-100'
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': False, 'message': 'Amount paid cannot be negative.'})

    def test_pay_debt_success(self):
        """Test paying a portion of a transaction's debt."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('pay_debt'), {
            'transaction_id': self.transaction.id,
            'payment_amount': '50.00'
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'success': True,
            'message': 'Payment of 50.00 successfully applied.',
            'new_balance': '100.00',
            'outstanding_debt': '-50.00'
        })
        self.transaction.refresh_from_db()
        self.member.refresh_from_db()
        self.assertEqual(self.transaction.amount_paid, Decimal('50.00'))
        self.assertEqual(self.transaction.balance, Decimal('100.00'))
        self.assertEqual(self.member.outstanding_debt, Decimal('-50.00'))

    def test_pay_debt_exceeds_balance(self):
        """Test paying more than the transaction balance."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('pay_debt'), {
            'transaction_id': self.transaction.id,
            'payment_amount': '200.00'
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'success': False,
            'message': 'Payment amount exceeds the remaining balance.'
        })

    def test_pay_debt_zero_amount(self):
        """Test paying zero amount."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('pay_debt'), {
            'transaction_id': self.transaction.id,
            'payment_amount': '0.00'
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'success': False,
            'message': 'Payment amount must be greater than zero.'
        })

    # Librarian Management Tests
    def test_add_librarian_success(self):
        """Test adding a new librarian."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('add_or_edit_librarian'), {
            'username': 'newlibrarian',
            'email': 'newlibrarian@example.com',
            'password': 'newpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True, 'message': 'Librarian added successfully.'})
        self.assertTrue(User.objects.filter(username='newlibrarian').exists())

    def test_edit_librarian_success(self):
        """Test updating an existing librarian."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('add_or_edit_librarian'), {
            'librarian_id': self.user.id,
            'username': 'updateduser',
            'email': 'updated@example.com',
            'password': 'newpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True, 'message': 'Librarian updated successfully.'})
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')
        self.assertEqual(self.user.email, 'updated@example.com')
        self.assertTrue(self.user.check_password('newpass123'))

    def test_edit_librarian_no_password(self):
        """Test updating a librarian without changing password."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('add_or_edit_librarian'), {
            'librarian_id': self.user.id,
            'username': 'updateduser',
            'email': 'updated@example.com'
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True, 'message': 'Librarian updated successfully.'})
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')
        self.assertTrue(self.user.check_password('testpass123'))  # Password unchanged

    def test_delete_librarian_success(self):
        """Test deleting a librarian."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('delete_librarian', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True, 'message': 'Librarian deleted successfully.'})
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_delete_librarian_not_found(self):
        """Test deleting a non-existent librarian."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('delete_librarian', args=[999]))
        self.assertEqual(response.status_code, 404)