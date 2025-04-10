 $(document).ready(function () {

    function getQueryParams() {
    const params = {};
    const queryString = window.location.search.substring(1); // Remove the leading '?'
    queryString.split('&').forEach(pair => {
        const [key, value] = pair.split('=');
        if (key && value) {
            params[decodeURIComponent(key)] = decodeURIComponent(value);
        }
    });
    return params;
}


    let currentPage = 1; // Global variable to track the current page

// Fetch and display transactions
function fetchTransactions(page = 1, member_id = '', book_id = '') {
    $.ajax({
        url: '/transactions/',
        method: 'GET',
        data: { page: page, member_id: member_id, book_id: book_id },
        success: function (response) {
            $('#transactions-table-body').empty();
            response.transactions.forEach(function (t) {
                $('#transactions-table-body').append(`
                    <tr>
                        <td>#${t.id}</td>
                        <td>${t.book_title}</td>
                        <td>${t.member_name}</td>
                        <td>${t.issue_date}</td>
                        <td>${t.return_date}</td>
                        <td>${t.amount_paid}</td>
                        <td>
                            <button class="return-btn" data-id="${t.id}">Return</button>
                        </td>
                    </tr>
                `);
            });
            updatePagination(response.pagination, page);
        },
    });
}

// Initial load
const queryParams = getQueryParams(); // Parse query parameters from the URL
currentPage = parseInt(queryParams.page) || 1; // Use the current page from the URL or default to 1
const memberId = queryParams.member_id || ''; // Use the member_id filter if present
const bookId = queryParams.book_id || ''; // Use the book_id filter if present

// Fetch transactions with the parsed query parameters
fetchTransactions(currentPage, memberId, bookId);

    // Handle "Issue Book" button click
    $('.issue-book-btn').on('click', function () {
        // Populate book options
        $.ajax({
            url: '/books-details/',
            method: 'GET',
            success: function (response) {
                $('#book-id').empty();
                response.books.forEach(function (book) {
                    $('#book-id').append(`<option value="${book.id}">${book.title}</option>`);
                });
            },
        });

        // Populate member options
        $.ajax({
            url: '/members-details/',
            method: 'GET',
            success: function (response) {
                $('#member-id').empty();
                response.members.forEach(function (member) {
                    $('#member-id').append(`<option value="${member.id}">${member.name}</option>`);
                });
                $('#issueBookModal').modal('show');
            },
        });
    });

    // Handle issue book form submission
    $('#issue-book-form').on('submit', function (e) {
        e.preventDefault();
        const formData = $(this).serialize();
        $.ajax({
            url: '/transactions/issue/',
            method: 'POST',
            data: formData,
            success: function (response) {
                if (response.success) {
                    $('#issueBookModal').modal('hide');
                    fetchTransactions(currentPage, memberId, bookId);
                } else {
                    alert(response.message);
                }
            },
        });
    });

    // Handle "Return Book" button click
    $(document).on('click', '.return-btn', function () {
        const transactionId = $(this).data('id');
        $('#transaction-id').val(transactionId);
        $('#returnBookModal').modal('show');
    });

    // Handle return book form submission
    $('#return-book-form').on('submit', function (e) {
        e.preventDefault();
        const formData = $(this).serialize();
        $.ajax({
            url: '/transactions/return/',
            method: 'POST',
            data: formData,
            success: function (response) {
                if (response.success) {
                    $('#returnBookModal').modal('hide');
                    fetchTransactions(currentPage, memberId, bookId);
                    alert(`Book returned successfully.\nTotal Fee: KES ${response.total_fee}\nAmount Paid: KES ${response.amount_paid}\nRemaining Fee: KES ${response.remaining_fee}`);
                } else {
                    alert(response.message);
                }
            },
        });
    });

   function updatePagination(pagination, currentPage) {
    const queryParams = getQueryParams(); // Get existing query parameters
    const paginationControls = $('#pagination-controls');
    paginationControls.empty();

    // Add "Previous" button
    if (pagination.has_previous) {
        const prevPage = pagination.previous_page_number;
        paginationControls.append(`
            <button class="page-btn" data-page="${prevPage}">
                Previous
            </button>
        `);
    }

    // Add current page indicator
    paginationControls.append(`<span>Page ${pagination.current_page} of ${pagination.total_pages}</span>`);

    // Add "Next" button
    if (pagination.has_next) {
        const nextPage = pagination.next_page_number;
        paginationControls.append(`
            <button class="page-btn" data-page="${nextPage}">
                Next
            </button>
        `);
    }

    // Handle pagination button clicks
    $('.page-btn').on('click', function () {
        const newPage = $(this).data('page');
        queryParams.page = newPage; // Update the page in query parameters
        const queryString = new URLSearchParams(queryParams).toString(); // Convert to query string
        window.location.search = queryString; // Update the URL
    });
}
    // Open Return Book Modal
    $('.return-book-btn').on('click', function () {
        $('#returnBookModal').modal('show');
    });
});