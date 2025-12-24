/**
 * 📊 ADHD Dashboard v2.0 - Charts
 * نمودارها با Chart.js
 */

// تنظیمات پیش‌فرض برای RTL
Chart.defaults.font.family = 'Vazir, system-ui, sans-serif';

// ============================================
// Mood & Energy Chart
// ============================================

function renderMoodChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || !data.labels || data.labels.length === 0) return;
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Mood',
                    data: data.mood,
                    borderColor: '#8B5CF6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6
                },
                {
                    label: 'Energy',
                    data: data.energy,
                    borderColor: '#3B82F6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    rtl: true
                }
            },
            scales: {
                y: {
                    min: 0,
                    max: 10,
                    ticks: {
                        stepSize: 2
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            }
        }
    });
}

// ============================================
// Quadrant Chart
// ============================================

function renderQuadrantChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['🔥 بحران', '🌱 رشد', '⚡ مزاحمت', '🗑️ اتلاف'],
            datasets: [{
                data: [data[1] || 0, data[2] || 0, data[3] || 0, data[4] || 0],
                backgroundColor: [
                    '#E74C3C',
                    '#2ECC71',
                    '#F39C12',
                    '#95A5A6'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    rtl: true
                }
            },
            cutout: '60%'
        }
    });
}

// ============================================
// Bad Habits Frequency Chart (Bar)
// ============================================

function renderBadHabitsChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || !data || data.length === 0) return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.name),
            datasets: [{
                label: 'دفعات',
                data: data.map(d => d.count),
                backgroundColor: '#EA4335',
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// ============================================
// Good Habits Streak Chart (Line)
// ============================================

function renderGoodHabitsChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || !data || data.length === 0) return;
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.date),
            datasets: [{
                label: 'تعداد عادت خوب',
                data: data.map(d => d.count),
                borderColor: '#34A853',
                backgroundColor: 'rgba(52, 168, 83, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            }
        }
    });
}

// ============================================
// Techniques Usage Chart (Pie)
// ============================================

function renderTechniquesChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || !data || data.length === 0) return;
    
    const colors = [
        '#4A90E2', '#50C878', '#FFB347', '#FF6B6B',
        '#C39BD3', '#85C1E9', '#F9E79F', '#ABEBC6'
    ];
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.map(d => d.name),
            datasets: [{
                data: data.map(d => d.value),
                backgroundColor: colors.slice(0, data.length),
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    rtl: true
                }
            }
        }
    });
}

// ============================================
// Energy Distribution Chart
// ============================================

function renderEnergyChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['🔥 High Focus', '⚡ Medium', '🪶 Low Focus'],
            datasets: [{
                data: [data.high || 0, data.medium || 0, data.low || 0],
                backgroundColor: [
                    '#E74C3C',
                    '#F39C12',
                    '#3498DB'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    rtl: true
                }
            },
            cutout: '60%'
        }
    });
}

// ============================================
// Context Distribution Chart
// ============================================

function renderContextChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || !data) return;
    
    const labels = Object.keys(data);
    const values = Object.values(data);
    
    if (labels.length === 0) return;
    
    const colors = [
        '#E74C3C', '#3498DB', '#2ECC71', '#F39C12',
        '#9B59B6', '#1ABC9C', '#E67E22', '#95A5A6'
    ];
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors.slice(0, labels.length),
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// ============================================
// Tasks Done Chart
// ============================================

function renderTasksChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || !data.labels) return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'کارهای انجام شده',
                data: data.values,
                backgroundColor: '#2ECC71',
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}
