/**
 * 🧠 ADHD Dashboard v3.0 - Main JavaScript
 * Features:
 * - Toast Notifications
 * - Confetti Celebration
 * - Focus Mode (Zen) with Pomodoro Timer
 * - Kanban Drag & Drop
 * - Alpine.js Integration
 */

// ============================================
// Global State
// ============================================

let currentFocusTaskId = null;
let timerInterval = null;
let timerSeconds = 25 * 60; // 25 minutes
let timerRunning = false;

// ============================================
// Toast Notifications
// ============================================

function showToast(message, type = 'info', duration = 3000) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = message;
    
    container.appendChild(toast);
    
    // Auto remove
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(-20px)';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ============================================
// Confetti Celebration 🎊
// ============================================

function celebrate() {
    if (typeof confetti === 'undefined') {
        console.warn('Confetti library not loaded');
        return;
    }
    
    // First burst
    confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 },
        colors: ['#6366F1', '#8B5CF6', '#10B981', '#F59E0B', '#EF4444']
    });
    
    // Side bursts
    setTimeout(() => {
        confetti({
            particleCount: 50,
            angle: 60,
            spread: 55,
            origin: { x: 0 },
            colors: ['#6366F1', '#8B5CF6', '#10B981']
        });
    }, 200);
    
    setTimeout(() => {
        confetti({
            particleCount: 50,
            angle: 120,
            spread: 55,
            origin: { x: 1 },
            colors: ['#6366F1', '#8B5CF6', '#10B981']
        });
    }, 400);
}

function smallCelebrate() {
    if (typeof confetti === 'undefined') return;
    
    confetti({
        particleCount: 30,
        spread: 50,
        origin: { y: 0.7 },
        colors: ['#10B981', '#6366F1']
    });
}

// ============================================
// Focus Mode (Zen)
// ============================================

function openFocusMode() {
    const modal = document.getElementById('focus-modal');
    if (!modal) return;
    
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
    
    // Load priority task
    loadPriorityTask();
    
    // Reset timer
    resetTimer();
}

function closeFocusMode() {
    const modal = document.getElementById('focus-modal');
    if (!modal) return;
    
    modal.classList.add('hidden');
    document.body.style.overflow = '';
    
    // Stop timer
    pauseTimer();
}

async function loadPriorityTask() {
    const titleEl = document.getElementById('focus-task-title');
    const categoryEl = document.getElementById('focus-task-category');
    
    if (!titleEl) return;
    
    try {
        const response = await fetch('/api/tasks?status=Next%20Action&limit=1');
        const data = await response.json();
        
        if (data.tasks && data.tasks.length > 0) {
            const task = data.tasks[0];
            currentFocusTaskId = task.id;
            titleEl.textContent = task.title;
            categoryEl.textContent = task.category || task.status || '';
        } else {
            // Try urgent tasks
            const urgentResponse = await fetch('/api/tasks?urgency=Urgent&limit=1');
            const urgentData = await urgentResponse.json();
            
            if (urgentData.tasks && urgentData.tasks.length > 0) {
                const task = urgentData.tasks[0];
                currentFocusTaskId = task.id;
                titleEl.textContent = task.title;
                categoryEl.textContent = '🚨 فوری';
            } else {
                titleEl.textContent = 'کاری وجود نداره!';
                categoryEl.textContent = 'یه کار جدید اضافه کن';
                currentFocusTaskId = null;
            }
        }
    } catch (error) {
        titleEl.textContent = 'خطا در بارگذاری';
        categoryEl.textContent = '';
        currentFocusTaskId = null;
    }
}

async function completeFocusTask() {
    if (!currentFocusTaskId) {
        showToast('کاری انتخاب نشده', 'warning');
        closeFocusMode();
        return;
    }
    
    try {
        const response = await fetch(`/api/tasks/${currentFocusTaskId}/done`, {
            method: 'POST'
        });
        
        if (response.ok) {
            celebrate();
            showToast('🎉 آفرین! کار انجام شد!', 'success', 4000);
            
            setTimeout(() => {
                closeFocusMode();
                // Reload page to update stats
                window.location.reload();
            }, 2000);
        } else {
            showToast('خطا در ثبت', 'error');
        }
    } catch (error) {
        showToast('خطا در ارتباط', 'error');
    }
}

// ============================================
// Pomodoro Timer
// ============================================

function startTimer() {
    if (timerRunning) return;
    
    timerRunning = true;
    document.getElementById('timer-start')?.classList.add('hidden');
    document.getElementById('timer-pause')?.classList.remove('hidden');
    
    timerInterval = setInterval(() => {
        timerSeconds--;
        updateTimerDisplay();
        
        if (timerSeconds <= 0) {
            timerComplete();
        }
    }, 1000);
}

function pauseTimer() {
    timerRunning = false;
    clearInterval(timerInterval);
    
    document.getElementById('timer-start')?.classList.remove('hidden');
    document.getElementById('timer-pause')?.classList.add('hidden');
}

function resetTimer() {
    pauseTimer();
    timerSeconds = 25 * 60;
    updateTimerDisplay();
}

function updateTimerDisplay() {
    const display = document.getElementById('timer-display');
    if (!display) return;
    
    const minutes = Math.floor(timerSeconds / 60);
    const seconds = timerSeconds % 60;
    
    display.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    // Change color when low
    if (timerSeconds < 60) {
        display.classList.add('text-red-500');
        display.classList.remove('text-primary');
    } else if (timerSeconds < 300) {
        display.classList.add('text-yellow-500');
        display.classList.remove('text-primary');
    }
}

function timerComplete() {
    pauseTimer();
    
    // Sound notification (if available)
    try {
        const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdH19');
        audio.play().catch(() => {});
    } catch (e) {}
    
    // Visual notification
    smallCelebrate();
    showToast('⏰ زمان تمام شد! استراحت کن', 'info', 5000);
    
    // Vibrate (mobile)
    if (navigator.vibrate) {
        navigator.vibrate([200, 100, 200]);
    }
}

// ============================================
// Task Actions
// ============================================

async function markDone(taskId) {
    try {
        const response = await fetch(`/api/tasks/${taskId}/done`, { method: 'POST' });
        const result = await response.json();
        
        if (result.success) {
            smallCelebrate();
            showToast('✅ آفرین!', 'success');
            
            const taskEl = document.querySelector(`[data-id="${taskId}"]`);
            if (taskEl) {
                taskEl.style.opacity = '0.5';
                taskEl.style.transform = 'translateX(-20px)';
                setTimeout(() => taskEl.remove(), 300);
            }
        }
    } catch (error) {
        showToast('خطا', 'error');
    }
}

async function deleteTask(taskId) {
    if (!confirm('حذف شود؟')) return;
    
    try {
        const response = await fetch(`/api/tasks/${taskId}`, { method: 'DELETE' });
        const result = await response.json();
        
        if (result.success) {
            showToast('حذف شد', 'info');
            document.querySelector(`[data-id="${taskId}"]`)?.remove();
        }
    } catch (error) {
        showToast('خطا', 'error');
    }
}

// ============================================
// Habit Actions
// ============================================

async function incrementHabit(habitId) {
    try {
        const response = await fetch(`/api/habits/${habitId}/increment`, {
            method: 'POST'
        });
        const result = await response.json();
        
        if (result.success) {
            smallCelebrate();
            showToast(`🔥 Streak: ${result.habit.streak}`, 'success');
            
            // Update UI
            const card = document.querySelector(`[data-habit-id="${habitId}"]`);
            if (card) {
                const counterEl = card.querySelector('.habit-counter');
                const streakEl = card.querySelector('.habit-streak');
                
                if (counterEl) counterEl.textContent = result.habit.counter;
                if (streakEl) streakEl.textContent = result.habit.streak;
            }
        }
    } catch (error) {
        showToast('خطا', 'error');
    }
}

// ============================================
// Kanban Drag & Drop
// ============================================

function initKanban() {
    const columns = document.querySelectorAll('.kanban-column');
    
    columns.forEach(column => {
        if (typeof Sortable === 'undefined') {
            console.warn('SortableJS not loaded');
            return;
        }
        
        new Sortable(column.querySelector('.kanban-items'), {
            group: 'tasks',
            animation: 150,
            ghostClass: 'sortable-ghost',
            dragClass: 'sortable-drag',
            
            onEnd: async function(evt) {
                const taskId = evt.item.dataset.id;
                const newStatus = evt.to.closest('.kanban-column').dataset.status;
                
                if (taskId && newStatus) {
                    try {
                        await fetch(`/api/tasks/${taskId}`, {
                            method: 'PATCH',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ status: newStatus })
                        });
                        
                        showToast('منتقل شد', 'info');
                    } catch (error) {
                        showToast('خطا در انتقال', 'error');
                    }
                }
            }
        });
    });
}

// ============================================
// Alpine.js Global Store
// ============================================

document.addEventListener('alpine:init', () => {
    Alpine.store('app', {
        darkMode: true,
        focusMode: false,
        
        toggleDarkMode() {
            this.darkMode = !this.darkMode;
            document.documentElement.classList.toggle('dark', this.darkMode);
        }
    });
});

// ============================================
// Keyboard Shortcuts
// ============================================

document.addEventListener('keydown', (e) => {
    // Escape: Close modals
    if (e.key === 'Escape') {
        closeFocusMode();
        document.querySelectorAll('.modal').forEach(m => m.classList.add('hidden'));
    }
    
    // F: Open Focus Mode
    if (e.key === 'f' && !e.ctrlKey && !e.metaKey && !isInputFocused()) {
        openFocusMode();
    }
    
    // Space in Focus Mode: Toggle timer
    if (e.key === ' ' && document.getElementById('focus-modal')?.classList.contains('hidden') === false) {
        e.preventDefault();
        timerRunning ? pauseTimer() : startTimer();
    }
});

function isInputFocused() {
    const active = document.activeElement;
    return active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA' || active.isContentEditable);
}

// ============================================
// Initialize
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Kanban if exists
    if (document.querySelector('.kanban-column')) {
        initKanban();
    }
    
    // Add click handlers for task checkboxes
    document.querySelectorAll('.task-checkbox').forEach(checkbox => {
        checkbox.addEventListener('click', function() {
            const taskId = this.closest('[data-id]')?.dataset.id;
            if (taskId) markDone(taskId);
        });
    });
    
    console.log('🧠 ADHD Dashboard v3.0 loaded');
});

// ============================================
// Utility Functions
// ============================================

function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('fa-IR');
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ============================================
// Export for global use
// ============================================

window.showToast = showToast;
window.celebrate = celebrate;
window.smallCelebrate = smallCelebrate;
window.openFocusMode = openFocusMode;
window.closeFocusMode = closeFocusMode;
window.completeFocusTask = completeFocusTask;
window.startTimer = startTimer;
window.pauseTimer = pauseTimer;
window.resetTimer = resetTimer;
window.markDone = markDone;
window.deleteTask = deleteTask;
window.incrementHabit = incrementHabit;
