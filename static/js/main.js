document.addEventListener("DOMContentLoaded", () => {
  const searchToggle = document.querySelector(".search-toggle");
  const closeSearch = document.querySelector(".close-search");
  const searchForm = document.querySelector(".search-form");
  const navbarLogo = document.querySelector(".navbar-logo");
  const navbarRight = document.querySelector(".navbar-right");
  const sidebar = document.querySelector(".sidebar");

// Toggle search bar 
  searchToggle.addEventListener("click", (e) => {
    e.preventDefault();
    searchForm.classList.toggle("d-none");
    navbarLogo.classList.toggle("d-none");
    navbarRight.classList.toggle("d-none");
  });


  closeSearch.addEventListener("click", () => {
    searchForm.classList.add("d-none");
    navbarLogo.classList.remove("d-none");
    navbarRight.classList.remove("d-none");
  });


  window.toggleSidebar = () => {
    sidebar.classList.toggle("active");
  };
});

// function to get the CSRF token from cookies " will be used in every ajx call"
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$(document).ready(function () {
    const csrftoken = getCookie('csrftoken');

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

});


// show the Success Modal
function showSuccessModal(message) {
    $('#successModalBody').text(message);
    $('#successModal').modal('show'); 

    setTimeout(function () {
        $('#successModal').modal('hide');
    }, 3000);
}


//show the Error Modal
function showErrorModal(message) {
    $('#errorModalBody').text(message); 
    $('#errorModal').modal('show'); 

    setTimeout(function () {
        $('#errorModal').modal('hide');
    }, 3000);
}


// Toggle Search Bar on Small Devices
$(document).on('click', '.search-toggle-btn', function () {
  const $searchBar = $('.transaction-search-bar');
  const $toggleBtn = $(this);
  
  $searchBar.toggleClass('active');
  
  if ($searchBar.hasClass('active')) {
    $toggleBtn.html('<i class="fas fa-times"></i>'); 
  } else {
    $toggleBtn.html('<i class="fas fa-search"></i>'); 
  }
});


// fetch search results and populate in dropdown
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
          resultsDropdown.append(`<div class="dropdown-item"><a href="${link}" style="text-decoration: none; color: inherit;">${displayText}</a></div>`);
        });
       
        resultsDropdown.removeClass('d-none').addClass('active');
        $('.modern-search-bar').addClass('results-open');
        $('.general-search-filter-wrapper').addClass('results-filter-open')
      } else {
        
        resultsDropdown.removeClass('active').addClass('d-none');
        $('.modern-search-bar').removeClass('results-open');
        $('.general-search-filter-wrapper').removeClass('results-filter-open')
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
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(function () {
    if (searchQuery.length > 2) { 
      fetchSearchResults(searchType, searchQuery);
    } else {
      $('#search-results').removeClass('active').addClass('d-none');
      $('.modern-search-bar').removeClass('results-open');
      $('.general-search-filter-wrapper').removeClass('results-filter-open')
    }
  }, 300); 
});


$(document).on('click', function (e) {
  if (!$(e.target).closest('.search-form').length) {
    $('#search-results').removeClass('active').addClass('d-none');
    $('.modern-search-bar').removeClass('results-open');
    $('.general-search-filter-wrapper').removeClass('results-filter-open')

  }
});


$(document).on('click', '.modern-search-bar .close-search', function () {
  $('#search-query').val('');
  $('#search-results').removeClass('active').addClass('d-none');
  $('.modern-search-bar').removeClass('results-open');
  $('.general-search-filter-wrapper').removeClass('results-filter-open')
});


// Login call
$('#login-btn').on('click', function () {
    const username = $('#login-username').val();
    const password = $('#login-password').val();

    $('#login-spinner').removeClass('d-none');
    $('#login-btn').prop('disabled', true);
    $.ajax({
        url: '/login/',
        method: 'POST',
        data: { username: username, password: password },
        success: function (response) {
            if (response.success) {
                window.location.href = response.redirect_url; 
            } else {
              $('#loginModal').modal('hide')
              $('#login-spinner').addClass('d-none');
              showErrorModal(response.message);
            }
        },
        error: function () {
            showErrorModal('An error occurred while logging in.');
        },
       complete: function () {
          
          $('#login-spinner').addClass('d-none');
          $('#login-btn').prop('disabled', false);
      },
    });
});

$(document).on('click', '.logout-btn', function () {
    $('.confirm-modal .modal-body').html('Are you sure you want to log out?');
    $('.confirm-modal .modal-footer .btn-primary').attr('id', 'confirmModalBtn-logout');
    $('.confirm-modal').modal('show')
})


//Logout call
$(document).on('click', '#confirmModalBtn-logout', function (e) {
    e.preventDefault();
        $.ajax({
            url: '/logout/',
            method: 'POST',
            success: function (response) {
                if (response.success) {
                    location.reload();
                } else {
                    showErrorModal(response.message);
                }
            },
            error: function () {
                showErrorModal('An error occurred while logging out.');
            },
        });

});
