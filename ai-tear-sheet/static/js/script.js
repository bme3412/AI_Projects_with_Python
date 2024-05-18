let chart; // This will hold the chart instance
const symbol = '{{ company.get("symbol", "AAPL") }}'; // Default to 'AAPL' if not specified

function fetchPriceData(symbol, period) {
  return fetch(`/price-data/${symbol}`)
    .then(response => response.json())
    .then(data => data[period]);
}

function updateChart(period) {
  const symbol = new URLSearchParams(window.location.search).get('symbol') || 'AAPL';

  fetchPriceData(symbol, period)
    .then(data => {
      const timestamps = data.timestamps.map(timestamp => new Date(timestamp));
      const prices = data.prices;

      const ctx = document.getElementById('priceChart').getContext('2d');
      if (chart) {
        chart.destroy();
      }
      chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: timestamps,
          datasets: [{
            label: 'Price',
            data: prices,
            borderColor: 'rgba(75, 192, 192, 1)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderWidth: 1,
            pointRadius: 0,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              type: 'time',
              time: {
                unit: getTimeUnit(period),
                displayFormats: {
                  minute: 'MMM d, HH:mm',
                  hour: 'MMM d, HH:mm',
                  day: 'MMM d',
                  week: 'MMM d',
                  month: 'MMM yyyy',
                  year: 'yyyy'
                }
              },
              ticks: {
                source: 'auto'
              }
            },
            y: {
              beginAtZero: false
            }
          }
        }
      });
    })
    .catch(error => {
      console.error('Error fetching price data:', error);
    });
}

function getTimeUnit(period) {
  switch (period) {
    case '1d':
      return 'minute';
    case '5d':
      return 'hour';
    case '1mo':
    case '3mo':
    case '6mo':
      return 'day';
    case '1y':
      return 'week';
    case '3y':
    case '5y':
      return 'month';
    case '10y':
    case 'max':
      return 'year';
    default:
      return 'day';
  }
}

// Initial chart render
updateChart('1d');

// Event listeners for time period buttons
const timePeriodButtons = document.querySelectorAll('.chart-labels button');
timePeriodButtons.forEach(button => {
  button.addEventListener('click', () => {
    const period = button.getAttribute('data-period');
    updateChart(period);
  });
});