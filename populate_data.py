import os
import django
import random
from datetime import date, timedelta
from faker import Faker

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library.settings')
django.setup()

# Import models
from base.models import Book, Member, Transaction

# Initialize Faker
fake = Faker()

# Sample data for generating books
TITLES = [
    "The Great Gatsby", "To Kill a Mockingbird", "1984", "Pride and Prejudice", "The Catcher in the Rye",
    "Animal Farm", "Brave New World", "The Hobbit", "The Lord of the Rings", "Harry Potter and the Philosopher's Stone",
    "The Alchemist", "The Kite Runner", "A Thousand Splendid Suns", "Life of Pi", "The Book Thief",
    "The Road", "Sapiens: A Brief History of Humankind", "Educated", "Becoming", "The Da Vinci Code",
    "Angels & Demons", "Inferno", "The Hunger Games", "Catching Fire", "Mockingjay",
    "Divergent", "Insurgent", "Allegiant", "The Fault in Our Stars", "Wonder",
    "The Night Circus", "The Girl with the Dragon Tattoo", "The Help", "Gone Girl", "Sharp Objects",
    "Big Little Lies", "Little Fires Everywhere", "Where the Crawdads Sing", "The Silent Patient", "The Midnight Library",
    "The Shadow of the Wind", "The Angel's Game", "The Prisoner of Heaven", "The Labyrinth of the Spirits", "The Shadow Cabinet",
    "The Name of the Wind", "The Wise Man's Fear", "The Doors of Stone", "Mistborn", "Warbreaker"
]

AUTHORS = [
    "F. Scott Fitzgerald", "Harper Lee", "George Orwell", "Jane Austen", "J.D. Salinger",
    "George Orwell", "Aldous Huxley", "J.R.R. Tolkien", "J.R.R. Tolkien", "J.K. Rowling",
    "Paulo Coelho", "Khaled Hosseini", "Khaled Hosseini", "Yann Martel", "Markus Zusak",
    "Cormac McCarthy", "Yuval Noah Harari", "Tara Westover", "Michelle Obama", "Dan Brown",
    "Dan Brown", "Dan Brown", "Suzanne Collins", "Suzanne Collins", "Suzanne Collins",
    "Veronica Roth", "Veronica Roth", "Veronica Roth", "John Green", "R.J. Palacio",
    "Erin Morgenstern", "Stieg Larsson", "Kathryn Stockett", "Gillian Flynn", "Gillian Flynn",
    "Liane Moriarty", "Celeste Ng", "Delia Owens", "Alex Michaelides", "Matt Haig",
    "Carlos Ruiz Zafón", "Carlos Ruiz Zafón", "Carlos Ruiz Zafón", "Carlos Ruiz Zafón", "Rin Chupeco",
    "Patrick Rothfuss", "Patrick Rothfuss", "Patrick Rothfuss", "Brandon Sanderson", "Brandon Sanderson"
]

GENRES = [
    "Fiction", "Classic", "Science Fiction", "Romance", "Fantasy",
    "Historical Fiction", "Mystery", "Thriller", "Non-Fiction", "Biography",
    "Self-Help", "Adventure", "Young Adult", "Horror", "Poetry"
]

def generate_isbn():
    """Generate a random unique ISBN."""
    return ''.join(random.choices('0123456789', k=13))

def generate_publication_date():
    """Generate a random publication date between 1900 and 2023."""
    start_date = date(1900, 1, 1)
    end_date = date(2023, 1, 1)
    random_days = random.randint(0, (end_date - start_date).days)
    return start_date + timedelta(days=random_days)

def populate_books(num_books=50):
    """Populate the database with sample books."""
    for i in range(num_books):
        title = TITLES[i % len(TITLES)]
        author = AUTHORS[i % len(AUTHORS)]
        genre = random.choice(GENRES)
        isbn = generate_isbn()
        publication_date = generate_publication_date()
        description = f"A captivating {genre.lower()} book by {author}."
        stock = random.randint(1, 20)

        # Create and save the book
        book = Book(
            title=title,
            author=author,
            genre=genre,
            isbn=isbn,
            publication_date=publication_date,
            description=description,
            stock=stock
        )
        book.save()

    print(f"Successfully populated the database with {num_books} books.")

def create_members(num_members=50):
    """Populate the database with sample members."""
    for _ in range(num_members):
        # Generate random data for each member
        name = fake.name()
        email = fake.email()
        phone_number = fake.phone_number()[:15]  # Limit to 15 characters
        address = fake.address().replace('\n', ', ')  # Replace newlines with commas
        outstanding_debt = round(random.uniform(0, 500), 2)  # Random debt between 0 and 500
        is_active = random.choice([True, False])  # Randomly set active status

        # Create the member
        Member.objects.create(
            name=name,
            email=email,
            phone_number=phone_number,
            address=address,
            outstanding_debt=outstanding_debt,
            is_active=is_active
        )

    print(f"Successfully created {num_members} members.")

from decimal import Decimal  # Import Decimal

def populate_transactions(num_transactions=50):
    """Populate the database with sample transactions."""
    books = list(Book.objects.all())
    members = list(Member.objects.all())

    if not books or not members:
        print("Error: No books or members available to create transactions.")
        return

    for _ in range(num_transactions):
        # Randomly select a book and a member
        book = random.choice(books)
        member = random.choice(members)

        # Skip if the book's stock is 0 (cannot issue a book with no stock)
        if book.stock <= 0:
            continue

        # Generate random issue and return dates
        issue_date = fake.date_between(start_date='-1y', end_date='today')  # Issue date within the last year
        return_date = None
        fee = Decimal('0')  # Use Decimal instead of float
        amount_paid = Decimal('0')  # Use Decimal instead of float

        # Randomly decide if the book is returned
        if random.random() > 0.5:  # 50% chance of being returned
            return_date = fake.date_between(start_date=issue_date, end_date='today')

            # Calculate fee
            days_borrowed = (return_date - issue_date).days
            initial_fee = Decimal('150')  # Initial fee as Decimal
            late_fee = Decimal(max(0, (days_borrowed - 7) * 50))  # Late fee as Decimal
            total_fee = initial_fee + late_fee

            # Randomly generate amount paid
            amount_paid = Decimal(random.uniform(0, float(total_fee)))  # Convert float to Decimal
            remaining_fee = total_fee - amount_paid

            # Update member's outstanding debt
            member.outstanding_debt += remaining_fee  # Now compatible with Decimal
            member.save()

            # Update book stock
            book.stock += 1  # Return the book
            book.save()

        else:
            # If not returned, deduct stock
            book.stock -= 1  # Issue the book
            book.save()

        # Create the transaction
        Transaction.objects.create(
            book=book,
            member=member,
            issue_date=issue_date,
            return_date=return_date,
            fee=fee if return_date else None,
            amount_paid=amount_paid if return_date else None
        )

    print(f"Successfully created {num_transactions} transactions.")

def update


    
if __name__ == "__main__":
    # Populate books
    populate_books()

    # Populate members
    create_members()

    # Populate transactions
    populate_transactions()