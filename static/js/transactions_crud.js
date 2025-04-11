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
            let dropdownAction = '';
            if (t.return_date === '-') {
                // No return date: show "Return"
                dropdownAction = `
                    <li><a class="dropdown-item return-btn" href="#" data-id="${t.id}">Return</a></li>
                `;
            } else if (t.balance > 0) {
                // Has return date and balance > 0: show "Pay Debt"
                dropdownAction = `
                    <li><a class="dropdown-item pay-debt-btn" href="#" data-id="${t.id}" data-balance="${t.balance}">Pay Debt</a></li>
                `;
            } else {
                // Has return date and balance <= 0: show "No actions required"
                dropdownAction = `
                    <li><a class="dropdown-item disabled" href="#" data-id="${t.id}">No actions required</a></li>
                `;
            }

             $('#transactions-table-body').append(`
                        <tr>
                            <td>#${t.id}</td>
                            <td>${t.book_title}</td>
                            <td>${t.member_name}</td>
                            <td>${t.issue_date}</td>
                            <td>${t.return_date || '-'}</td>
                            <td>${t.amount_paid || '0.00'}</td>
                            <td>${t.balance || '0.00'}</td>
                            <td>
                                <!-- Dropdown Menu -->
                                <div class="dropdown">
                                    <button class="action-dropdown-btn" type="button" id="transactionActionsDropdown-${t.id}" data-bs-toggle="dropdown" aria-expanded="false">
                                        <i class="fas fa-ellipsis-h"></i>
                                    </button>
                                    <ul class="dropdown-menu" aria-labelledby="transactionActionsDropdown-${t.id}">
                                       ${dropdownAction}
                                    </ul>
                                </div>
                            </td>
                        </tr>
                    `);
            });
            updateTransactionsPagination(response.pagination, page);
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
                $('#book-id-option').empty();
                response.books.forEach(function (book) {
                    $('#book-id-option').append(`<option value="${book.id}">${book.title}</option>`);
                });
            },
        });

        // Populate member options
        $.ajax({
            url: '/members-details/',
            method: 'GET',
            success: function (response) {
                $('#member-id-option').empty();
                response.members.forEach(function (member) {
                    $('#member-id-option').append(`<option value="${member.id}">${member.name}</option>`);
                });
                $('#issueBookModal').modal('show');
            },
        });
    });


    // Handle "Issue Book" button click
$(document).on('click', '.issue-book-link', function (e) {
    e.preventDefault(); // Prevent default link behavior

    // Get the selected ID and type from the clicked link
    const selectedId = $(this).data('id'); // ID of the selected book or member
    const selectedType = $(this).data('type'); // Type ('book' or 'member')

    // Populate book options
    $.ajax({
        url: '/books-details/',
        method: 'GET',
        success: function (response) {
            $('#book-id-option').empty(); // Clear the dropdown

            // Populate book options
            response.books.forEach(function (book) {
                $('#book-id-option').append(`<option value="${book.id}">${book.title}</option>`);
                
            });

            // Pre-select the book if applicable
            if (selectedType === 'book' && selectedId) {
                $('#book-id-option').val(selectedId); // Pre-select the book
                $('#book-id-option').prop('disabled', true); // Make the dropdown read-only
                $('#member-id-option').prop('disabled', false); // Ensure member dropdown is editable
               
            }
        },
    });

    // Populate member options
    $.ajax({
        url: '/members-details/',
        method: 'GET',
        success: function (response) {
            $('#member-id-option').empty(); // Clear the dropdown

            // Populate member options
            response.members.forEach(function (member) {
                $('#member-id-option').append(`<option value="${member.id}">${member.name}</option>`);
            });

            // Pre-select the member if applicable
            if (selectedType === 'member' && selectedId) {
                $('#member-id-option').val(selectedId); // Pre-select the member
                $('#member-id-option').prop('disabled', true); // Make the dropdown read-only
                $('#book-id-option').prop('disabled', false); // Ensure book dropdown is editable
            }

            // Show the modal after both dropdowns are populated
            $('#issueBookModal').modal('show');
        },
    });
});

    // Handle issue book form submission
    $('#issue-book-form').on('submit', function (e) {
        e.preventDefault();
        // Temporarily enable disabled fields
        $('#book-id-option, #member-id-option').prop('disabled', false);

        // Serialize the form data
        const formData = $(this).serialize();

        // Re-disable fields if necessary (optional, based on UI needs)
        if ($('#book-id-option').data('was-disabled')) {
            $('#book-id-option').prop('disabled', true);
        }
        if ($('#member-id-option').data('was-disabled')) {
            $('#member-id-option').prop('disabled', true);
        }
        const issueBookurl = $("#issue-book-form").data('url')
        $.ajax({
            url: issueBookurl,
            method: 'POST',
            data: formData,
            success: function (response) {
                if (response.success) {
                    $('#issueBookModal').modal('hide');
                    fetchTransactions(currentPage, memberId, bookId);
                    showSuccessModal(response.message);
                } else {
                    $('#issueBookModal').modal('hide');
                    showErrorModal(response.message);
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
                    showSuccessModal(`Book returned successfully.\nTotal Fee: KES ${response.total_fee}\nAmount Paid: KES ${response.amount_paid}\nRemaining Fee: KES ${response.remaining_fee}`);
                } else {
                    $('#returnBookModal').modal('hide');
                    showErrorModal(response.message);
                }
            },
        });
    });

   function updateTransactionsPagination(pagination, currentPage) {
    const queryParams = getQueryParams(); // Get existing query parameters
    const paginationControls = $('#transactions-pagination-controls');
    paginationControls.empty();

    // Add "Previous" button
    if (pagination.has_previous) {
        const prevPage = pagination.previous_page_number;
        paginationControls.append(`
            <button class="page-btn transaction-page-btn" data-page="${prevPage}">
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
            <button class="page-btn transaction-page-btn" data-page="${nextPage}">
                Next
            </button>
        `);
    }

    // Handle pagination button clicks
    $('.transaction-page-btn').on('click', function () {
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


$(document).on('click', '.pay-debt-btn', function () {
    const transactionId = $(this).data('id');
    const balance = $(this).data('balance');

    // Populate the modal with transaction details
    $('#transactionId').val(transactionId);
    $('#remainingBalance').text(balance);

    // Show the modal
    $('#payDebtModal').modal('show');
});

$(document).on('click', '#submitPaymentBtn', function () {
    const transactionId = $('#transactionId').val();
    const paymentAmount = $('#paymentAmount').val();
    $.ajax({
        url: '/pay-debt/',  // URL to the pay_debt view
        method: 'POST',
        data: {
            transaction_id: transactionId,
            payment_amount: paymentAmount,
        },
        success: function (response) {
            if (response.success) {
                $('#payDebtModal').modal('hide');
                showSuccessModal(response.message);
                location.reload();  // Reload the page to reflect changes
            } else {
                $('#payDebtModal').modal('hide');
                showErrorModal(response.message);
            }
        },
        error: function () {
            $('#payDebtModal').modal('hide');
            showErrorModal('An error occurred while processing the payment.');
        }
    });
});