from django.urls import path
from . import views

urlpatterns = [
    path('books/', views.book_list, name='book_list'),
    path('books/create/', views.create_book, name='create_book'),
    path('books/update/<int:book_id>/', views.update_book, name='update_book'),
    path('books/delete/<int:book_id>/', views.delete_book, name='delete_book'),
    path('books/<int:book_id>/', views.fetch_book_details, name='fetch_book_details'),
    path('books-details/', views.fetch_all_books, name='fetch_all_books'),

    path('book/<int:book_id>/', views.book_details, name='book_details'),


    path('members/', views.member_list, name='member_list'),
    path('members/add-edit/', views.add_or_edit_member, name='add_or_edit_member'),
    path('members/delete/<int:member_id>/', views.delete_member, name='delete_member'),
    path('members/<int:member_id>/', views.fetch_member_details, name='fetch_member_details'),
    path('members-details/', views.fetch_all_members, name='fetch_all_members'),
    path('member/<int:member_id>/', views.member_details, name='member_details'),



    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/issue/', views.issue_book, name='issue_book'),
    path('transactions/return/', views.return_book, name='return_book'),

 
    ]