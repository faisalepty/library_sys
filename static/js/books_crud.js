$(document).ready(function () {
    // fetch books with search functionality
function fetchBooks(page = 1, searchType = '', searchQuery = '') {
    $.ajax({
        url: '/books/',
        method: 'GET',
        data: {
            page: page,
            search_type: searchType,
            search_query: searchQuery
        },
        success: function (response) {
            $('#books-table-body').empty();
            response.books.forEach(function (book) {
                $('#books-table-body').append(`
                    <tr>
                        <td>#${book.id}</td>
                        <td>${book.title}</td>
                        <td>${book.author}</td>
                        <td>${book.genre || '-'}</td>
                        <td>${book.stock}</td>
                        <td><!-- Dropdown Menu --><div class="dropdown"><button class="action-dropdown-btn" type="button" id="actionsDropdown-${book.id}" data-bs-toggle="dropdown" aria-expanded="false"><i class="fas fa-ellipsis-h"></i></button><ul class="dropdown-menu" aria-labelledby="actionsDropdown-${book.id}"><li><a class="dropdown-item" href="/book/${book.id}/">View details</a></li><li><a class="dropdown-item issue-book-link" href="#" data-id="${book.id}" data-type="book">Issue Book</a></li><li><a class="dropdown-item edit-book-action" href="#" data-id="${book.id}">Edit</a></li><li><a class="dropdown-item delete-book-action" href="#" data-id="${book.id}">Delete</a></li></ul></div>
                        </td>
                    </tr>
                `);
            });
            updateBookPagination(response.pagination, page);
        },
        error: function () {
            alert('Error fetching books.');
        },
    });
}
fetchBooks();

let bookSearchType = $('.books-search-bar .book-search-type-options li.selected').data('value');
let bookSearchQuery = $('#book-search-query').val();
// Listen for changes in the search input
$('#book-search-query').on('input', function () {
    currentPage = 1; 
    const searchType = $('.books-search-bar .book-search-type-options li.selected').data('value');
    const searchQuery = $(this).val();
    fetchBooks(currentPage, searchType, searchQuery);
});

    // update pagination controls
function updateBookPagination(pagination) {
    const paginationControls = $('#books-pagination-controls');
    paginationControls.empty();
    if (pagination.has_previous) {
        paginationControls.append(`
            <button class="page-btn book-page-btn" data-page="${pagination.previous_page_number}">Previous</button>
        `);
    }
    else{
        paginationControls.append(`
            <button class="page-btn book-page-btn" disabled aria-disabled="true">Previous</button>
        `);
    }
    paginationControls.append(`<span>Page ${pagination.current_page} of ${pagination.total_pages}</span>`);
    if (pagination.has_next) {
        paginationControls.append(`
            <button class="page-btn book-page-btn" data-page="${pagination.next_page_number}">Next</button>
        `);
    }
    else{
        paginationControls.append(`
            <button class="page-btn book-page-btn" disabled aria-disabled="true">Next</button>
        `);
    }
}

    // pagination button clicks
$(document).on('click', '.book-page-btn', function () {
        let page = $(this).data('page');
        let searchQuery = $('#search-books').val();
        let bookSearchType = $('.books-search-bar .search-type-options li.selected').data('value');
        let bookSearchQuery = $('#search-query').val();
       
        fetchBooks(page, bookSearchType, bookSearchQuery);
});

// clear input fields on Add Book button click
$('.add-book-btn').on('click', function () {
        $('#book-id').val(''); 
        $('#title').val('');
        $('#author').val('');
        $('#genre').val('');
        $('#isbn').val('');
        $('#stock').val('');
        $('#bookModalTitle').text('Add book')
        $('#addEditBookModal').modal('show');
});
    
// populate form on Edit Book button click
$(document).on('click', '.edit-book-action', function () {
        const bookId = $(this).data('id');
        
        $.ajax({
            url: `/books/${bookId}/`, 
            method: 'GET',
            success: function (response) {
                
                $('#book-id').val(response.id);
                $('#title').val(response.title);
                $('#author').val(response.author);
                $('#genre').val(response.genre);
                $('#isbn').val(response.isbn);
                $('#stock').val(response.stock);
                $('#bookModalTitle').text(`Edit ${response.title} by ${response.author}`)

               
                $('#addEditBookModal').modal('show');
            },
            error: function () {
                showErrorModal('Error fetching book details.');
            },
        });
    });

// submit add/edit book form
$('#book-form').on('submit', function (e) {
        e.preventDefault();
        const bookId = $('#book-id').val();
        const url = bookId ? `/books/update/${bookId}/` : '/books/create/';
        const method = bookId ? 'POST' : 'POST';
         $('#book-spinner').removeClass('d-none');
        $.ajax({
            url: url,
            method: method,
            data: $(this).serialize(),
            success: function (response) {
                if (response.success) {
                    $('#addEditBookModal').modal('hide');
                    let page = $('#page-btn').innerHtml;
                    let searchQuery = $('#search-books').val();
                    let bookSearchType = $('.books-search-bar .search-type-options li.selected').data('value');
                    let bookSearchQuery = $('#search-query').val();
                    fetchBooks(page, bookSearchType, bookSearchQuery);
                    $('#addEditBookModal').modal('hide');
                    showSuccessModal(response.message);
                } else {
                    $('#addEditBookModal').modal('hide');
                    $('#book-spinner').addClass('d-none');
                    showErrorModal(response.message);
                }
            },
            complete: function () {
                  
                  $('#book-spinner').addClass('d-none');
              }
        });
    });

let delbookId
$(document).on('click', '.delete-book-action', function () {
    delbookId = $(this).data('id');
    $('.confirm-modal .modal-body').html('Are you sure you want to delete this book?');
    $('.confirm-modal .modal-footer .btn-primary').attr('id', 'confirmModalBtn-book');
    $('.confirm-modal').modal('show')
})
    // call for delete on Delete Book button click
    $(document).on('click', '#confirmModalBtn-book', function () {
            $('.confirm-modal').modal('hide')
            $.ajax({
                url: `/books/delete/${delbookId}/`,
                method: 'POST',
                success: function (response) {
                    if (response.success) {
                        let page = $('#page-btn').innerHtml;
                        let searchQuery = $('#search-books').val();
                        let bookSearchType = $('.books-search-bar .search-type-options li.selected').data('value');
                        let bookSearchQuery = $('#search-query').val();
                        fetchBooks(page, bookSearchType, bookSearchQuery);
                        showSuccessModal(response.message);
                    } else {
                        showErrorModal(response.message);
                    }
                },
            });
    });

});


// Toggle Search Bar on Small Devices
$(document).on('click', '.books-header .book-search-toggle-btn', function () {
  const $searchBar = $('.books-search-bar');
  const $toggleBtn = $(this);
  
  $searchBar.toggleClass('active');
  
  
  if ($searchBar.hasClass('active')) {
    $toggleBtn.html('<i class="fas fa-times"></i>'); 
    $toggleBtn.html('<i class="fas fa-search"></i>');
  }
});
$(document).on('click', '.books-search-bar .book-search-type-btn', function (e) {
  e.stopPropagation(); 
  const dropdown = $(this).siblings('.book-search-type-options');
  dropdown.toggleClass('active');
});

// Handle Dropdown Option Selection
$(document).on('click', '.books-search-bar .book-search-type-options li', function (e) {
  e.stopPropagation(); 
  const value = $(this).data('value');
  let displayText = '';
  switch (value) {
    case 'title':
      displayText = 'Title: ';
      break;
    case 'author':
      displayText = 'Author: ';
      break;
  }
  $(this).closest('.book-search-filter-wrapper').find('.book-search-filter-display').text(displayText);
  $(this).siblings().removeClass('selected');
  $(this).addClass('selected');
  $(this).closest('.book-search-type-options').removeClass('active'); 
});

// Initialize Filter Display on Page Load
$(document).ready(function () {
  const selectedOption = $('.books-search-bar .book-search-type-options li.selected');
  const value = selectedOption.data('value');
  let displayText = '';
  switch (value) {
    case 'title':
      displayText = 'Title: ';
      break;
    case 'author':
      displayText = 'Author: ';
      break;
  }
  $('.books-search-bar .book-search-filter-display').text(displayText);
});