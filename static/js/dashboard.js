/* ============================================================
   dashboard.js — Chart.js charts for the Dashboard page
   Called only on dashboard.html via <script src="...">
   ============================================================ */

// ── Chart.js global style defaults ───────────────────────────
Chart.defaults.color      = '#7a7f9a';   // axis label colour
Chart.defaults.font.family = 'DM Sans';  // match site font

// Colour palette — one colour per expense category
const COLORS = [
  '#7c6af7',  // purple  (accent)
  '#f76a6a',  // red     (accent2)
  '#4ade80',  // green
  '#fbbf24',  // yellow
  '#38bdf8',  // sky blue
  '#fb923c',  // orange
  '#a78bfa',  // violet
  '#f472b6',  // pink
  '#34d399'   // emerald
];


/* ── 1. Category Doughnut Chart ──────────────────────────────
   Calls GET /api/category-data  →  { labels: [...], values: [...] }
   and renders a doughnut chart showing this month's spending
   split by category.
   ──────────────────────────────────────────────────────────── */
fetch('/api/category-data')
  .then(function(response) {
    return response.json();               // parse JSON from Flask API
  })
  .then(function(data) {

    // If no expenses this month — hide canvas, show text message
    if (data.labels.length === 0) {
      document.getElementById('categoryChart').style.display = 'none';
      document.getElementById('no-category').style.display  = 'block';
      return;
    }

    // Build the doughnut chart
    new Chart(document.getElementById('categoryChart'), {
      type: 'doughnut',
      data: {
        labels: data.labels,
        datasets: [{
          data:            data.values,
          backgroundColor: COLORS.slice(0, data.labels.length),
          borderWidth:     2,
          borderColor:     '#1e2230'       // matches --card colour
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              padding:  16,
              boxWidth: 12,
              font: { size: 12 }
            }
          }
        }
      }
    });

  })
  .catch(function(error) {
    console.error('Category chart error:', error);
  });


/* ── 2. Monthly Trend Bar Chart ──────────────────────────────
   Calls GET /api/monthly-trend  →  { labels: [...], values: [...] }
   and renders a bar chart showing total spending per month
   for the current year.
   ──────────────────────────────────────────────────────────── */
fetch('/api/monthly-trend')
  .then(function(response) {
    return response.json();
  })
  .then(function(data) {

    new Chart(document.getElementById('trendChart'), {
      type: 'bar',
      data: {
        labels: data.labels,
        datasets: [{
          label:           'Total Spent (₹)',
          data:            data.values,
          backgroundColor: 'rgba(124,106,247,0.7)',
          borderColor:     '#7c6af7',
          borderWidth:     1,
          borderRadius:    6             // rounded bar tops
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false }     // label shown in tooltip instead
        },
        scales: {
          x: {
            grid: { color: '#2a2f42' }   // subtle grid lines
          },
          y: {
            grid: { color: '#2a2f42' },
            ticks: {
              // prefix every y-axis tick with ₹
              callback: function(value) { return '₹' + value; }
            }
          }
        }
      }
    });

  })
  .catch(function(error) {
    console.error('Trend chart error:', error);
  });
