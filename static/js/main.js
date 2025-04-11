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