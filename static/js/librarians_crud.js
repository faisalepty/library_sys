// Fetch librarians and populate the table
function fetchLibrarians(page = 1, search = '') {
    $.ajax({
        url: '/librarians/',
        method: 'GET',
        data: { page: page, search: search },
        success: function (response) {
            $('#librarians-table-body').empty();

            // Populate table rows
            response.librarians.forEach(function (librarian) {
                $('#librarians-table-body').append(`
                    <tr>
                        <td>#${librarian.id}</td>
                        <td>${librarian.username}</td>
                        <td>${librarian.email}</td>
                        <td>${librarian.phone_number || '-'}</td>
                        <td>${librarian.address || '-'}</td>
                        <td>
                            <button class="btn btn-sm btn-primary edit-librarian-btn" data-id="${librarian.id}">
                                Edit
                            </button>
                            <button class="btn btn-sm btn-danger delete-librarian-btn" data-id="${librarian.id}">
                                Delete
                            </button>
                        </td>
                    </tr>
                `);
            });

            // Update pagination controls
            updateLibrarianPagination(response.pagination, page);
        },
        error: function () {
            alert('Error fetching librarians.');
        },
    });
}

// Save Librarian (Add or Edit)
$('#save-librarian-btn').on('click', function () {
    const id = $('#librarian-id').val();
    const url = '/librarians/add-or-edit/';
    const method = 'POST';

    $.ajax({
        url: url,
        method: method,
        data: $('#librarian-form').serialize(),
        success: function (response) {
            if (response.success) {
                fetchLibrarians(); // Refresh the table
                $('#addEditLibrarianModal').modal('hide'); // Close the modal
                resetLibrarianForm(); // Reset the form
            } else {
                alert(response.message);
            }
        },
        error: function () {
            alert('An error occurred while saving the librarian.');
        },
    });
});

// Open the Add Librarian Modal
$('.add-librarian-btn').on('click', function () {
    resetLibrarianForm();
    $('#addEditLibrarianModalLabel').text('Add Librarian');
    $('.optional-fields').show(); // Show all fields for adding
});

// Open the Edit Librarian Modal
$(document).on('click', '.edit-librarian-btn', function () {
    const id = $(this).data('id');

    $.ajax({
        url: `/librarians/get/${id}/`,
        method: 'GET',
        success: function (response) {
            $('#librarian-id').val(response.id);
            $('#librarian-username').val(response.username);
            $('#librarian-email').val(response.email);
            $('#librarian-phone').val(response.phone_number || '');
            $('#librarian-address').val(response.address || '');

            $('#addEditLibrarianModalLabel').text('Edit Librarian');
            $('.optional-fields').hide(); // Hide optional fields for editing
            $('#addEditLibrarianModal').modal('show');
        },
        error: function () {
            alert('Error fetching librarian details.');
        },
    });
});

// Delete a Librarian
$(document).on('click', '.delete-librarian-btn', function () {
    const id = $(this).data('id');

    if (confirm('Are you sure you want to delete this librarian?')) {
        $.ajax({
            url: `/librarians/delete/${id}/`,
            method: 'POST',
            success: function (response) {
                if (response.success) {
                    fetchLibrarians(); // Refresh the table
                } else {
                    alert(response.message);
                }
            },
            error: function () {
                alert('An error occurred while deleting the librarian.');
            },
        });
    }
});

// Reset the Librarian Form
function resetLibrarianForm() {
    $('#librarian-id').val('');
    $('#librarian-username').val('');
    $('#librarian-email').val('');
    $('#librarian-password').val('');
    $('#librarian-phone').val('');
    $('#librarian-address').val('');
    $('.optional-fields').show(); // Ensure all fields are visible after resetting
}

// Update Pagination Controls
function updateLibrarianPagination(pagination, currentPage) {
    const paginationControls = $('#librarians-pagination-controls');
    paginationControls.empty();

    if (pagination.has_previous) {
        paginationControls.append(`
            <a href="#" class="page-link" data-page="${pagination.previous_page_number}">Previous</a>
        `);
    }

    paginationControls.append(`
        <span class="current-page">${pagination.current_page} of ${pagination.total_pages}</span>
    `);

    if (pagination.has_next) {
        paginationControls.append(`
            <a href="#" class="page-link" data-page="${pagination.next_page_number}">Next</a>
        `);
    }

    // Handle pagination link clicks
    $('.page-link').on('click', function (e) {
        e.preventDefault();
        const page = $(this).data('page');
        fetchLibrarians(page);
    });
}

// Search Librarians

$('#search-librarians').on('input', function () {
    const searchQuery = $(this).val().trim();

    clearTimeout(debounceTimer);

    debounceTimer = setTimeout(function () {
        fetchLibrarians(1, searchQuery); // Reset to the first page when searching
    }, 300);
});

// Initial Load
$(document).ready(function () {
    fetchLibrarians();
});