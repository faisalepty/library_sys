 // Retrieve the serialized JSON data
  const checkoutStatsMonths = JSON.parse(document.getElementById('checkout-stats-months').textContent);
  const checkoutStatsBorrowed = JSON.parse(document.getElementById('checkout-stats-borrowed').textContent);
  const checkoutStatsReturned = JSON.parse(document.getElementById('checkout-stats-returned').textContent);

  // Initialize the chart
  const ctx = document.getElementById('checkoutChart').getContext('2d');
  const checkoutChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: checkoutStatsMonths, // Months passed from the backend
      datasets: [
        {
          label: 'Borrowed',
          data: checkoutStatsBorrowed, // Borrowed counts passed from the backend
          borderColor: '#28a745',
          borderWidth: 2,
          fill: false,
        },
        {
          label: 'Returned',
          data: checkoutStatsReturned, // Returned counts passed from the backend
          borderColor: '#dc3545',
          borderWidth: 2,
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'top',
        },
      },
      scales: {
        x: {
          beginAtZero: true,
        },
        y: {
          beginAtZero: true,
        },
      },
    },
  });
