from django.db import models

# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=255)  
    author = models.CharField(max_length=255) 
    genre = models.CharField(max_length=100, blank=True, null=True) 
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True) 
    publication_date = models.DateField(blank=True, null=True)  
    description = models.TextField(blank=True, null=True)  
    stock = models.PositiveIntegerField(default=0) 
    
    #cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)

    def __str__(self):
        return self.title



class Member(models.Model):
    name = models.CharField(max_length=255)  
    email = models.EmailField(unique=True) 
    phone_number = models.CharField(max_length=15, blank=True, null=True)  
    address = models.TextField(blank=True, null=True) 
    membership_date = models.DateField(auto_now_add=True)  
    outstanding_debt = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  
     

    def __str__(self):
        return self.name


class Transaction(models.Model):
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    member = models.ForeignKey('Member', on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True) 
    return_date = models.DateField(blank=True, null=True)  
    fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=150) 
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)  
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0) 

    def save(self, *args, **kwargs):
        
        self.balance = self.fee - self.amount_paid
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book.title} issued to {self.member.name}"