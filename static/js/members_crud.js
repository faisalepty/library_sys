$(document).ready(function () {
    let currentPage = 1; // Global variable to track the current page

    // Fetch and display members
    function fetchMembers(page = 1, search = '') {
        $.ajax({
            url: '/members/',
            method: 'GET',
            data: { page: page, search: search },
            success: function (response) {
                // Clear existing rows
                $('#members-table-body').empty();

                // Populate table with new rows
                response.members.forEach(function (member) {
                    $('#members-table-body').append(`
                        <tr>
                            <td>#${member.id}</td>
                            <td>${member.name}</td>
                            <td>${member.email}</td>
                            <td>${member.phone_number || '-'}</td>
                            <td>${member.outstanding_debt}</td>
                            <td>${member.is_active ? 'Active' : 'Inactive'}</td>
                            <td>
                                <!-- Dropdown Menu -->
                                <div class="dropdown">
                                    <button class="action-dropdown-btn" type="button" id="memberActionsDropdown-${member.id}" data-bs-toggle="dropdown" aria-expanded="false">
                                        ...
                                    </button>
                                    <ul class="dropdown-menu" aria-labelledby="memberActionsDropdown-${member.id}">
                                        <li><a class="dropdown-item " href="/member/${member.id}/">View details</a></li>
                                        <li><a class="dropdown-item issue-book-link" href="#" data-id="${member.id}" data-type="member">Issue Book</a></li>
                                        <li><a class="dropdown-item edit-member-action" href="#" data-id="${member.id}">Edit</a></li>
                                        <li><a class="dropdown-item delete-member-action" href="#" data-id="${member.id}">Delete</a></li>
                                    </ul>
                                </div>
                            </td>
                        </tr>
                    `);
                });

                // Update pagination controls
                updateMemberPagination(response.pagination, page);
            },
            error: function () {
                alert('Error fetching members.');
            },
        });
    }

    // Initial load
    fetchMembers();

    // Handle search input
    $('#search-members').on('input', function () {
        const searchQuery = $(this).val();
        fetchMembers(1, searchQuery); // Reset to page 1 when searching
    });

    // Handle "Add Member" button click
    $('.add-member-btn').on('click', function () {
        $('#member-id').val('');
        $('#name').val('');
        $('#email').val('');
        $('#phone_number').val('');
        $('#address').val('');
        $('#outstanding_debt').val('');
        $('#addEditMemberModal').modal('show');
    });

    // Handle "Edit Member" button click
    $(document).on('click', '.edit-member-action', function () {
        const memberId = $(this).data('id');
        $.ajax({
            url: `/members/${memberId}/`,
            method: 'GET',
            success: function (response) {
                $('#member-id').val(response.id);
                $('#name').val(response.name);
                $('#email').val(response.email);
                $('#phone_number').val(response.phone_number);
                $('#address').val(response.address);
                $('#outstanding_debt').val(response.outstanding_debt);
                $('#addEditMemberModal').modal('show');
            },
            error: function () {
                showErrorModal('Error fetching member details.');
            },
        });
    });

    // Handle form submission
    $('#member-form').on('submit', function (e) {
        e.preventDefault();
        const formData = $(this).serialize();
        $.ajax({
            url: '/members/add-edit/',
            method: 'POST',
            data: formData,
            success: function (response) {
                if (response.success) {
                    $('#addEditMemberModal').modal('hide');
                    fetchMembers(currentPage);
                    $('#addEditMemberModal').modal('hide'); 
                    showSuccessModal(response.message);
                } else {
                    $('#addEditMemberModal').modal('hide');
                    showErrorModal(response.message);
                }
            },
            error: function () {
                $('#addEditMemberModal').modal('hide');
                showErrorModal('Error saving member.');
            },
        });
    });

    // Handle "Delete Member" button click
    $(document).on('click', '.delete-member-action', function () {
        const memberId = $(this).data('id');
        if (confirm('Are you sure you want to delete this member?')) {
            $.ajax({
                url: `/members/delete/${memberId}/`,
                method: 'POST',
                success: function (response) {
                    if (response.success) {
                        fetchMembers(currentPage);
                        showSuccessModal(response.message);
                    } else {
                        showErrorModal(response.message);
                    }
                },
                error: function () {
                    showErrorModal('Error deleting member.');
                },
            });
        }
    });

    // Update pagination controls
 function updateMemberPagination(pagination, currentPage) {
    const paginationControls = $('#members-pagination-controls'); // Unique ID
    paginationControls.empty();
    if (pagination.has_previous) {
        paginationControls.append(`
            <button class="page-btn member-page-btn" data-page="${pagination.previous_page_number}">Previous</button>
        `);
    }
    paginationControls.append(`<span>Page ${pagination.current_page} of ${pagination.total_pages}</span>`);
    if (pagination.has_next) {
        paginationControls.append(`
            <button class="page-btn member-page-btn" data-page="${pagination.next_page_number}">Next</button>
        `);
    }
}


    // Handle pagination button clicks
    $(document).on('click', '.member-page-btn', function () {
        currentPage = $(this).data('page'); // Update the current page
        const searchQuery = $('#search-members').val();
        fetchMembers(currentPage, searchQuery);
    });
});