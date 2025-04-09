from django.db import models

# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=255)  # Title of the book
    author = models.CharField(max_length=255)  # Author's name
    genre = models.CharField(max_length=100, blank=True, null=True)  # Genre (e.g., Fiction, Non-Fiction)
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True)  # ISBN number
    publication_date = models.DateField(blank=True, null=True)  # Publication date
    description = models.TextField(blank=True, null=True)  # Short description of the book
    stock = models.PositiveIntegerField(default=0)  # Number of copies available
    
    #cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)  # Cover image

    def __str__(self):
        return self.title



class Member(models.Model):
    name = models.CharField(max_length=255)  # Full name of the member
    email = models.EmailField(unique=True)  # Email address
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # Contact number
    address = models.TextField(blank=True, null=True)  # Physical address
    membership_date = models.DateField(auto_now_add=True)  # Date of joining
    outstanding_debt = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Debt owed
    is_active = models.BooleanField(default=True)  # Active status of the member

    def __str__(self):
        return self.name


class Transaction(models.Model):
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    member = models.ForeignKey('Member', on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True)  # Date book was issued
    return_date = models.DateField(blank=True, null=True)  # Date book was returned
    fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Total fee charged
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Amount paid by member

    def __str__(self):
        return f"{self.book.title} issued to {self.member.name}"