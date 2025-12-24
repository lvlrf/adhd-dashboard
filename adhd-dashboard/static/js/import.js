/**
 * 📥 Import JavaScript - v2.0
 * مدیریت Import از Gem به Notion
 */

let parsedTasks = [];

// ============================================
// Parse JSON
// ============================================

function parseJSON() {
    const input = document.getElementById('json-input').value.trim();
    
    if (!input) {
        showToast('لطفاً JSON را وارد کنید', 'error');
        return;
    }
    
    try {
        const data = JSON.parse(input);
        
        if (data.tasks && Array.isArray(data.tasks)) {
            parsedTasks = data.tasks;
        } else if (Array.isArray(data)) {
            parsedTasks = data;
        } else {
            throw new Error('فرمت نادرست');
        }
        
        if (parsedTasks.length === 0) {
            showToast('هیچ Task ای پیدا نشد', 'error');
            return;
        }
        
        showPreview(parsedTasks);
        showToast(`${parsedTasks.length} کار پیدا شد ✅`, 'success');
        
    } catch (error) {
        console.error('Parse error:', error);
        showToast('خطا در پارس JSON: ' + error.message, 'error');
        parsedTasks = [];
        hidePreview();
    }
}

// ============================================
// Preview
// ============================================

function showPreview(tasks) {
    const section = document.getElementById('preview-section');
    const list = document.getElementById('preview-list');
    const count = document.getElementById('preview-count');
    
    section.classList.remove('hidden');
    count.textContent = `${tasks.length} کار`;
    
    list.innerHTML = tasks.map((task, index) => `
        <div class="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
            <span class="w-6 h-6 rounded-full bg-primary text-white text-xs flex items-center justify-center shrink-0">
                ${index + 1}
            </span>
            <div class="flex-1 min-w-0">
                <h4 class="font-medium text-gray-800 truncate">${escapeHtml(task.title || 'بدون عنوان')}</h4>
                <div class="flex flex-wrap gap-1 mt-1">
                    ${task.status ? `<span class="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full">${escapeHtml(task.status)}</span>` : ''}
                    ${task.importance ? `<span class="text-xs px-2 py-0.5 bg-purple-100 text-purple-700 rounded-full">${escapeHtml(task.importance)}</span>` : ''}
                    ${task.urgency ? `<span class="text-xs px-2 py-0.5 bg-yellow-100 text-yellow-700 rounded-full">${escapeHtml(task.urgency)}</span>` : ''}
                    ${task.energy ? `<span class="text-xs px-2 py-0.5 bg-orange-100 text-orange-700 rounded-full">${escapeHtml(task.energy)}</span>` : ''}
                    ${task.quick_win ? `<span class="text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded-full">⚡ Quick Win</span>` : ''}
                </div>
                ${task.notes ? `<p class="text-xs text-gray-500 mt-1 truncate">${escapeHtml(task.notes)}</p>` : ''}
            </div>
            <button onclick="removeFromPreview(${index})" class="text-gray-400 hover:text-red-500" title="حذف">
                ✕
            </button>
        </div>
    `).join('');
}

function hidePreview() {
    document.getElementById('preview-section').classList.add('hidden');
    document.getElementById('result-section')?.classList.add('hidden');
}

function removeFromPreview(index) {
    parsedTasks.splice(index, 1);
    
    if (parsedTasks.length === 0) {
        hidePreview();
        showToast('همه کارها حذف شدند', 'info');
    } else {
        showPreview(parsedTasks);
    }
}

// ============================================
// Import
// ============================================

async function importTasks() {
    if (parsedTasks.length === 0) {
        showToast('لیست خالی است', 'error');
        return;
    }
    
    const btn = document.getElementById('import-btn');
    btn.disabled = true;
    btn.innerHTML = '⏳ در حال Import...';
    
    try {
        const response = await fetch('/api/import', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tasks: parsedTasks })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showResult(result);
            showToast(`${result.imported} کار Import شد! 🎉`, 'success');
            
            document.getElementById('json-input').value = '';
            parsedTasks = [];
            document.getElementById('preview-section').classList.add('hidden');
        } else {
            showToast(result.error || 'خطا در Import', 'error');
        }
        
    } catch (error) {
        console.error('Import error:', error);
        showToast('خطا در ارتباط با سرور', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '📤 Import به Notion';
    }
}

function showResult(result) {
    const section = document.getElementById('result-section');
    const title = document.getElementById('result-title');
    const content = document.getElementById('result-content');
    
    section.classList.remove('hidden');
    
    if (result.failed === 0) {
        title.textContent = '✅ Import موفق';
        title.className = 'card-title text-green-600';
    } else {
        title.textContent = '⚠️ Import با خطا';
        title.className = 'card-title text-yellow-600';
    }
    
    content.innerHTML = `
        <div class="grid grid-cols-2 gap-4 mb-4">
            <div class="text-center p-4 bg-green-50 rounded-xl">
                <div class="text-3xl font-bold text-green-600">${result.imported}</div>
                <div class="text-sm text-gray-500">موفق</div>
            </div>
            <div class="text-center p-4 bg-red-50 rounded-xl">
                <div class="text-3xl font-bold text-red-600">${result.failed}</div>
                <div class="text-sm text-gray-500">ناموفق</div>
            </div>
        </div>
        
        ${result.errors && result.errors.length > 0 ? `
            <div class="bg-red-50 p-3 rounded-lg">
                <h4 class="font-medium text-red-700 mb-2">خطاها:</h4>
                <ul class="text-sm text-red-600 space-y-1">
                    ${result.errors.map(err => `<li>• ${escapeHtml(err)}</li>`).join('')}
                </ul>
            </div>
        ` : ''}
        
        <div class="mt-4">
            <a href="/tasks" class="btn-primary inline-block">مشاهده کارها →</a>
        </div>
    `;
}

// ============================================
// Utilities
// ============================================

function clearInput() {
    document.getElementById('json-input').value = '';
    parsedTasks = [];
    hidePreview();
    showToast('پاک شد', 'info');
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function loadSampleData() {
    const sample = {
        "tasks": [
            {
                "title": "جواب دادن به ایمیل مهم",
                "status": "▶️ Next Action",
                "context": ["📧 ایمیل"],
                "energy": "🪶 Low Focus",
                "importance": "🔴 High",
                "urgency": "🚨 Urgent",
                "time": "🕐 15 min",
                "quick_win": true,
                "notes": "ایمیل از مدیر پروژه"
            },
            {
                "title": "برنامه‌ریزی هفته آینده",
                "status": "▶️ Next Action",
                "context": ["🤔 فکر کردن", "📝 نوشتن"],
                "energy": "🔥 High Focus",
                "importance": "🔴 High",
                "urgency": "⏰ Soon",
                "time": "🕑 30 min",
                "quick_win": false
            },
            {
                "title": "خرید لوازم اداری",
                "status": "💭 Someday/Maybe",
                "context": ["🛒 خرید"],
                "energy": "🪶 Low Focus",
                "importance": "🟢 Low",
                "urgency": "📅 Normal",
                "time": "🕓 1 hour"
            }
        ]
    };
    
    document.getElementById('json-input').value = JSON.stringify(sample, null, 2);
    showToast('نمونه داده بارگذاری شد', 'info');
}
