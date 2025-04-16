from django.test import TestCase
from django.urls import reverse, resolve
from base.views import (
    dashboard, general_search, book_list, create_book, update_book, delete_book,
    fetch_book_details, fetch_all_books, book_details, member_list, add_or_edit_member,
    delete_member, fetch_member_details, fetch_all_members, member_details,
    transaction_list, issue_book, return_book, pay_debt, librarian_list,
    add_or_edit_librarian, get_librarian_details, delete_librarian, user_login, user_logout
)

class URLTests(TestCase):
    """Tests for URL patterns."""
    def test_dashboard_url(self):
        """Test dashboard URL resolves."""
        url = reverse('dashboard')
        self.assertEqual(url, '/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, dashboard)
        self.assertEqual(resolver.url_name, 'dashboard')

    def test_general_search_url(self):
        """Test general_search URL resolves."""
        url = reverse('general_search')
        self.assertEqual(url, '/general-search/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, general_search)
        self.assertEqual(resolver.url_name, 'general_search')

    def test_book_list_url(self):
        """Test book_list URL resolves."""
        url = reverse('book_list')
        self.assertEqual(url, '/books/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, book_list)
        self.assertEqual(resolver.url_name, 'book_list')

    def test_create_book_url(self):
        """Test create_book URL resolves."""
        url = reverse('create_book')
        self.assertEqual(url, '/books/create/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, create_book)
        self.assertEqual(resolver.url_name, 'create_book')

    def test_update_book_url(self):
        """Test update_book URL resolves with book_id."""
        url = reverse('update_book', args=[1])
        self.assertEqual(url, '/books/update/1/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, update_book)
        self.assertEqual(resolver.url_name, 'update_book')
        self.assertEqual(resolver.kwargs['book_id'], 1)

    def test_delete_book_url(self):
        """Test delete_book URL resolves with book_id."""
        url = reverse('delete_book', args=[1])
        self.assertEqual(url, '/books/delete/1/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, delete_book)
        self.assertEqual(resolver.url_name, 'delete_book')
        self.assertEqual(resolver.kwargs['book_id'], 1)

    def test_fetch_book_details_url(self):
        """Test fetch_book_details URL resolves with book_id."""
        url = reverse('fetch_book_details', args=[1])
        self.assertEqual(url, '/books/1/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, fetch_book_details)
        self.assertEqual(resolver.url_name, 'fetch_book_details')
        self.assertEqual(resolver.kwargs['book_id'], 1)

    def test_fetch_all_books_url(self):
        """Test fetch_all_books URL resolves."""
        url = reverse('fetch_all_books')
        self.assertEqual(url, '/books-details/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, fetch_all_books)
        self.assertEqual(resolver.url_name, 'fetch_all_books')

    def test_book_details_url(self):
        """Test book_details URL resolves with book_id."""
        url = reverse('book_details', args=[1])
        self.assertEqual(url, '/book/1/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, book_details)
        self.assertEqual(resolver.url_name, 'book_details')
        self.assertEqual(resolver.kwargs['book_id'], 1)

    def test_member_list_url(self):
        """Test member_list URL resolves."""
        url = reverse('member_list')
        self.assertEqual(url, '/members/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, member_list)
        self.assertEqual(resolver.url_name, 'member_list')

    def test_add_or_edit_member_url(self):
        """Test add_or_edit_member URL resolves."""
        url = reverse('add_or_edit_member')
        self.assertEqual(url, '/members/add-edit/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, add_or_edit_member)
        self.assertEqual(resolver.url_name, 'add_or_edit_member')

    def test_delete_member_url(self):
        """Test delete_member URL resolves with member_id."""
        url = reverse('delete_member', args=[1])
        self.assertEqual(url, '/members/delete/1/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, delete_member)
        self.assertEqual(resolver.url_name, 'delete_member')
        self.assertEqual(resolver.kwargs['member_id'], 1)

    def test_fetch_member_details_url(self):
        """Test fetch_member_details URL resolves with member_id."""
        url = reverse('fetch_member_details', args=[1])
        self.assertEqual(url, '/members/1/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, fetch_member_details)
        self.assertEqual(resolver.url_name, 'fetch_member_details')
        self.assertEqual(resolver.kwargs['member_id'], 1)

    def test_fetch_all_members_url(self):
        """Test fetch_all_members URL resolves."""
        url = reverse('fetch_all_members')
        self.assertEqual(url, '/members-details/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, fetch_all_members)
        self.assertEqual(resolver.url_name, 'fetch_all_members')

    def test_member_details_url(self):
        """Test member_details URL resolves with member_id."""
        url = reverse('member_details', args=[1])
        self.assertEqual(url, '/member/1/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, member_details)
        self.assertEqual(resolver.url_name, 'member_details')
        self.assertEqual(resolver.kwargs['member_id'], 1)

    def test_transaction_list_url(self):
        """Test transaction_list URL resolves."""
        url = reverse('transaction_list')
        self.assertEqual(url, '/transactions/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, transaction_list)
        self.assertEqual(resolver.url_name, 'transaction_list')

    def test_issue_book_url(self):
        """Test issue_book URL resolves."""
        url = reverse('issue_book')
        self.assertEqual(url, '/transactions/issue/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, issue_book)
        self.assertEqual(resolver.url_name, 'issue_book')

    def test_return_book_url(self):
        """Test return_book URL resolves."""
        url = reverse('return_book')
        self.assertEqual(url, '/transactions/return/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, return_book)
        self.assertEqual(resolver.url_name, 'return_book')

    def test_pay_debt_url(self):
        """Test pay_debt URL resolves."""
        url = reverse('pay_debt')
        self.assertEqual(url, '/pay-debt/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, pay_debt)
        self.assertEqual(resolver.url_name, 'pay_debt')

    def test_librarian_list_url(self):
        """Test librarian_list URL resolves."""
        url = reverse('librarian_list')
        self.assertEqual(url, '/librarians/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, librarian_list)
        self.assertEqual(resolver.url_name, 'librarian_list')

    def test_add_or_edit_librarian_url(self):
        """Test add_or_edit_librarian URL resolves."""
        url = reverse('add_or_edit_librarian')
        self.assertEqual(url, '/librarians/add-or-edit/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, add_or_edit_librarian)
        self.assertEqual(resolver.url_name, 'add_or_edit_librarian')

    def test_get_librarian_details_url(self):
        """Test get_librarian_details URL resolves with pk."""
        url = reverse('get_librarian_details', args=[1])
        self.assertEqual(url, '/librarians/get/1/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, get_librarian_details)
        self.assertEqual(resolver.url_name, 'get_librarian_details')
        self.assertEqual(resolver.kwargs['pk'], 1)

    def test_delete_librarian_url(self):
        """Test delete_librarian URL resolves with pk."""
        url = reverse('delete_librarian', args=[1])
        self.assertEqual(url, '/librarians/delete/1/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, delete_librarian)
        self.assertEqual(resolver.url_name, 'delete_librarian')
        self.assertEqual(resolver.kwargs['pk'], 1)

    def test_user_login_url(self):
        """Test user_login URL resolves."""
        url = reverse('user_login')
        self.assertEqual(url, '/login/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, user_login)
        self.assertEqual(resolver.url_name, 'user_login')

    def test_user_logout_url(self):
        """Test user_logout URL resolves."""
        url = reverse('user_logout')
        self.assertEqual(url, '/logout/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, user_logout)
        self.assertEqual(resolver.url_name, 'user_logout')
