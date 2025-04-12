    // script.js
document.addEventListener("DOMContentLoaded", () => {
  const searchToggle = document.querySelector(".search-toggle");
  const closeSearch = document.querySelector(".close-search");
  const searchForm = document.querySelector(".search-form");
  const navbarLogo = document.querySelector(".navbar-logo");
  const navbarRight = document.querySelector(".navbar-right");
  const sidebar = document.querySelector(".sidebar");

  // Toggle search bar on mobile
  searchToggle.addEventListener("click", (e) => {
    e.preventDefault();
    searchForm.classList.toggle("d-none");
    navbarLogo.classList.toggle("d-none");
    navbarRight.classList.toggle("d-none");
  });

  // Close search bar on mobile
  closeSearch.addEventListener("click", () => {
    searchForm.classList.add("d-none");
    navbarLogo.classList.remove("d-none");
    navbarRight.classList.remove("d-none");
  });

  // Toggle sidebar on mobile (for now, we'll trigger this manually; you can add a hamburger icon later)
  window.toggleSidebar = () => {
    sidebar.classList.toggle("active");
  };
});



// function to get the CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Check if the cookie name matches
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Use the CSRF token in all AJAX requests
$(document).ready(function () {
    const csrftoken = getCookie('csrftoken'); // Get CSRF token

    // Set up AJAX headers
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

});

// Function to show the Success Modal
function showSuccessModal(message, duration = 3000) {
    $('#successModalBody').text(message); // Set the success message
    $('#successModal').modal('show'); // Show the modal

    // Automatically hide the modal after the specified duration
    setTimeout(function () {
        $('#successModal').modal('hide'); // Hide the modal
    }, duration);
}

// Function to show the Error Modal
function showErrorModal(message, duration = 3000) {
    $('#errorModalBody').text(message); // Set the error message
    $('#errorModal').modal('show'); // Show the modal

    // Automatically hide the modal after the specified duration
    setTimeout(function () {
        $('#errorModal').modal('hide'); // Hide the modal
    }, duration);
}

// Toggle Search Bar on Small Devices
$(document).on('click', '.search-toggle-btn', function () {
  const $searchBar = $('.transaction-search-bar');
  const $toggleBtn = $(this);
  
  $searchBar.toggleClass('active');
  
  // Toggle magnifying glass icon between search and close
  if ($searchBar.hasClass('active')) {
    $toggleBtn.html('<i class="fas fa-times"></i>'); // Show close icon when search bar is visible
  } else {
    $toggleBtn.html('<i class="fas fa-search"></i>'); // Show search icon when search bar is hidden
  }
});



// Function to fetch search results
function fetchSearchResults(searchType, searchQuery) {
  $.ajax({
    url: '/general-search/',
    method: 'GET',
    data: {
      search_type: searchType,
      search_query: searchQuery,
    },
    success: function (results) {
      const resultsDropdown = $('#search-results');
      resultsDropdown.empty();

      if (results.length > 0) {
        // Populate dropdown with results
        results.forEach(function (result) {
          let displayText = '';
          let link = '#';

          if (result.type === 'book') {
            displayText = `${result.title} by ${result.author}`;
            link = `/book/${result.id}/`;
          } else if (result.type === 'member') {
            displayText = `${result.name} (${result.email})`;
            link = `/member/${result.id}/`;
          }

          resultsDropdown.append(`
            <div class="dropdown-item">
              <a href="${link}" style="text-decoration: none; color: inherit;">${displayText}</a>
            </div>
          `);
        });

        // Show the dropdown
        resultsDropdown.removeClass('d-none').addClass('active');
        $('.modern-search-bar').addClass('results-open');
      } else {
        // Hide the dropdown if no results are found
        resultsDropdown.removeClass('active').addClass('d-none');
        $('.modern-search-bar').removeClass('results-open');
      }
    },
    error: function (xhr, status, error) {
      console.error('Error fetching search results:', error);
      alert('An error occurred while searching. Please try again.');
    },
  });
}

// Toggle Filter Dropdown Options
$(document).on('click', '.modern-search-bar .general-search-type-btn', function (e) {
  e.stopPropagation();
  const $dropdown = $(this).siblings('.general-search-type-options');
  $dropdown.toggleClass('active');
});

// Handle Filter Dropdown Option Selection
$(document).on('click', '.modern-search-bar .general-search-type-options li', function (e) {
  e.stopPropagation();
  const value = $(this).data('value');
  let displayText = '';
  switch (value) {
    case 'book_title':
      displayText = 'Book Title: ';
      break;
    case 'book_author':
      displayText = 'Book Author: ';
      break;
    case 'member_name':
      displayText = 'Member Name: ';
      break;
  }
  $(this).closest('.general-search-filter-wrapper').find('.general-search-filter-display').text(displayText);
  $(this).siblings().removeClass('selected');
  $(this).addClass('selected');
  $(this).closest('.general-search-type-options').removeClass('active');
});

// Close Filter Dropdown When Clicking Outside
$(document).on('click', function () {
  $('.modern-search-bar .general-search-type-options').removeClass('active');
});

// Initialize Filter Display on Page Load
$(document).ready(function () {
  const selectedOption = $('.modern-search-bar .general-search-type-options li.selected');
  const value = selectedOption.data('value');
  let displayText = '';
  switch (value) {
    case 'book_title':
      displayText = 'Book Title: ';
      break;
    case 'book_author':
      displayText = 'Book Author: ';
      break;
    case 'member_name':
      displayText = 'Member Name: ';
      break;
  }
  $('.modern-search-bar .general-search-filter-display').text(displayText);
});

// Listen for Changes in the Search Input
let debounceTimer;
$('#search-query').on('input', function () {
  const searchType = $('.modern-search-bar .general-search-type-options li.selected').data('value');
  const searchQuery = $(this).val().trim();

  // Clear previous timeout
  clearTimeout(debounceTimer);

  // Debounce the search input to avoid excessive AJAX calls
  debounceTimer = setTimeout(function () {
    if (searchQuery.length > 2) { // Only trigger search if query is longer than 2 characters
      fetchSearchResults(searchType, searchQuery);
    } else {
      $('#search-results').removeClass('active').addClass('d-none');
      $('.modern-search-bar').removeClass('results-open');
    }
  }, 300); // Wait 300ms before triggering the search
});

// Hide the Dropdown When Clicking Outside
$(document).on('click', function (e) {
  if (!$(e.target).closest('.search-form').length) {
    $('#search-results').removeClass('active').addClass('d-none');
    $('.modern-search-bar').removeClass('results-open');
  }
});

// Close Search Results When Clicking the Close Icon
$(document).on('click', '.modern-search-bar .close-search', function () {
  $('#search-query').val('');
  $('#search-results').removeClass('active').addClass('d-none');
  $('.modern-search-bar').removeClass('results-open');
});

