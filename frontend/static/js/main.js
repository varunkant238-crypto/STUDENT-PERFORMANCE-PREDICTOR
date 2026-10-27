/**
 * Student Performance Predictor - Frontend Interactivity
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Auto dismiss bootstrap alert messages after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    // 2. Interactive Chart rendering for Graphs and Dashboard
    initAnalyticsCharts();
});

function initAnalyticsCharts() {
    const pieCanvas = document.getElementById('passFailPieChart');
    const barCanvas = document.getElementById('categoryBarChart');

    if (!pieCanvas && !barCanvas) return;

    fetch('/api/analytics-data')
        .then(response => response.json())
        .then(data => {
            // Render Pass/Fail Chart
            if (pieCanvas && data.pass_fail) {
                new Chart(pieCanvas, {
                    type: 'doughnut',
                    data: {
                        labels: ['Pass (>= 60 Marks)', 'Fail (< 60 Marks)'],
                        datasets: [{
                            data: [data.pass_fail.Pass || 0, data.pass_fail.Fail || 0],
                            backgroundColor: ['#10b981', '#ef4444'],
                            borderWidth: 2,
                            borderColor: '#ffffff'
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { position: 'bottom' }
                        }
                    }
                });
            }

            // Render Categories Chart
            if (barCanvas && data.categories) {
                const labels = Object.keys(data.categories);
                const counts = Object.values(data.categories);

                new Chart(barCanvas, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Student Submissions',
                            data: counts,
                            backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'],
                            borderRadius: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { display: false }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: { stepSize: 1 }
                            }
                        }
                    }
                });
            }
        })
        .catch(err => console.log('Analytics data fetch note:', err));
}
