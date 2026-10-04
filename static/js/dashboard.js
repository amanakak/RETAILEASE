/* TrackCart Application JavaScript */

document.addEventListener('DOMContentLoaded', function () {
  // Mobile Sidebar Toggle
  const sidebarToggleBtn = document.getElementById('sidebarToggle');
  const sidebar = document.querySelector('.sidebar');
  const sidebarOverlay = document.getElementById('sidebarOverlay');

  if (sidebarToggleBtn && sidebar) {
    sidebarToggleBtn.addEventListener('click', function () {
      sidebar.classList.toggle('show');
      if (sidebarOverlay) {
        sidebarOverlay.classList.toggle('show');
      }
    });
  }

  if (sidebarOverlay) {
    sidebarOverlay.addEventListener('click', function () {
      sidebar.classList.remove('show');
      sidebarOverlay.classList.remove('show');
    });
  }

  // Password Visibility Toggle
  const togglePasswordBtn = document.getElementById('togglePassword');
  const passwordInput = document.getElementById('passwordInput');

  if (togglePasswordBtn && passwordInput) {
    togglePasswordBtn.addEventListener('click', function () {
      const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
      passwordInput.setAttribute('type', type);
      
      const icon = this.querySelector('i');
      if (icon) {
        if (type === 'text') {
          icon.classList.remove('fa-eye');
          icon.classList.add('fa-eye-slash');
        } else {
          icon.classList.remove('fa-eye-slash');
          icon.classList.add('fa-eye');
        }
      }
    });
  }

  // Global Search Filter Helper
  const globalSearchInput = document.getElementById('globalSearchInput');
  if (globalSearchInput) {
    globalSearchInput.addEventListener('keyup', function (e) {
      if (e.key === 'Enter') {
        const query = this.value.trim();
        if (query) {
          window.location.href = `/products/?search=${encodeURIComponent(query)}`;
        }
      }
    });
  }
});

// Chart Initialization Helper Function
function initSalesChart(canvasId, chartDataRaw) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !chartDataRaw) return;

  let chartData;
  try {
    chartData = typeof chartDataRaw === 'string' ? JSON.parse(chartDataRaw) : chartDataRaw;
  } catch (e) {
    console.error('Failed to parse chart data:', e);
    return;
  }

  const labels = chartData.map(item => {
    // Format date string YYYY-MM-DD to short format like "Sep 22"
    const parts = item.date.split('-');
    if (parts.length === 3) {
      const dateObj = new Date(parts[0], parts[1] - 1, parts[2]);
      return dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
    return item.date;
  });

  const values = chartData.map(item => item.sales || item.total || 0);

  const ctx = canvas.getContext('2d');
  
  // Gradient fill for line chart
  const gradient = ctx.createLinearGradient(0, 0, 0, 300);
  gradient.addColorStop(0, 'rgba(35, 56, 43, 0.25)');
  gradient.addColorStop(1, 'rgba(35, 56, 43, 0.0)');

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Revenue (₹)',
        data: values,
        borderColor: '#23382B',
        borderWidth: 3,
        backgroundColor: gradient,
        fill: true,
        tension: 0.35,
        pointBackgroundColor: '#23382B',
        pointBorderColor: '#FFFFFF',
        pointBorderWidth: 2,
        pointRadius: 5,
        pointHoverRadius: 7
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#151815',
          padding: 12,
          titleFont: { family: 'Plus Jakarta Sans', size: 13, weight: '700' },
          bodyFont: { family: 'Plus Jakarta Sans', size: 13 },
          displayColors: false,
          callbacks: {
            label: function(context) {
              return 'Revenue: ₹' + context.parsed.y.toLocaleString();
            }
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { font: { family: 'Plus Jakarta Sans', size: 12 }, color: '#767A75' }
        },
        y: {
          grid: { color: '#F0F0EC' },
          ticks: {
            font: { family: 'Plus Jakarta Sans', size: 12 },
            color: '#767A75',
            callback: function(value) {
              return '₹' + value;
            }
          }
        }
      }
    }
  });
}

function initCategoryDoughnutChart(canvasId, categoryDataRaw) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !categoryDataRaw) return;

  const labels = categoryDataRaw.map(item => item.product__category__name || 'Other');
  const values = categoryDataRaw.map(item => item.total_revenue || 0);

  if (labels.length === 0) return;

  const ctx = canvas.getContext('2d');
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: ['#23382B', '#536957', '#88C399', '#C07D14', '#151815'],
        borderWidth: 2,
        borderColor: '#FFFFFF'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: { font: { family: 'Plus Jakarta Sans', size: 12 }, boxWidth: 12, padding: 15 }
        }
      },
      cutout: '70%'
    }
  });
}
