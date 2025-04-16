from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from datetime import date
from decimal import Decimal
from base.models import Book, Member, Transaction

class BookModelTest(TestCase):
    """Tests for the Book model."""
    def test_create_book_with_required_fields(self):
        """Test creating a book with only required fields."""
        book = Book.objects.create(
            title="Test Book",
            author="Test Author"
        )
        self.assertEqual(book.title, "Test Book")
        self.assertEqual(book.author, "Test Author")
        self.assertIsNone(book.genre)
        self.assertIsNone(book.isbn)
        self.assertIsNone(book.publication_date)
        self.assertIsNone(book.description)
        self.assertEqual(book.stock, 0)

    def test_create_book_with_all_fields(self):
        """Test creating a book with all fields."""
        book = Book.objects.create(
            title="Full Book",
            author="Full Author",
            genre="Fiction",
            isbn="1234567890123",
            publication_date=date(2023, 1, 1),
            description="A test book description",
            stock=10
        )
        self.assertEqual(book.title, "Full Book")
        self.assertEqual(book.author, "Full Author")
        self.assertEqual(book.genre, "Fiction")
        self.assertEqual(book.isbn, "1234567890123")
        self.assertEqual(book.publication_date, date(2023, 1, 1))
        self.assertEqual(book.description, "A test book description")
        self.assertEqual(book.stock, 10)

    def test_book_str(self):
        """Test the string representation of a book."""
        book = Book.objects.create(title="Str Book", author="Str Author")
        self.assertEqual(str(book), "Str Book")

    def test_isbn_unique_constraint(self):
        """Test that ISBN is unique."""
        Book.objects.create(title="Book 1", author="Author", isbn="1234567890123")
        with self.assertRaises(ValidationError):
            book2 = Book(title="Book 2", author="Author", isbn="1234567890123")
            book2.full_clean()

    def test_stock_positive_integer(self):
        """Test that stock cannot be negative."""
        with self.assertRaises(ValidationError):
            book = Book(title="Invalid Book", author="Author", stock=-1)
            book.full_clean()

    def test_title_max_length(self):
        """Test that title respects max_length."""
        long_title = "x" * 256
        with self.assertRaises(ValidationError):
            book = Book(title=long_title, author="Author")
            book.full_clean()

class MemberModelTest(TestCase):
    """Tests for the Member model."""
    def test_create_member_with_required_fields(self):
        """Test creating a member with required fields."""
        member = Member.objects.create(
            name="Test Member",
            email="test@example.com"
        )
        self.assertEqual(member.name, "Test Member")
        self.assertEqual(member.email, "test@example.com")
        self.assertIsNone(member.phone_number)
        self.assertIsNone(member.address)
        self.assertEqual(member.outstanding_debt, Decimal("0.00"))
        self.assertTrue(member.is_active)
        self.assertEqual(member.membership_date, date.today())

    def test_create_member_with_all_fields(self):
        """Test creating a member with all fields."""
        member = Member.objects.create(
            name="Full Member",
            email="full@example.com",
            phone_number="1234567890",
            address="123 Test St",
            outstanding_debt=Decimal("50.00"),
            is_active=False
        )
        self.assertEqual(member.name, "Full Member")
        self.assertEqual(member.email, "full@example.com")
        self.assertEqual(member.phone_number, "1234567890")
        self.assertEqual(member.address, "123 Test St")
        self.assertEqual(member.outstanding_debt, Decimal("50.00"))
        self.assertFalse(member.is_active)
        self.assertEqual(member.membership_date, date.today())

    def test_member_str(self):
        """Test the string representation of a member."""
        member = Member.objects.create(name="Str Member", email="str@example.com")
        self.assertEqual(str(member), "Str Member")

    def test_email_unique_constraint(self):
        """Test that email is unique."""
        Member.objects.create(name="Member 1", email="same@example.com")
        with self.assertRaises(ValidationError):
            member2 = Member(name="Member 2", email="same@example.com")
            member2.full_clean()

    def test_outstanding_debt_decimal(self):
        """Test outstanding_debt field precision."""
        member = Member.objects.create(
            name="Debt Member",
            email="debt@example.com",
            outstanding_debt=Decimal("123.45")
        )
        self.assertEqual(member.outstanding_debt, Decimal("123.45"))

    def test_membership_date_auto_now_add(self):
        """Test that membership_date is set automatically."""
        member = Member.objects.create(name="Auto Member", email="auto@example.com")
        self.assertEqual(member.membership_date, date.today())

class TransactionModelTest(TestCase):
    """Tests for the Transaction model."""
    def setUp(self):
        """Set up book and member for transaction tests."""
        self.book = Book.objects.create(title="Test Book", author="Author")
        self.member = Member.objects.create(name="Test Member", email="test@example.com")

    def test_create_transaction_minimal(self):
        """Test creating a transaction with minimal fields."""
        transaction = Transaction.objects.create(
            book=self.book,
            member=self.member
        )
        self.assertEqual(transaction.book, self.book)
        self.assertEqual(transaction.member, self.member)
        self.assertEqual(transaction.issue_date, date.today())
        self.assertIsNone(transaction.return_date)
        self.assertEqual(transaction.fee, Decimal("150.00"))
        self.assertEqual(transaction.amount_paid, Decimal("0.00"))
        self.assertEqual(transaction.balance, Decimal("150.00"))

    def test_create_transaction_with_all_fields(self):
        """Test creating a transaction with all fields."""
        transaction = Transaction.objects.create(
            book=self.book,
            member=self.member,
            return_date=date.today(),
            fee=Decimal("200.00"),
            amount_paid=Decimal("100.00")
        )
        self.assertEqual(transaction.fee, Decimal("200.00"))
        self.assertEqual(transaction.amount_paid, Decimal("100.00"))
        self.assertEqual(transaction.balance, Decimal("100.00"))
        self.assertEqual(transaction.return_date, date.today())

    def test_transaction_save_balance_calculation(self):
        """Test that save method calculates balance correctly."""
        transaction = Transaction(book=self.book, member=self.member)
        transaction.fee = Decimal("300.00")
        transaction.amount_paid = Decimal("50.00")
        transaction.save()
        self.assertEqual(transaction.balance, Decimal("250.00"))

    def test_transaction_str(self):
        """Test the string representation of a transaction."""
        transaction = Transaction.objects.create(book=self.book, member=self.member)
        self.assertEqual(str(transaction), "Test Book issued to Test Member")

    def test_balance_update_on_save(self):
        """Test that balance updates when fee or amount_paid changes."""
        transaction = Transaction.objects.create(
            book=self.book,
            member=self.member,
            fee=Decimal("150.00"),
            amount_paid=Decimal("0.00")
        )
        transaction.amount_paid = Decimal("100.00")
        transaction.save()
        self.assertEqual(transaction.balance, Decimal("50.00"))

    def test_foreign_key_cascade(self):
        """Test that deleting a book or member deletes related transactions."""
        transaction = Transaction.objects.create(book=self.book, member=self.member)
        book_id = self.book.id
        self.book.delete()
        self.assertFalse(Transaction.objects.filter(id=transaction.id).exists())
        new_book = Book.objects.create(title="New Book", author="Author")
        transaction = Transaction.objects.create(book=new_book, member=self.member)
        self.member.delete()
        self.assertFalse(Transaction.objects.filter(id=transaction.id).exists())

    def test_fee_and_amount_paid_nullable(self):
        """Test that setting fee and amount_paid to null raises TypeError in save."""
        with self.assertRaises(TypeError):
            transaction = Transaction(
                book=self.book,
                member=self.member,
                fee=None,
                amount_paid=None
            )
            transaction.save()

    def test_balance_default(self):
        """Test default balance when fee and amount_paid are set."""
        transaction = Transaction(book=self.book, member=self.member)
        transaction.save()
        self.assertEqual(transaction.balance, Decimal("150.00"))