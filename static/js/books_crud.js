   $(document).ready(function () {
    // Function to fetch and display books
    function fetchBooks(page = 1, search = '') {
        $.ajax({
            url: '/books/',
            method: 'GET',
            data: {
                page: page,
                search: search,
            },
            success: function (response) {
                // Clear existing rows
                $('#books-table-body').empty();

                // Populate table with new rows
                response.books.forEach(function (book) {
                    $('#books-table-body').append(`
                    <tr>
                        <td>#${book.id}</td>
                        <td>${book.title}</td>
                        <td>${book.author}</td>
                        <td>${book.genre || '-'}</td>
                        <td>${book.stock}</td>
                        <td>
                            <!-- Dropdown Menu -->
                            <div class="dropdown">

                                <button class="action-dropdown-btn" type="button" id="actionsDropdown-${book.id}" data-bs-toggle="dropdown" aria-expanded="false">
                                    ...
                                </button>
                                <ul class="dropdown-menu" aria-labelledby="actionsDropdown-${book.id}">
                                    <li><a class="dropdown-item" href="/book/${book.id}/">View details</a></li>
                                    <li><a class="dropdown-item issue-book-link" href="#" data-id="${book.id}" data-type="book">Issue Book</a></li>
                                    <li><a class="dropdown-item edit-book-action" href="#" data-id="${book.id}">Edit</a></li>
                                    <li><a class="dropdown-item delete-book-action" href="#" data-id="${book.id}">Delete</a></li>
                                </ul>
                            </div>
                        </td>
                    </tr>
                    `);
                });

                // Update pagination controls
                updateBookPagination(response.pagination);
            },
            error: function () {
                alert('Error fetching books.');
            },
        });
    }

    // Initial load
    fetchBooks();

    // Handle search input
    $('#search-books').on('input', function () {
        const searchQuery = $(this).val();
        fetchBooks(1, searchQuery); // Reset to page 1 when searching
    });

    // Function to update pagination controls
  function updateBookPagination(pagination) {
    const paginationControls = $('#books-pagination-controls'); // Unique ID
    paginationControls.empty();
    if (pagination.has_previous) {
        paginationControls.append(`
            <button class="page-btn book-page-btn" data-page="${pagination.previous_page_number}">Previous</button>
        `);
    }
    paginationControls.append(`<span>Page ${pagination.current_page} of ${pagination.total_pages}</span>`);
    if (pagination.has_next) {
        paginationControls.append(`
            <button class="page-btn book-page-btn" data-page="${pagination.next_page_number}">Next</button>
        `);
    }
}


    // Handle pagination button clicks
    $(document).on('click', '.book-page-btn', function () {
        let page = $(this).data('page');
        let searchQuery = $('#search-books').val();
        fetchBooks(page, searchQuery);
    });



// Handle "Add Book" button click
    $('.add-book-btn').on('click', function () {
        $('#book-id').val(''); // Clear ID for new book
        $('#title').val('');
        $('#author').val('');
        $('#genre').val('');
        $('#isbn').val('');
        $('#stock').val('');
        $('#addEditBookModal').modal('show');
    });

    // Handle "Edit Book" button click
    $(document).on('click', '.edit-book-action', function () {
        const bookId = $(this).data('id');

        // Fetch book details using the new endpoint
        $.ajax({
            url: `/books/${bookId}/`,  // Fetch book details by ID
            method: 'GET',
            success: function (response) {
                // Populate the modal fields with the fetched data
                $('#book-id').val(response.id);
                $('#title').val(response.title);
                $('#author').val(response.author);
                $('#genre').val(response.genre);
                $('#isbn').val(response.isbn);
                $('#stock').val(response.stock);

                // Show the modal
                $('#addEditBookModal').modal('show');
            },
            error: function () {
                showErrorModal('Error fetching book details.');
            },
        });
    });

    // Handle form submission
    $('#book-form').on('submit', function (e) {
        e.preventDefault();
        const bookId = $('#book-id').val();
        const url = bookId ? `/books/update/${bookId}/` : '/books/create/';
        const method = bookId ? 'POST' : 'POST';

        $.ajax({
            url: url,
            method: method,
            data: $(this).serialize(),
            success: function (response) {
                if (response.success) {
                    $('#addEditBookModal').modal('hide');
                    let page = $('#page-btn').innerHtml;
                    let searchQuery = $('#search-books').val();
                    fetchBooks(page, searchQuery);
                    $('#addEditBookModal').modal('hide');
                    showSuccessModal(response.message);
                } else {
                    $('#addEditBookModal').modal('hide');
                    showErrorModal(response.message);
                }
            },
        });
    });

let delbookId
$(document).on('click', '.delete-book-action', function () {
    delbookId = $(this).data('id');
    $('.confirm-modal .modal-body').html('Are you sure you want to delete this book?');
    $('.confirm-modal .modal-footer .btn-primary').attr('id', 'confirmModalBtn-book');
    $('.confirm-modal').modal('show')


})
    // Handle "Delete Book" button click
    $(document).on('click', '#confirmModalBtn-book', function () {
            $('.confirm-modal').modal('hide')
            $.ajax({
                url: `/books/delete/${delbookId}/`,
                method: 'POST',
                success: function (response) {
                    if (response.success) {
                        let page = $('#page-btn').innerHtml;
                        let searchQuery = $('#search-books').val();
                        fetchBooks(page, searchQuery);
                        showSuccessModal(response.message);
                    } else {
                        showErrorModal(response.message);
                    }
                },
            });

    });

});