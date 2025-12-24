/**
 * 🧠 ADHD Dashboard v2.0 - Main JavaScript
 */

// ============================================
// Toast Notifications
// ============================================

/**
 * نمایش Toast
 * @param {string} message - پیام
 * @param {string} type - نوع: success, error, info
 * @param {number} duration - مدت نمایش (ms)
 */
function showToast(message, type = 'info', duration = 3000) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: '✅',
        error: '❌',
        info: 'ℹ️'
    };
    
    toast.innerHTML = `
        <span>${icons[type] || 'ℹ️'}</span>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(20px)';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ============================================
// API Helper
// ============================================

/**
 * ارسال درخواست به API
 * @param {string} url - آدرس
 * @param {object} options - تنظیمات fetch
 * @returns {Promise<object>}
 */
async function apiRequest(url, options = {}) {
    try {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        const response = await fetch(url, { ...defaultOptions, ...options });
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'خطای سرور');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// ============================================
// Task Actions
// ============================================

/**
 * علامت‌گذاری Task به عنوان Done
 * @param {string} taskId - شناسه Task
 */
async function markDone(taskId) {
    try {
        const result = await apiRequest(`/api/tasks/${taskId}/done`, { method: 'POST' });
        
        if (result.success) {
            showToast('آفرین! ✅', 'success');
            
            const taskEl = document.querySelector(`[data-id="${taskId}"]`);
            if (taskEl) {
                taskEl.classList.add('opacity-50', 'line-through');
                setTimeout(() => {
                    taskEl.style.transition = 'all 0.3s ease';
                    taskEl.style.opacity = '0';
                    taskEl.style.transform = 'translateX(-20px)';
                    setTimeout(() => taskEl.remove(), 300);
                }, 500);
            }
            
            updateStats();
        }
    } catch (error) {
        showToast('خطا در انجام عملیات', 'error');
    }
}

/**
 * حذف Task
 * @param {string} taskId - شناسه Task
 */
async function deleteTask(taskId) {
    if (!confirm('مطمئنی می‌خوای حذف کنی؟')) return;
    
    try {
        const result = await apiRequest(`/api/tasks/${taskId}`, { method: 'DELETE' });
        
        if (result.success) {
            showToast('حذف شد', 'success');
            
            const taskEl = document.querySelector(`[data-id="${taskId}"]`);
            if (taskEl) {
                taskEl.style.transition = 'all 0.3s ease';
                taskEl.style.opacity = '0';
                taskEl.style.transform = 'translateX(-20px)';
                setTimeout(() => taskEl.remove(), 300);
            }
        }
    } catch (error) {
        showToast('خطا در حذف', 'error');
    }
}

// ============================================
// Stats Update
// ============================================

/**
 * بروزرسانی آمار در Dashboard
 */
async function updateStats() {
    try {
        const stats = await apiRequest('/api/stats');
        
        // بروزرسانی اعداد
        const doneToday = document.querySelector('[data-stat="done-today"]');
        if (doneToday) doneToday.textContent = stats.done_today || 0;
        
        const pending = document.querySelector('[data-stat="pending"]');
        if (pending) pending.textContent = stats.pending || 0;
        
        const urgent = document.querySelector('[data-stat="urgent"]');
        if (urgent) urgent.textContent = stats.urgent || 0;
        
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

// ============================================
// Utility Functions
// ============================================

/**
 * فرمت تاریخ
 * @param {string} dateStr - تاریخ ISO
 * @returns {string}
 */
function formatDate(dateStr) {
    if (!dateStr) return '';
    
    const date = new Date(dateStr);
    return date.toLocaleDateString('fa-IR', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

/**
 * کوتاه کردن متن
 * @param {string} text - متن
 * @param {number} maxLength - حداکثر طول
 * @returns {string}
 */
function truncate(text, maxLength = 50) {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

/**
 * Debounce
 * @param {Function} func - تابع
 * @param {number} wait - تاخیر
 * @returns {Function}
 */
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

/**
 * Escape HTML
 * @param {string} text - متن
 * @returns {string}
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================
// Keyboard Shortcuts
// ============================================

document.addEventListener('keydown', (e) => {
    // ESC - بستن modal ها
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal:not(.hidden)');
        modals.forEach(modal => modal.classList.add('hidden'));
    }
    
    // Ctrl+K - جستجوی سریع
    if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[name="q"]');
        if (searchInput) searchInput.focus();
    }
});

// ============================================
// Card Animations
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // اضافه کردن انیمیشن به کارت‌ها
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.05}s`;
        card.classList.add('card-enter');
    });
});

// ============================================
// Console Message
// ============================================

console.log(`
🧠 ADHD Dashboard v2.0
━━━━━━━━━━━━━━━━━━━━━
ساخته شده با 💜 برای ذهن‌های ADHD
`);
