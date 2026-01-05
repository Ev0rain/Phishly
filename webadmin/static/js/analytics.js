/**
 * Analytics Page JavaScript
 * Handles charts, filters, and interactive data visualization
 */

// Chart instances
let timeSeriesChart = null;
let deviceChart = null;
let browserChart = null;

/**
 * Get current theme
 */
function getCurrentTheme() {
    return document.documentElement.getAttribute('data-theme') || 'light';
}

/**
 * Get theme-aware colors for charts
 */
function getChartColors() {
    const isDark = getCurrentTheme() === 'dark';
    return {
        text: isDark ? 'hsl(210, 40%, 98%)' : 'hsl(222.2, 84%, 4.9%)',
        grid: isDark ? 'hsl(217.2, 32.6%, 17.5%)' : 'hsl(214.3, 31.8%, 91.4%)',
        background: isDark ? 'hsl(222.2, 84%, 8%)' : 'white'
    };
}

document.addEventListener('DOMContentLoaded', function () {
    // Initialize charts
    initializeTimeSeriesChart(30); // Default 30 days
    initializeDeviceChart();
    initializeBrowserChart();
    
    // Re-render charts when theme changes
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'attributes' && mutation.attributeName === 'data-theme') {
                // Re-initialize all charts with new theme colors
                if (timeSeriesChart) {
                    const days = 30; // Use current range
                    initializeTimeSeriesChart(days);
                }
                if (deviceChart) initializeDeviceChart();
                if (browserChart) initializeBrowserChart();
            }
        });
    });
    
    observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['data-theme']
    });

    // Filter panel toggle
    const filterBtn = document.getElementById('filterBtn');
    const filterPanel = document.getElementById('filterPanel');

    filterBtn?.addEventListener('click', () => {
        filterPanel.classList.toggle('active');
    });

    // Time range buttons for chart
    const chartButtons = document.querySelectorAll('.chart-btn');
    chartButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            // Remove active class from all buttons
            chartButtons.forEach(b => b.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');

            const days = parseInt(this.getAttribute('data-days'));
            updateTimeSeriesChart(days);
        });
    });

    // Apply filters button
    const applyFiltersBtn = document.getElementById('applyFiltersBtn');
    applyFiltersBtn?.addEventListener('click', applyFilters);

    // Clear filters button
    const clearFiltersBtn = document.getElementById('clearFiltersBtn');
    clearFiltersBtn?.addEventListener('click', clearFilters);

    // Export data button
    const exportBtn = document.getElementById('exportBtn');
    exportBtn?.addEventListener('click', exportData);

    // Refresh button
    const refreshBtn = document.getElementById('refreshBtn');
    refreshBtn?.addEventListener('click', () => {
        location.reload();
    });

    // Refresh events button
    const refreshEventsBtn = document.getElementById('refreshEventsBtn');
    refreshEventsBtn?.addEventListener('click', refreshEvents);

    // Time range select for filters
    const timeRangeSelect = document.getElementById('filterTimeRange');
    timeRangeSelect?.addEventListener('change', function () {
        const days = parseInt(this.value);
        updateTimeSeriesChart(days);
    });
});

/**
 * Initialize time series chart (line chart)
 */
function initializeTimeSeriesChart(days) {
    fetch(`/api/analytics/time-series?days=${days}`)
        .then(response => response.json())
        .then(result => {
            if (!result.success) {
                console.error('Failed to fetch time series data');
                return;
            }

            const data = result.data;
            const ctx = document.getElementById('timeSeriesChart');

            if (!ctx) return;

            // Destroy existing chart if it exists
            if (timeSeriesChart) {
                timeSeriesChart.destroy();
            }
            
            const colors = getChartColors();

            timeSeriesChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.map(d => d.date),
                    datasets: [
                        {
                            label: 'Emails Sent',
                            data: data.map(d => d.emails_sent),
                            borderColor: '#3b82f6',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            tension: 0.4,
                            fill: true,
                        },
                        {
                            label: 'Opened',
                            data: data.map(d => d.emails_opened),
                            borderColor: '#10b981',
                            backgroundColor: 'rgba(16, 185, 129, 0.1)',
                            tension: 0.4,
                            fill: true,
                        },
                        {
                            label: 'Clicked',
                            data: data.map(d => d.links_clicked),
                            borderColor: '#f59e0b',
                            backgroundColor: 'rgba(245, 158, 11, 0.1)',
                            tension: 0.4,
                            fill: true,
                        },
                        {
                            label: 'Submitted',
                            data: data.map(d => d.credentials_submitted),
                            borderColor: '#ef4444',
                            backgroundColor: 'rgba(239, 68, 68, 0.1)',
                            tension: 0.4,
                            fill: true,
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                color: colors.text
                            }
                        },
                        tooltip: {
                            callbacks: {
                                footer: function (tooltipItems) {
                                    const index = tooltipItems[0].dataIndex;
                                    const openRate = data[index].open_rate;
                                    const clickRate = data[index].click_rate;
                                    const submitRate = data[index].submission_rate;
                                    return `Open: ${openRate}% | Click: ${clickRate}% | Submit: ${submitRate}%`;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0,
                                color: colors.text
                            },
                            grid: {
                                color: colors.grid
                            }
                        },
                        x: {
                            ticks: {
                                maxRotation: 45,
                                minRotation: 45,
                                color: colors.text
                            },
                            grid: {
                                color: colors.grid
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error fetching time series data:', error);
        });
}

/**
 * Update time series chart with new time range
 */
function updateTimeSeriesChart(days) {
    initializeTimeSeriesChart(days);
}

/**
 * Initialize device breakdown pie chart
 */
function initializeDeviceChart() {
    const ctx = document.getElementById('deviceChart');
    if (!ctx) return;

    const data = window.analyticsData.deviceBreakdown;
    const colors = getChartColors();
    
    if (deviceChart) {
        deviceChart.destroy();
    }

    deviceChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => d.device_type),
            datasets: [{
                data: data.map(d => d.count),
                backgroundColor: [
                    '#3b82f6',
                    '#10b981',
                    '#f59e0b',
                ],
                borderWidth: 2,
                borderColor: colors.background
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: colors.text
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const percentage = data[context.dataIndex].percentage;
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Initialize browser breakdown pie chart
 */
function initializeBrowserChart() {
    const ctx = document.getElementById('browserChart');
    if (!ctx) return;

    const data = window.analyticsData.browserBreakdown;
    const colors = getChartColors();
    
    if (browserChart) {
        browserChart.destroy();
    }

    browserChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => d.browser),
            datasets: [{
                data: data.map(d => d.count),
                backgroundColor: [
                    '#ef4444',
                    '#f59e0b',
                    '#10b981',
                    '#3b82f6',
                    '#8b5cf6',
                ],
                borderWidth: 2,
                borderColor: colors.background
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: colors.text
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const percentage = data[context.dataIndex].percentage;
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Apply filters to analytics data
 */
function applyFilters() {
    const filters = {
        campaign_id: document.getElementById('filterCampaign').value,
        template_id: document.getElementById('filterTemplate').value,
        group_id: document.getElementById('filterGroup').value,
        date_from: document.getElementById('filterDateFrom').value,
        date_to: document.getElementById('filterDateTo').value,
    };

    // Remove empty filters
    Object.keys(filters).forEach(key => {
        if (!filters[key]) delete filters[key];
    });

    if (Object.keys(filters).length === 0) {
        alert('Please select at least one filter');
        return;
    }

    // Send filter request to backend
    fetch('/api/analytics/filter', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(filters)
    })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                console.log('Filtered data:', result.data);
                // In production, this would update the page with filtered data
                // For now, show a message
                alert(`Filters applied! Found ${result.data.emails_sent} emails sent with current filters.`);
            } else {
                alert('Failed to apply filters');
            }
        })
        .catch(error => {
            console.error('Error applying filters:', error);
            alert('Error applying filters. Please try again.');
        });
}

/**
 * Clear all filters
 */
function clearFilters() {
    document.getElementById('filterCampaign').value = '';
    document.getElementById('filterTemplate').value = '';
    document.getElementById('filterGroup').value = '';
    document.getElementById('filterDateFrom').value = '';
    document.getElementById('filterDateTo').value = '';
    document.getElementById('filterTimeRange').value = '30';

    // Reload page to show unfiltered data
    location.reload();
}

/**
 * Export analytics data
 */
function exportData() {
    fetch('/api/analytics/export')
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                alert(result.message);
            } else {
                alert('Export failed');
            }
        })
        .catch(error => {
            console.error('Error exporting data:', error);
            alert('Error exporting data. Please try again.');
        });
}

/**
 * Refresh events timeline
 */
function refreshEvents() {
    // In production, this would fetch new events via AJAX
    // For now, just reload the page
    location.reload();
}

/**
 * Format number with commas
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Calculate percentage
 */
function calculatePercentage(part, total) {
    if (total === 0) return 0;
    return ((part / total) * 100).toFixed(1);
}

/**
 * Get risk level based on score
 */
function getRiskLevel(score) {
    if (score > 15) return 'high';
    if (score > 8) return 'medium';
    return 'low';
}

/**
 * Get effectiveness level based on score
 */
function getEffectivenessLevel(score) {
    if (score > 60) return 'high';
    if (score > 40) return 'medium';
    return 'low';
}
