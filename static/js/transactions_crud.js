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
// Function to fetch transactions with search functionality
function fetchTransactions(page = 1, member_id = '', book_id = '') {
    // Get the current search type and query
    const searchType = $('.transaction-search-type-options li.selected').data('value');
    const searchQuery = $('#transaction-search-query').val();
    $.ajax({
        url: '/transactions/',
        method: 'GET',
        data: {
            page: page,
            member_id: member_id,
            book_id: book_id,
            search_type: searchType,
            search_query: searchQuery
        },
        success: function (response) {
            $('#transactions-table-body').empty();
            response.transactions.forEach(function (t) {
                let dropdownAction = '';
                if (t.return_date === '-') {
                    dropdownAction = `
                        <li><a class="dropdown-item return-btn" href="#" data-id="${t.id}">Return</a></li>
                    `;
                } else if (t.balance > 0) {
                    dropdownAction = `
                        <li><a class="dropdown-item pay-debt-btn" href="#" data-id="${t.id}" data-balance="${t.balance}">Pay Debt</a></li>
                    `;
                } else {
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
                        <td><!-- Dropdown Menu --><div class="dropdown"><button class="action-dropdown-btn" type="button" id="transactionActionsDropdown-${t.id}" data-bs-toggle="dropdown" aria-expanded="false"><i class="fas fa-ellipsis-h"></i></button><ul class="dropdown-menu" aria-labelledby="transactionActionsDropdown-${t.id}">
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
// Listen for changes in the search input
$('#transaction-search-query').on('input', function () {
    currentPage = 1; // Reset to the first page when searching
    fetchTransactions(currentPage);
});
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
            $('#issueBookModal').modal('show');
        },
    });
});

    // Handle issue book form submission
    $('#issue-book-form').on('submit', function (e) {
        e.preventDefault(); 
        $('#book-id-option, #member-id-option').prop('disabled', false);
        const formData = $(this).serialize();
        // Re-disable fields if necessary (optional, based on UI needs)
        if ($('#book-id-option').data('was-disabled')) {
            $('#book-id-option').prop('disabled', true);        }
        if ($('#member-id-option').data('was-disabled')) {
            $('#member-id-option').prop('disabled', true);
        }
        const issueBookurl = $("#issue-book-form").data('url')
        $('#issue-book-spinner').removeClass('d-none');
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
            complete: function () {
                  $('#issue-book-spinner').addClass('d-none');
              }
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
        $('#return-book-spinner').removeClass('d-none');
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
                     $('#return-book-spinner').addClass('d-none');
                    $('#returnBookModal').modal('hide');
                    showErrorModal(response.message);
                }
            },
            complete: function () {
                  $('#return-book-spinner').addClass('d-none');
              }
        });
    });

    $(document).on('click', '#submitPaymentBtn', function () {
    const transactionId = $('#transactionId').val();
    const paymentAmount = $('#paymentAmount').val();
    $('#pay-debt-spinner').removeClass('d-none');
    $.ajax({
        url: '/pay-debt/', 
        method: 'POST',
        data: {
            transaction_id: transactionId,
            payment_amount: paymentAmount,
        },
        success: function (response) {
            if (response.success) {
                $('#payDebtModal').modal('hide');
                fetchTransactions(currentPage, memberId, bookId);
                showSuccessModal(response.message);                            
            } else {
                 $('#return-book-spinner').addClass('d-none');
                $('#payDebtModal').modal('hide');
                showErrorModal(response.message);
            }
        },
        error: function () {
             $('#return-book-spinner').addClass('d-none');
            $('#payDebtModal').modal('hide');
            showErrorModal('An error occurred while processing the payment.');
        },
        complete: function () {
              // Hide spinner and re-enable login button
              $('#return-book-spinner').addClass('d-none');
          }
    });
});
 function updateTransactionsPagination(pagination, currentPage) {
    const queryParams = getQueryParams(); // Get existing query parameters
    const paginationControls = $('#transactions-pagination-controls');
    paginationControls.empty();
    if (pagination.has_previous) {
        const prevPage = pagination.previous_page_number;
        paginationControls.append(`<button class="page-btn transaction-page-btn" data-page="${prevPage}">Previous</button>`);
    }
    paginationControls.append(`<span>Page ${pagination.current_page} of ${pagination.total_pages}</span>`);
    if (pagination.has_next) {
        const nextPage = pagination.next_page_number;
        paginationControls.append(`<button class="page-btn transaction-page-btn" data-page="${nextPage}">Next</button>`);
    }
}
// Handle pagination button clicks
$(document).on('click', '.transaction-page-btn', function() {
    const newPage = $(this).data('page');
    queryParams.page = newPage; 
    currentPage = newPage; 
    const queryString = new URLSearchParams(queryParams).toString()
  
    fetchTransactions(newPage, memberId, bookId);
    history.pushState(null, '', '?' + queryString);
});   
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
    $('#payDebtModal').modal('show');
});


// Toggle Dropdown Options
$(document).on('click', '.transaction-search-type-btn', function (e) {
  e.stopPropagation(); // Prevent closing when clicking the button
  $('.transaction-search-type-options').toggleClass('active');
});

// Handle Dropdown Option Selection
$(document).on('click', '.transaction-search-type-options li', function (e) {
  e.stopPropagation(); // Prevent closing when clicking an option
  const value = $(this).data('value');
  let displayText = '';
  switch (value) {
    case 'isbn':
      displayText = 'ISBN: ';
      break;
    case 'title':
      displayText = 'Title: ';
      break;
    case 'author':
      displayText = 'Author: ';
      break;
    case 'member':
      displayText = 'Member: ';
      break;
  }
  $('.transaction-search-filter-display').text(displayText);
  $('.transaction-search-type-options li').removeClass('selected');
  $(this).addClass('selected');
  $('.transaction-search-type-options').removeClass('active'); // Close dropdown
});

// Close Dropdown When Clicking Outside
$(document).on('click', function () {
  $('.transaction-search-type-options').removeClass('active');
});

// Initialize Filter Display on Page Load
$(document).ready(function () {
  const selectedOption = $('.transaction-search-type-options li.selected');
  const value = selectedOption.data('value');
  let displayText = '';
  switch (value) {
    case 'isbn':
      displayText = 'ISBN: ';
      break;
    case 'title':
      displayText = 'Title: ';
      break;
    case 'author':
      displayText = 'Author: ';
      break;
    case 'member':
      displayText = 'Member: ';
      break;
  }
  $('.search-filter-display').text(displayText);
});

// Toggle Search Bar on Small Devices
$(document).on('click', '.transactions-header .transaction-search-toggle-btn', function () {
    console.log('click')
  const $transactionsearchBar = $('.transaction-search-bar');
  const $transactiontoggleBtn = $(this);
  console.log($transactionsearchBar, '\n',$transactiontoggleBtn )
  
  $transactionsearchBar.toggleClass('active');
  
  // Toggle magnifying glass icon between search and close
  if ($transactionsearchBar.hasClass('active')) {
    $transactiontoggleBtn.html('<i class="fas fa-times"></i>'); // Show close icon when search bar is visible
  } else {
    $transactiontoggleBtn.html('<i class="fas fa-search"></i>'); // Show search icon when search bar is hidden
  }
});

$(document).on('click', '.transactions-search-bar .transaction-search-type-btn', function (e) {
  e.stopPropagation(); // Prevent event bubbling
  const dropdown = $(this).siblings('.transaction-search-type-options');
  dropdown.addClass('active');
});