# 🔄 MEGA PROMPT: Sync System (Notion ↔ Sheet ↔ Dashboard)

---

## 🎯 هدف:

یک سیستم همگام‌سازی **دو طرفه** بین:
- 📊 Google Sheets
- 📝 Notion
- 🖥️ Dashboard

**قانون اصلی:** Notion = Source of Truth

---

## 📋 معماری Sync:

```
┌─────────────┐
│  Notion DB  │ ← Source of Truth
└──────┬──────┘
       │
       ↓ (Sync Every 5 min)
┌──────────────┐
│  Dashboard   │ ← Main Interface
└──────┬───────┘
       │
       ↓ (Backup Every Hour)
┌──────────────┐
│ Google Sheet │ ← Analytics & Backup
└──────────────┘
```

---

## 🔧 PART 1: Notion → Dashboard Sync

### Service: NotionSyncService

```javascript
// در backend/services/notionSync.js

const { Client } = require('@notionhq/client');
const notion = new Client({ auth: process.env.NOTION_API_KEY });

class NotionSyncService {
  constructor() {
    this.databases = {
      tasks: process.env.NOTION_TASKS_DB_ID,
      projects: process.env.NOTION_PROJECTS_DB_ID,
      habits: process.env.NOTION_HABITS_DB_ID,
      dailyLogs: process.env.NOTION_DAILY_LOGS_DB_ID
    };
  }

  // -------------------------
  // Sync All Databases
  // -------------------------
  async syncAll() {
    console.log('🔄 Starting full sync from Notion...');
    
    try {
      await this.syncTasks();
      await this.syncProjects();
      await this.syncHabits();
      await this.syncDailyLogs();
      
      console.log('✅ Full sync completed!');
      return { success: true };
    } catch (error) {
      console.error('❌ Sync error:', error);
      return { success: false, error: error.message };
    }
  }

  // -------------------------
  // Sync Tasks
  // -------------------------
  async syncTasks() {
    const response = await notion.databases.query({
      database_id: this.databases.tasks,
      filter: {
        or: [
          { property: 'Status', select: { does_not_equal: 'Done' } },
          {
            and: [
              { property: 'Status', select: { equals: 'Done' } },
              { 
                property: 'Completed Date', 
                date: { after: this.getLastWeek() } 
              }
            ]
          }
        ]
      }
    });

    for (const page of response.results) {
      const task = this.parseNotionTask(page);
      await this.upsertTaskInDB(task);
    }

    console.log(`✅ Synced ${response.results.length} tasks`);
  }

  parseNotionTask(page) {
    const props = page.properties;
    
    return {
      notion_id: page.id,
      name: props.Name?.title[0]?.plain_text || '',
      status: props.Status?.select?.name || 'Inbox',
      context: props.Context?.multi_select?.map(c => c.name) || [],
      energy_level: props['Energy Level']?.select?.name || '',
      importance: props.Importance?.select?.name || '',
      urgency: props.Urgency?.select?.name || '',
      estimated_time: props['Estimated Time']?.select?.name || '',
      due_date: props['Due Date']?.date?.start || null,
      scheduled_for: props['Scheduled For']?.date?.start || null,
      quick_win: props['Quick Win']?.checkbox || false,
      tags: props.Tags?.multi_select?.map(t => t.name) || [],
      category: props.Category?.select?.name || '',
      notes: props.Notes?.rich_text[0]?.plain_text || '',
      is_recurring: props['Is Recurring']?.checkbox || false,
      recurring_type: props['Recurring Type']?.select?.name || null,
      project_id: props['Related Project']?.relation[0]?.id || null,
      last_synced: new Date(),
      notion_url: page.url
    };
  }

  async upsertTaskInDB(task) {
    const existing = await db.query(
      'SELECT id FROM tasks WHERE notion_id = ?',
      [task.notion_id]
    );

    if (existing.length > 0) {
      await db.query(
        'UPDATE tasks SET ? WHERE notion_id = ?',
        [task, task.notion_id]
      );
    } else {
      await db.query('INSERT INTO tasks SET ?', task);
    }
  }

  // -------------------------
  // Sync Projects
  // -------------------------
  async syncProjects() {
    const response = await notion.databases.query({
      database_id: this.databases.projects
    });

    for (const page of response.results) {
      const project = this.parseNotionProject(page);
      await this.upsertProjectInDB(project);
    }

    console.log(`✅ Synced ${response.results.length} projects`);
  }

  parseNotionProject(page) {
    const props = page.properties;
    
    return {
      notion_id: page.id,
      name: props.Name?.title[0]?.plain_text || '',
      status: props.Status?.select?.name || 'Active',
      area: props.Area?.select?.name || '',
      priority: props.Priority?.select?.name || '',
      start_date: props['Start Date']?.date?.start || null,
      target_date: props['Target Date']?.date?.start || null,
      vision: props['Vision/Why']?.rich_text[0]?.plain_text || '',
      last_synced: new Date()
    };
  }

  async upsertProjectInDB(project) {
    const existing = await db.query(
      'SELECT id FROM projects WHERE notion_id = ?',
      [project.notion_id]
    );

    if (existing.length > 0) {
      await db.query(
        'UPDATE projects SET ? WHERE notion_id = ?',
        [project, project.notion_id]
      );
    } else {
      await db.query('INSERT INTO projects SET ?', project);
    }
  }

  // -------------------------
  // Sync Habits
  // -------------------------
  async syncHabits() {
    const response = await notion.databases.query({
      database_id: this.databases.habits,
      filter: {
        property: 'Status',
        select: { equals: '🎯 Active' }
      }
    });

    for (const page of response.results) {
      const habit = this.parseNotionHabit(page);
      await this.upsertHabitInDB(habit);
    }

    console.log(`✅ Synced ${response.results.length} habits`);
  }

  parseNotionHabit(page) {
    const props = page.properties;
    
    return {
      notion_id: page.id,
      name: props['Habit Name']?.title[0]?.plain_text || '',
      type: props.Type?.select?.name || '',
      category: props.Category?.select?.name || '',
      status: props.Status?.select?.name || '',
      frequency: props.Frequency?.select?.name || '',
      counter: props.Counter?.number || 0,
      streak: props.Streak?.number || 0,
      best_streak: props['Best Streak']?.number || 0,
      trigger: props['Related Trigger']?.rich_text[0]?.plain_text || '',
      last_synced: new Date()
    };
  }

  async upsertHabitInDB(habit) {
    const existing = await db.query(
      'SELECT id FROM habits WHERE notion_id = ?',
      [habit.notion_id]
    );

    if (existing.length > 0) {
      await db.query(
        'UPDATE habits SET ? WHERE notion_id = ?',
        [habit, habit.notion_id]
      );
    } else {
      await db.query('INSERT INTO habits SET ?', habit);
    }
  }

  // -------------------------
  // Helper Methods
  // -------------------------
  getLastWeek() {
    const date = new Date();
    date.setDate(date.getDate() - 7);
    return date.toISOString().split('T')[0];
  }
}

module.exports = new NotionSyncService();
```

---

## 🔧 PART 2: Dashboard → Notion Sync

### Service: NotionUpdateService

```javascript
// در backend/services/notionUpdate.js

const { Client } = require('@notionhq/client');
const notion = new Client({ auth: process.env.NOTION_API_KEY });

class NotionUpdateService {
  // -------------------------
  // Update Task in Notion
  // -------------------------
  async updateTask(taskId, updates) {
    const task = await db.query(
      'SELECT notion_id FROM tasks WHERE id = ?',
      [taskId]
    );

    if (!task[0]?.notion_id) {
      throw new Error('Task not synced with Notion');
    }

    const properties = this.buildNotionProperties(updates);

    await notion.pages.update({
      page_id: task[0].notion_id,
      properties: properties
    });

    // Update local DB
    await db.query(
      'UPDATE tasks SET ?, last_synced = NOW() WHERE id = ?',
      [updates, taskId]
    );

    return { success: true };
  }

  buildNotionProperties(updates) {
    const properties = {};

    if (updates.name) {
      properties.Name = {
        title: [{ text: { content: updates.name } }]
      };
    }

    if (updates.status) {
      properties.Status = {
        select: { name: updates.status }
      };
    }

    if (updates.energy_level) {
      properties['Energy Level'] = {
        select: { name: updates.energy_level }
      };
    }

    if (updates.importance) {
      properties.Importance = {
        select: { name: updates.importance }
      };
    }

    if (updates.urgency) {
      properties.Urgency = {
        select: { name: updates.urgency }
      };
    }

    if (updates.scheduled_for) {
      properties['Scheduled For'] = {
        date: { start: updates.scheduled_for }
      };
    }

    if (updates.due_date) {
      properties['Due Date'] = {
        date: { start: updates.due_date }
      };
    }

    if (updates.tags) {
      properties.Tags = {
        multi_select: updates.tags.map(tag => ({ name: tag }))
      };
    }

    if (updates.category) {
      properties.Category = {
        select: { name: updates.category }
      };
    }

    if (updates.context) {
      properties.Context = {
        multi_select: updates.context.map(c => ({ name: c }))
      };
    }

    return properties;
  }

  // -------------------------
  // Create Task in Notion
  // -------------------------
  async createTask(task) {
    const response = await notion.pages.create({
      parent: { database_id: process.env.NOTION_TASKS_DB_ID },
      properties: this.buildNotionProperties(task)
    });

    // Save notion_id in local DB
    await db.query(
      'UPDATE tasks SET notion_id = ?, last_synced = NOW() WHERE id = ?',
      [response.id, task.id]
    );

    return { success: true, notion_id: response.id };
  }

  // -------------------------
  // Delete Task from Notion
  // -------------------------
  async deleteTask(taskId) {
    const task = await db.query(
      'SELECT notion_id FROM tasks WHERE id = ?',
      [taskId]
    );

    if (task[0]?.notion_id) {
      // Archive in Notion (can't delete permanently via API)
      await notion.pages.update({
        page_id: task[0].notion_id,
        archived: true
      });
    }

    // Delete from local DB
    await db.query('DELETE FROM tasks WHERE id = ?', [taskId]);

    return { success: true };
  }
}

module.exports = new NotionUpdateService();
```

---

## 🔧 PART 3: Dashboard → Google Sheets Sync

### Service: SheetBackupService

```javascript
// در backend/services/sheetBackup.js

const { google } = require('googleapis');

class SheetBackupService {
  constructor() {
    this.spreadsheetId = null;
    this.sheets = null;
  }

  async init() {
    const auth = await this.getGoogleAuth();
    this.sheets = google.sheets({ version: 'v4', auth });
    
    // Load spreadsheet ID from config
    const config = await this.loadConfig();
    this.spreadsheetId = config.spreadsheetId;
  }

  async loadConfig() {
    const fs = require('fs').promises;
    const data = await fs.readFile('./config/sheets.json', 'utf8');
    return JSON.parse(data);
  }

  async getGoogleAuth() {
    const credentials = require(process.env.GOOGLE_SHEETS_CREDENTIALS);
    
    const auth = new google.auth.GoogleAuth({
      credentials: credentials,
      scopes: ['https://www.googleapis.com/auth/spreadsheets']
    });
    
    return auth;
  }

  // -------------------------
  // Backup Daily Logs
  // -------------------------
  async backupDailyLogs() {
    await this.init();
    
    // Get logs from last 7 days
    const logs = await db.query(`
      SELECT * FROM daily_logs 
      WHERE date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
      ORDER BY date DESC
    `);

    const values = logs.map(log => [
      log.date,
      log.mood,
      log.energy,
      log.top_win,
      log.main_obstacle,
      log.techniques_suggested,
      log.reflection,
      log.techniques_used || '-',
      log.bad_habits || '-',
      log.good_habits || '-',
      log.desires || '-',
      `"${log.daily_report || '-'}"`
    ]);

    // Clear existing data (keep headers)
    await this.sheets.spreadsheets.values.clear({
      spreadsheetId: this.spreadsheetId,
      range: 'Daily Log!A2:Q1000'
    });

    // Insert new data
    await this.sheets.spreadsheets.values.update({
      spreadsheetId: this.spreadsheetId,
      range: 'Daily Log!A2',
      valueInputOption: 'RAW',
      requestBody: { values }
    });

    console.log(`✅ Backed up ${logs.length} daily logs to Sheet`);
  }

  // -------------------------
  // Backup Tasks (Brain Dump Archive)
  // -------------------------
  async backupTasks() {
    await this.init();
    
    const tasks = await db.query(`
      SELECT * FROM tasks 
      WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
      ORDER BY created_at DESC
    `);

    const values = tasks.map(task => [
      task.created_at?.split('T')[0] || '',
      task.name,
      task.type || 'Task',
      task.status,
      task.context?.join(', ') || '',
      task.energy_level,
      task.importance,
      task.urgency,
      task.estimated_time,
      task.due_date || '',
      task.quick_win ? 'Yes' : 'No',
      task.notes || ''
    ]);

    await this.sheets.spreadsheets.values.clear({
      spreadsheetId: this.spreadsheetId,
      range: 'Brain Dump Archive!A2:L1000'
    });

    await this.sheets.spreadsheets.values.update({
      spreadsheetId: this.spreadsheetId,
      range: 'Brain Dump Archive!A2',
      valueInputOption: 'RAW',
      requestBody: { values }
    });

    console.log(`✅ Backed up ${tasks.length} tasks to Sheet`);
  }

  // -------------------------
  // Full Backup
  // -------------------------
  async backupAll() {
    console.log('📊 Starting full backup to Google Sheets...');
    
    try {
      await this.backupDailyLogs();
      await this.backupTasks();
      
      console.log('✅ Full backup completed!');
      return { success: true };
    } catch (error) {
      console.error('❌ Backup error:', error);
      return { success: false, error: error.message };
    }
  }
}

module.exports = new SheetBackupService();
```

---

## 🔧 PART 4: Scheduler (Cron Jobs)

### Setup: Automatic Syncing

```javascript
// در backend/services/scheduler.js

const cron = require('node-cron');
const notionSync = require('./notionSync');
const sheetBackup = require('./sheetBackup');
const recurringTasks = require('./recurringTasksScheduler');

class Scheduler {
  start() {
    console.log('⏰ Starting schedulers...');

    // Sync from Notion every 5 minutes
    cron.schedule('*/5 * * * *', async () => {
      console.log('🔄 [Scheduled] Syncing from Notion...');
      await notionSync.syncAll();
    });

    // Backup to Sheet every hour
    cron.schedule('0 * * * *', async () => {
      console.log('📊 [Scheduled] Backing up to Google Sheets...');
      await sheetBackup.backupAll();
    });

    // Create recurring tasks every day at midnight
    cron.schedule('0 0 * * *', async () => {
      console.log('🔁 [Scheduled] Creating recurring tasks...');
      await recurringTasks.createRecurringTasks();
    });

    console.log('✅ All schedulers started!');
  }

  // Manual triggers
  async triggerNotionSync() {
    console.log('🔄 [Manual] Syncing from Notion...');
    return await notionSync.syncAll();
  }

  async triggerSheetBackup() {
    console.log('📊 [Manual] Backing up to Google Sheets...');
    return await sheetBackup.backupAll();
  }
}

module.exports = new Scheduler();
```

### Start in app.js:

```javascript
// در backend/app.js

const scheduler = require('./services/scheduler');

// Start schedulers
scheduler.start();
```

---

## 🔧 PART 5: API Endpoints

```javascript
// در backend/routes/sync.js

const express = require('express');
const router = express.Router();
const notionSync = require('../services/notionSync');
const sheetBackup = require('../services/sheetBackup');
const scheduler = require('../services/scheduler');

// Manual sync from Notion
router.post('/notion/sync', async (req, res) => {
  try {
    const result = await scheduler.triggerNotionSync();
    res.json(result);
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Manual backup to Sheets
router.post('/sheets/backup', async (req, res) => {
  try {
    const result = await scheduler.triggerSheetBackup();
    res.json(result);
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get sync status
router.get('/status', async (req, res) => {
  try {
    const tasks = await db.query(`
      SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN last_synced >= DATE_SUB(NOW(), INTERVAL 10 MINUTE) THEN 1 ELSE 0 END) as recently_synced
      FROM tasks
    `);

    res.json({
      success: true,
      tasks: tasks[0],
      lastSyncTime: await getLastSyncTime()
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

async function getLastSyncTime() {
  const result = await db.query(`
    SELECT MAX(last_synced) as last_sync FROM tasks
  `);
  return result[0].last_sync;
}

module.exports = router;
```

---

## 🔧 PART 6: Frontend Sync UI

```jsx
// در frontend/src/components/SyncStatus.jsx

import { Card, Button, Space, Tag, Alert, Progress } from 'antd';
import { SyncOutlined, CloudSyncOutlined, SaveOutlined } from '@ant-design/icons';
import { useState, useEffect } from 'react';

function SyncStatus() {
  const [status, setStatus] = useState(null);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    loadStatus();
    const interval = setInterval(loadStatus, 30000); // Every 30 sec
    return () => clearInterval(interval);
  }, []);

  async function loadStatus() {
    try {
      const response = await fetch('/api/sync/status');
      const data = await response.json();
      setStatus(data);
    } catch (error) {
      console.error('Error loading sync status:', error);
    }
  }

  async function handleNotionSync() {
    setSyncing(true);
    try {
      const response = await fetch('/api/sync/notion/sync', {
        method: 'POST'
      });
      const data = await response.json();
      
      if (data.success) {
        message.success('✅ همگام‌سازی از Notion انجام شد');
        await loadStatus();
      }
    } catch (error) {
      message.error('خطا در همگام‌سازی');
    } finally {
      setSyncing(false);
    }
  }

  async function handleSheetBackup() {
    setSyncing(true);
    try {
      const response = await fetch('/api/sync/sheets/backup', {
        method: 'POST'
      });
      const data = await response.json();
      
      if (data.success) {
        message.success('✅ Backup در Sheet انجام شد');
      }
    } catch (error) {
      message.error('خطا در Backup');
    } finally {
      setSyncing(false);
    }
  }

  if (!status) return null;

  return (
    <Card 
      title="🔄 وضعیت همگام‌سازی"
      extra={
        <Space>
          <Button 
            icon={<SyncOutlined spin={syncing} />}
            onClick={handleNotionSync}
            loading={syncing}
          >
            Sync از Notion
          </Button>
          <Button 
            icon={<SaveOutlined />}
            onClick={handleSheetBackup}
            loading={syncing}
          >
            Backup در Sheet
          </Button>
        </Space>
      }
    >
      <Space direction="vertical" style={{ width: '100%' }}>
        <div>
          <strong>آخرین همگام‌سازی:</strong>{' '}
          <Tag color="green">
            {new Date(status.lastSyncTime).toLocaleString('fa-IR')}
          </Tag>
        </div>

        <div>
          <strong>کارهای همگام شده:</strong>{' '}
          <Progress 
            percent={Math.round((status.tasks.recently_synced / status.tasks.total) * 100)}
            format={(percent) => `${status.tasks.recently_synced}/${status.tasks.total}`}
          />
        </div>

        <Alert
          type="info"
          message="همگام‌سازی خودکار"
          description={
            <>
              • هر 5 دقیقه از Notion sync می‌شه<br/>
              • هر ساعت در Sheet backup می‌گیره
            </>
          }
        />
      </Space>
    </Card>
  );
}

export default SyncStatus;
```

---

## 🎯 Database Schema for Sync:

```sql
-- Add sync columns to tasks
ALTER TABLE tasks ADD COLUMN notion_id VARCHAR(100) UNIQUE;
ALTER TABLE tasks ADD COLUMN last_synced DATETIME;
ALTER TABLE tasks ADD COLUMN notion_url TEXT;

-- Add sync columns to projects
ALTER TABLE projects ADD COLUMN notion_id VARCHAR(100) UNIQUE;
ALTER TABLE projects ADD COLUMN last_synced DATETIME;

-- Add sync columns to habits
ALTER TABLE habits ADD COLUMN notion_id VARCHAR(100) UNIQUE;
ALTER TABLE habits ADD COLUMN last_synced DATETIME;

-- Sync log table
CREATE TABLE sync_log (
  id INT PRIMARY KEY AUTO_INCREMENT,
  sync_type ENUM('notion_to_db', 'db_to_notion', 'db_to_sheet') NOT NULL,
  status ENUM('success', 'failed') NOT NULL,
  records_synced INT DEFAULT 0,
  error_message TEXT,
  started_at DATETIME NOT NULL,
  completed_at DATETIME,
  duration_seconds INT
);
```

---

## 🎯 Environment Variables:

```env
# Notion API
NOTION_API_KEY=secret_xxxxx
NOTION_TASKS_DB_ID=xxxxx
NOTION_PROJECTS_DB_ID=xxxxx
NOTION_HABITS_DB_ID=xxxxx
NOTION_DAILY_LOGS_DB_ID=xxxxx

# Google Sheets
GOOGLE_SHEETS_CREDENTIALS=./credentials.json

# App
APP_URL=http://localhost:3000
```

---

## 💡 نکات مهم:

### 1. Conflict Resolution:
```javascript
// اگه هم در Notion و هم در Dashboard تغییر خورد:
function resolveConflict(notionData, dbData) {
  // Notion = Source of Truth
  return notionData.last_edited_time > dbData.updated_at 
    ? notionData 
    : dbData;
}
```

### 2. Error Handling:
```javascript
// Retry logic
async function syncWithRetry(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await sleep(1000 * (i + 1)); // Exponential backoff
    }
  }
}
```

### 3. Rate Limiting:
```javascript
// Notion API: 3 requests per second
const pLimit = require('p-limit');
const limit = pLimit(3);

const promises = tasks.map(task => 
  limit(() => updateNotionTask(task))
);
```

---

موفق باشی! 🚀

این یک سیستم همگام‌سازی کامل و قدرتمند است! 💪
