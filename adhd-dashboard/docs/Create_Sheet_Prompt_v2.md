# 📊 MEGA PROMPT: Create Google Sheet v2 (با ساختار واقعی)

---

## 🎯 هدف:

یک دکمه در Dashboard بساز که Google Sheet با ساختار **دقیقاً مشابه** فایل موجود رو بسازه.

**تغییرات مهم نسبت به نسخه قبل:**
- ✅ **Auto-detect تمام Tab ها** (بدون نیاز به .env)
- ✅ **امکان اضافه کردن Tab/Sheet جدید** از Dashboard
- ✅ **ساختار دقیق** مطابق با فایل فعلی

---

## 📋 ساختار Sheet موجود:

### Tab 1: Daily Log (17 ستون)
```
A: تاریخ
B: Mood (1-10)
C: Energy (1-10)
D: Top Win
E: Main Obstacle
F: Techniques Suggested
G: Reflection
H: Techniques Used
I: Bad Habits
J: Good Habits
K: Desires
L: Daily Report
M: Avg Mood (Formula)
N: Avg Energy (Formula)
O: Techs Used (Formula)
P: Bad Habits Count (Formula)
Q: Good Habits Count (Formula)
```

### Tab 2: Brain Dump Archive (12 ستون)
```
A: تاریخ
B: نام
C: نوع
D: وضعیت
E: زمینه
F: انرژی
G: اهمیت
H: فوریت
I: زمان تخمینی
J: ددلاین
K: Quick Win
L: یادداشت
```

### Tab 3: Analytics
```
A1: "Analytics Dashboard (Charts Placeholders)"
```

---

## 🔧 Environment Variables (ساده‌شده):

```env
# فقط یک متغیر:
GOOGLE_SHEETS_CREDENTIALS=./credentials.json

# باقی به صورت خودکار:
# - Spreadsheet ID: بعد از ساخت ذخیره می‌شه در DB
# - Tab Names: خودکار Detect می‌شوند
```

---

## 🚀 Implementation:

### Step 1: Auto-Detect All Tabs

```javascript
// در backend/services/sheetService.js

const { google } = require('googleapis');

async function getAllSheetTabs(spreadsheetId) {
  const auth = await getGoogleAuth();
  const sheets = google.sheets({ version: 'v4', auth });
  
  const response = await sheets.spreadsheets.get({
    spreadsheetId: spreadsheetId
  });
  
  const tabs = response.data.sheets.map(sheet => ({
    sheetId: sheet.properties.sheetId,
    title: sheet.properties.title,
    index: sheet.properties.index
  }));
  
  return tabs;
}

// استفاده:
const tabs = await getAllSheetTabs(process.env.DAILY_LOG_SHEET_ID);
// Result: [
//   { sheetId: 0, title: 'Daily Log', index: 0 },
//   { sheetId: 1, title: 'Brain Dump Archive', index: 1 },
//   { sheetId: 2, title: 'Analytics', index: 2 }
// ]
```

---

### Step 2: Create Sheet Function (Updated)

```javascript
// در backend/services/sheetCreator.js

async function createADHDSheetV2(onProgress) {
  const auth = await getGoogleAuth();
  const sheets = google.sheets({ version: 'v4', auth });
  
  try {
    // Step 1: Create Spreadsheet
    onProgress('ایجاد Spreadsheet...', 5);
    
    const spreadsheet = await sheets.spreadsheets.create({
      requestBody: {
        properties: {
          title: `ADHD Tracker - ${new Date().toISOString().split('T')[0]}`,
          locale: 'fa_IR',
          timeZone: 'Asia/Tehran'
        },
        sheets: [
          { properties: { title: 'Daily Log', index: 0 } },
          { properties: { title: 'Brain Dump Archive', index: 1 } },
          { properties: { title: 'Analytics', index: 2 } }
        ]
      }
    });
    
    const spreadsheetId = spreadsheet.data.spreadsheetId;
    const spreadsheetUrl = spreadsheet.data.spreadsheetUrl;
    
    // Step 2: Setup Daily Log (17 columns)
    onProgress('تنظیم Daily Log (17 ستون)...', 20);
    await setupDailyLogTab(sheets, spreadsheetId);
    
    // Step 3: Setup Brain Dump Archive (12 columns)
    onProgress('تنظیم Brain Dump Archive (12 ستون)...', 50);
    await setupBrainDumpTab(sheets, spreadsheetId);
    
    // Step 4: Setup Analytics
    onProgress('تنظیم Analytics...', 70);
    await setupAnalyticsTab(sheets, spreadsheetId);
    
    // Step 5: Formatting
    onProgress('Conditional Formatting...', 85);
    await addConditionalFormatting(sheets, spreadsheetId);
    
    // Step 6: Save to DB
    onProgress('ذخیره در دیتابیس...', 95);
    await saveSheetIdToDatabase(spreadsheetId);
    
    onProgress('✅ تمام!', 100);
    
    return {
      success: true,
      spreadsheetId,
      spreadsheetUrl
    };
    
  } catch (error) {
    throw new Error(`خطا در ساخت Sheet: ${error.message}`);
  }
}

// -------------------------
// Setup Daily Log Tab (17 columns)
// -------------------------
async function setupDailyLogTab(sheets, spreadsheetId) {
  const sheetId = 0;
  
  // Headers
  const headers = [[
    'تاریخ',           // A
    'Mood',            // B
    'Energy',          // C
    'Top Win',         // D
    'Main Obstacle',   // E
    'Techniques Suggested', // F
    'Reflection',      // G
    'Techniques Used', // H
    'Bad Habits',      // I
    'Good Habits',     // J
    'Desires',         // K
    'Daily Report',    // L
    'Avg Mood',        // M
    'Avg Energy',      // N
    'Techs Used',      // O
    'Bad Habits Count', // P
    'Good Habits Count' // Q
  ]];
  
  await sheets.spreadsheets.values.update({
    spreadsheetId,
    range: 'Daily Log!A1:Q1',
    valueInputOption: 'RAW',
    requestBody: { values: headers }
  });
  
  // Sample Data (Row 2-4)
  const sampleData = [
    [
      '2024/12/24', '7', '8', 'انجام 3 Task', 'حواس‌پرتی',
      'Pomodoro, Body Doubling', 'روز خوب', 'Pomodoro',
      '-', 'ورزش صبحگاهی', 'مطالعه بیشتر',
      '"امروز روز خوبی بود. انرژی بالا داشتم و 3 تا Task مهم رو تموم کردم."',
      '', '', '', '', '' // Empty for formulas
    ],
    [
      '2024/12/23', '5', '6', 'تماس با مشتری', 'خستگی',
      'قانون 5 دقیقه', 'خسته', '-',
      'دیر خوابیدن', '-', 'زودتر بخوابم',
      '"خسته بودم ولی تماس مهم رو انجام دادم."',
      '', '', '', '', ''
    ],
    [
      '2024/12/22', '8', '9', '2 پروژه تمام شد', '-',
      'Big 3, Time Blocking', 'عالی', 'Time Blocking, Big 3',
      '-', 'ورزش، خواب کافی', '-',
      '"یکی از بهترین روزها! هر دو پروژه رو تحویل دادم."',
      '', '', '', '', ''
    ]
  ];
  
  await sheets.spreadsheets.values.update({
    spreadsheetId,
    range: 'Daily Log!A2:Q4',
    valueInputOption: 'RAW',
    requestBody: { values: sampleData }
  });
  
  // Formulas (Row 2)
  const formulas = [[
    '=AVERAGE(B2:B100)',  // M2: Avg Mood
    '=AVERAGE(C2:C100)',  // N2: Avg Energy
    '=COUNTA(H2:H100)',   // O2: Techs Used
    '=COUNTA(I2:I100)',   // P2: Bad Habits Count
    '=COUNTA(J2:J100)'    // Q2: Good Habits Count
  ]];
  
  await sheets.spreadsheets.values.update({
    spreadsheetId,
    range: 'Daily Log!M2:Q2',
    valueInputOption: 'USER_ENTERED',
    requestBody: { values: formulas }
  });
  
  // Formatting
  await sheets.spreadsheets.batchUpdate({
    spreadsheetId,
    requestBody: {
      requests: [
        // Header formatting (Blue background, white text, bold)
        {
          repeatCell: {
            range: {
              sheetId: sheetId,
              startRowIndex: 0,
              endRowIndex: 1
            },
            cell: {
              userEnteredFormat: {
                backgroundColor: { red: 0.26, green: 0.52, blue: 0.96 },
                textFormat: { 
                  foregroundColor: { red: 1, green: 1, blue: 1 },
                  bold: true,
                  fontSize: 10
                },
                horizontalAlignment: 'CENTER',
                verticalAlignment: 'MIDDLE'
              }
            },
            fields: 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)'
          }
        },
        // Freeze header row + first column
        {
          updateSheetProperties: {
            properties: {
              sheetId: sheetId,
              gridProperties: {
                frozenRowCount: 1,
                frozenColumnCount: 1
              }
            },
            fields: 'gridProperties.frozenRowCount,gridProperties.frozenColumnCount'
          }
        },
        // Auto-resize columns
        {
          autoResizeDimensions: {
            dimensions: {
              sheetId: sheetId,
              dimension: 'COLUMNS',
              startIndex: 0,
              endIndex: 17
            }
          }
        }
      ]
    }
  });
}

// -------------------------
// Setup Brain Dump Archive Tab (12 columns)
// -------------------------
async function setupBrainDumpTab(sheets, spreadsheetId) {
  const sheetId = 1;
  
  const headers = [[
    'تاریخ',        // A
    'نام',          // B
    'نوع',          // C
    'وضعیت',        // D
    'زمینه',        // E
    'انرژی',        // F
    'اهمیت',        // G
    'فوریت',        // H
    'زمان تخمینی',  // I
    'ددلاین',       // J
    'Quick Win',    // K
    'یادداشت'       // L
  ]];
  
  await sheets.spreadsheets.values.update({
    spreadsheetId,
    range: 'Brain Dump Archive!A1:L1',
    valueInputOption: 'RAW',
    requestBody: { values: headers }
  });
  
  // Sample data
  const sampleData = [
    [
      '2024/12/24', 'تماس با علی درباره پروژه', 'Task', 'Next Action',
      '📞 تماس', '⚡ Medium', '🔴 High', '🚨 Urgent',
      '🕐 15 min', '2024/12/25', 'No', 'پیگیری پروژه سایت'
    ],
    [
      '2024/12/24', 'خرید نان و شیر', 'Task', 'Next Action',
      '🛒 خرید', '🪶 Low', '🟡 Medium', '⏰ Soon',
      '⚡ <5 min', '', 'Yes', ''
    ],
    [
      '2024/12/23', 'پروژه سایت شرکت X', 'Project', 'In Progress',
      '💻 سیستم', '🔥 High', '🔴 High', '🚨 Urgent',
      '🕕 2+ hours', '2024/12/30', 'No', 'شامل 5 صفحه'
    ]
  ];
  
  await sheets.spreadsheets.values.update({
    spreadsheetId,
    range: 'Brain Dump Archive!A2:L4',
    valueInputOption: 'RAW',
    requestBody: { values: sampleData }
  });
  
  // Data Validation (Dropdowns)
  await sheets.spreadsheets.batchUpdate({
    spreadsheetId,
    requestBody: {
      requests: [
        // نوع (Column C)
        {
          setDataValidation: {
            range: {
              sheetId: sheetId,
              startRowIndex: 1,
              endRowIndex: 1000,
              startColumnIndex: 2,
              endColumnIndex: 3
            },
            rule: {
              condition: {
                type: 'ONE_OF_LIST',
                values: [
                  { userEnteredValue: 'Task' },
                  { userEnteredValue: 'Project' },
                  { userEnteredValue: 'Resource' }
                ]
              },
              showCustomUi: true,
              strict: true
            }
          }
        },
        // وضعیت (Column D)
        {
          setDataValidation: {
            range: {
              sheetId: sheetId,
              startRowIndex: 1,
              endRowIndex: 1000,
              startColumnIndex: 3,
              endColumnIndex: 4
            },
            rule: {
              condition: {
                type: 'ONE_OF_LIST',
                values: [
                  { userEnteredValue: 'Inbox' },
                  { userEnteredValue: 'Next Action' },
                  { userEnteredValue: 'In Progress' },
                  { userEnteredValue: 'Waiting' },
                  { userEnteredValue: 'Done' },
                  { userEnteredValue: 'Someday/Maybe' }
                ]
              },
              showCustomUi: true,
              strict: true
            }
          }
        },
        // زمینه (Column E)
        {
          setDataValidation: {
            range: {
              sheetId: sheetId,
              startRowIndex: 1,
              endRowIndex: 1000,
              startColumnIndex: 4,
              endColumnIndex: 5
            },
            rule: {
              condition: {
                type: 'ONE_OF_LIST',
                values: [
                  { userEnteredValue: '📞 تماس' },
                  { userEnteredValue: '💬 پیام' },
                  { userEnteredValue: '🛒 خرید' },
                  { userEnteredValue: '💻 سیستم' },
                  { userEnteredValue: '🚗 بیرون' },
                  { userEnteredValue: '🏢 دفتر' },
                  { userEnteredValue: '🏠 خانه' }
                ]
              },
              showCustomUi: true,
              strict: true
            }
          }
        },
        // انرژی (Column F)
        {
          setDataValidation: {
            range: {
              sheetId: sheetId,
              startRowIndex: 1,
              endRowIndex: 1000,
              startColumnIndex: 5,
              endColumnIndex: 6
            },
            rule: {
              condition: {
                type: 'ONE_OF_LIST',
                values: [
                  { userEnteredValue: '🔥 High' },
                  { userEnteredValue: '⚡ Medium' },
                  { userEnteredValue: '🪶 Low' }
                ]
              },
              showCustomUi: true,
              strict: true
            }
          }
        },
        // اهمیت (Column G)
        {
          setDataValidation: {
            range: {
              sheetId: sheetId,
              startRowIndex: 1,
              endRowIndex: 1000,
              startColumnIndex: 6,
              endColumnIndex: 7
            },
            rule: {
              condition: {
                type: 'ONE_OF_LIST',
                values: [
                  { userEnteredValue: '🔴 High' },
                  { userEnteredValue: '🟡 Medium' },
                  { userEnteredValue: '🟢 Low' }
                ]
              },
              showCustomUi: true,
              strict: true
            }
          }
        },
        // فوریت (Column H)
        {
          setDataValidation: {
            range: {
              sheetId: sheetId,
              startRowIndex: 1,
              endRowIndex: 1000,
              startColumnIndex: 7,
              endColumnIndex: 8
            },
            rule: {
              condition: {
                type: 'ONE_OF_LIST',
                values: [
                  { userEnteredValue: '🚨 Urgent' },
                  { userEnteredValue: '⏰ Soon' },
                  { userEnteredValue: '📅 Normal' },
                  { userEnteredValue: '🐢 Low' }
                ]
              },
              showCustomUi: true,
              strict: true
            }
          }
        },
        // زمان تخمینی (Column I)
        {
          setDataValidation: {
            range: {
              sheetId: sheetId,
              startRowIndex: 1,
              endRowIndex: 1000,
              startColumnIndex: 8,
              endColumnIndex: 9
            },
            rule: {
              condition: {
                type: 'ONE_OF_LIST',
                values: [
                  { userEnteredValue: '⚡ <5 min' },
                  { userEnteredValue: '🕐 15 min' },
                  { userEnteredValue: '🕑 30 min' },
                  { userEnteredValue: '🕓 1 hour' },
                  { userEnteredValue: '🕕 2+ hours' }
                ]
              },
              showCustomUi: true,
              strict: true
            }
          }
        },
        // Header formatting
        {
          repeatCell: {
            range: {
              sheetId: sheetId,
              startRowIndex: 0,
              endRowIndex: 1
            },
            cell: {
              userEnteredFormat: {
                backgroundColor: { red: 0.26, green: 0.52, blue: 0.96 },
                textFormat: { 
                  foregroundColor: { red: 1, green: 1, blue: 1 },
                  bold: true,
                  fontSize: 10
                },
                horizontalAlignment: 'CENTER'
              }
            },
            fields: 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
          }
        },
        // Freeze header
        {
          updateSheetProperties: {
            properties: {
              sheetId: sheetId,
              gridProperties: {
                frozenRowCount: 1,
                frozenColumnCount: 1
              }
            },
            fields: 'gridProperties.frozenRowCount,gridProperties.frozenColumnCount'
          }
        }
      ]
    }
  });
}

// -------------------------
// Setup Analytics Tab
// -------------------------
async function setupAnalyticsTab(sheets, spreadsheetId) {
  const sheetId = 2;
  
  const content = [[
    'Analytics Dashboard (Charts Placeholders)'
  ]];
  
  await sheets.spreadsheets.values.update({
    spreadsheetId,
    range: 'Analytics!A1',
    valueInputOption: 'RAW',
    requestBody: { values: content }
  });
  
  // Title formatting
  await sheets.spreadsheets.batchUpdate({
    spreadsheetId,
    requestBody: {
      requests: [
        {
          repeatCell: {
            range: {
              sheetId: sheetId,
              startRowIndex: 0,
              endRowIndex: 1,
              startColumnIndex: 0,
              endColumnIndex: 1
            },
            cell: {
              userEnteredFormat: {
                textFormat: { 
                  fontSize: 14,
                  bold: true
                },
                horizontalAlignment: 'CENTER'
              }
            },
            fields: 'userEnteredFormat.textFormat,userEnteredFormat.horizontalAlignment'
          }
        }
      ]
    }
  });
}

// -------------------------
// Conditional Formatting
// -------------------------
async function addConditionalFormatting(sheets, spreadsheetId) {
  const sheetId = 0; // Daily Log
  
  await sheets.spreadsheets.batchUpdate({
    spreadsheetId,
    requestBody: {
      requests: [
        // Mood (B) - Red (1-3)
        {
          addConditionalFormatRule: {
            rule: {
              ranges: [{
                sheetId: sheetId,
                startRowIndex: 1,
                endRowIndex: 1000,
                startColumnIndex: 1,
                endColumnIndex: 2
              }],
              booleanRule: {
                condition: {
                  type: 'NUMBER_BETWEEN',
                  values: [
                    { userEnteredValue: '1' },
                    { userEnteredValue: '3' }
                  ]
                },
                format: {
                  backgroundColor: { red: 0.96, green: 0.80, blue: 0.80 }
                }
              }
            },
            index: 0
          }
        },
        // Mood (B) - Yellow (4-6)
        {
          addConditionalFormatRule: {
            rule: {
              ranges: [{
                sheetId: sheetId,
                startRowIndex: 1,
                endRowIndex: 1000,
                startColumnIndex: 1,
                endColumnIndex: 2
              }],
              booleanRule: {
                condition: {
                  type: 'NUMBER_BETWEEN',
                  values: [
                    { userEnteredValue: '4' },
                    { userEnteredValue: '6' }
                  ]
                },
                format: {
                  backgroundColor: { red: 1, green: 0.95, blue: 0.80 }
                }
              }
            },
            index: 1
          }
        },
        // Mood (B) - Green (7-10)
        {
          addConditionalFormatRule: {
            rule: {
              ranges: [{
                sheetId: sheetId,
                startRowIndex: 1,
                endRowIndex: 1000,
                startColumnIndex: 1,
                endColumnIndex: 2
              }],
              booleanRule: {
                condition: {
                  type: 'NUMBER_BETWEEN',
                  values: [
                    { userEnteredValue: '7' },
                    { userEnteredValue: '10' }
                  ]
                },
                format: {
                  backgroundColor: { red: 0.85, green: 0.95, blue: 0.85 }
                }
              }
            },
            index: 2
          }
        },
        // Energy (C) - Same as Mood
        {
          addConditionalFormatRule: {
            rule: {
              ranges: [{
                sheetId: sheetId,
                startRowIndex: 1,
                endRowIndex: 1000,
                startColumnIndex: 2,
                endColumnIndex: 3
              }],
              booleanRule: {
                condition: {
                  type: 'NUMBER_BETWEEN',
                  values: [
                    { userEnteredValue: '1' },
                    { userEnteredValue: '3' }
                  ]
                },
                format: {
                  backgroundColor: { red: 0.96, green: 0.80, blue: 0.80 }
                }
              }
            },
            index: 3
          }
        },
        {
          addConditionalFormatRule: {
            rule: {
              ranges: [{
                sheetId: sheetId,
                startRowIndex: 1,
                endRowIndex: 1000,
                startColumnIndex: 2,
                endColumnIndex: 3
              }],
              booleanRule: {
                condition: {
                  type: 'NUMBER_BETWEEN',
                  values: [
                    { userEnteredValue: '4' },
                    { userEnteredValue: '6' }
                  ]
                },
                format: {
                  backgroundColor: { red: 1, green: 0.95, blue: 0.80 }
                }
              }
            },
            index: 4
          }
        },
        {
          addConditionalFormatRule: {
            rule: {
              ranges: [{
                sheetId: sheetId,
                startRowIndex: 1,
                endRowIndex: 1000,
                startColumnIndex: 2,
                endColumnIndex: 3
              }],
              booleanRule: {
                condition: {
                  type: 'NUMBER_BETWEEN',
                  values: [
                    { userEnteredValue: '7' },
                    { userEnteredValue: '10' }
                  ]
                },
                format: {
                  backgroundColor: { red: 0.85, green: 0.95, blue: 0.85 }
                }
              }
            },
            index: 5
          }
        }
      ]
    }
  });
}

// -------------------------
// Save to Database
// -------------------------
async function saveSheetIdToDatabase(spreadsheetId) {
  // این تابع Sheet ID رو در دیتابیس ذخیره می‌کنه
  // می‌تونه SQLite, PostgreSQL, MongoDB یا حتی یک JSON file باشه
  
  const fs = require('fs').promises;
  const configPath = './config/sheets.json';
  
  const config = {
    spreadsheetId: spreadsheetId,
    createdAt: new Date().toISOString(),
    tabs: ['Daily Log', 'Brain Dump Archive', 'Analytics']
  };
  
  await fs.writeFile(configPath, JSON.stringify(config, null, 2));
}

module.exports = { 
  createADHDSheetV2,
  getAllSheetTabs
};
```

---

### Step 3: Add New Tab/Sheet from Dashboard

```javascript
// در backend/services/sheetService.js

async function addNewTab(spreadsheetId, tabName) {
  const auth = await getGoogleAuth();
  const sheets = google.sheets({ version: 'v4', auth });
  
  try {
    // Get all existing tabs
    const existingTabs = await getAllSheetTabs(spreadsheetId);
    const nextIndex = existingTabs.length;
    
    // Create new tab
    const result = await sheets.spreadsheets.batchUpdate({
      spreadsheetId,
      requestBody: {
        requests: [
          {
            addSheet: {
              properties: {
                title: tabName,
                index: nextIndex,
                gridProperties: {
                  rowCount: 1000,
                  columnCount: 26
                }
              }
            }
          }
        ]
      }
    });
    
    const newSheetId = result.data.replies[0].addSheet.properties.sheetId;
    
    return {
      success: true,
      sheetId: newSheetId,
      title: tabName,
      index: nextIndex
    };
    
  } catch (error) {
    throw new Error(`خطا در اضافه کردن Tab: ${error.message}`);
  }
}
```

---

### Step 4: API Endpoints

```javascript
// در backend/routes/sheets.js

const express = require('express');
const router = express.Router();
const { createADHDSheetV2, getAllSheetTabs, addNewTab } = require('../services/sheetCreator');

// Create new sheet
router.post('/create', async (req, res) => {
  try {
    const result = await createADHDSheetV2((message, progress) => {
      console.log(`[${progress}%] ${message}`);
    });
    
    res.json(result);
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get all tabs
router.get('/:spreadsheetId/tabs', async (req, res) => {
  try {
    const tabs = await getAllSheetTabs(req.params.spreadsheetId);
    res.json({ success: true, tabs });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Add new tab
router.post('/:spreadsheetId/tabs', async (req, res) => {
  try {
    const { tabName } = req.body;
    
    if (!tabName) {
      return res.status(400).json({
        success: false,
        error: 'Tab name is required'
      });
    }
    
    const result = await addNewTab(req.params.spreadsheetId, tabName);
    res.json(result);
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

module.exports = router;
```

---

### Step 5: Frontend UI

```jsx
// در frontend/src/pages/Settings.jsx

import { useState, useEffect } from 'react';
import { Button, Card, Alert, Progress, Input, Modal, List } from 'antd';
import { FileAddOutlined, PlusOutlined, FolderOutlined } from '@ant-design/icons';

function SheetManagement() {
  const [spreadsheetId, setSpreadsheetId] = useState(null);
  const [tabs, setTabs] = useState([]);
  const [isCreating, setIsCreating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [showAddTabModal, setShowAddTabModal] = useState(false);
  const [newTabName, setNewTabName] = useState('');

  useEffect(() => {
    loadSheetConfig();
  }, []);

  async function loadSheetConfig() {
    try {
      const response = await fetch('/api/config/sheet');
      const data = await response.json();
      
      if (data.success) {
        setSpreadsheetId(data.spreadsheetId);
        await loadTabs(data.spreadsheetId);
      }
    } catch (error) {
      console.error('Error loading config:', error);
    }
  }

  async function loadTabs(sheetId) {
    try {
      const response = await fetch(`/api/sheets/${sheetId}/tabs`);
      const data = await response.json();
      
      if (data.success) {
        setTabs(data.tabs);
      }
    } catch (error) {
      console.error('Error loading tabs:', error);
    }
  }

  async function handleCreateSheet() {
    setIsCreating(true);
    
    try {
      const response = await fetch('/api/sheets/create', {
        method: 'POST'
      });
      
      const data = await response.json();
      
      if (data.success) {
        setSpreadsheetId(data.spreadsheetId);
        await loadTabs(data.spreadsheetId);
      }
    } catch (error) {
      console.error('Error creating sheet:', error);
    } finally {
      setIsCreating(false);
    }
  }

  async function handleAddTab() {
    try {
      const response = await fetch(`/api/sheets/${spreadsheetId}/tabs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tabName: newTabName })
      });
      
      const data = await response.json();
      
      if (data.success) {
        await loadTabs(spreadsheetId);
        setShowAddTabModal(false);
        setNewTabName('');
      }
    } catch (error) {
      console.error('Error adding tab:', error);
    }
  }

  return (
    <div>
      <Card title="📊 مدیریت Google Sheet">
        {!spreadsheetId ? (
          <div>
            <Alert
              type="info"
              message="Sheet ای وجود ندارد"
              description="ابتدا یک Sheet جدید بسازید"
              style={{ marginBottom: 16 }}
            />
            <Button
              type="primary"
              size="large"
              icon={<FileAddOutlined />}
              onClick={handleCreateSheet}
              loading={isCreating}
            >
              🚀 ساخت Sheet جدید
            </Button>
          </div>
        ) : (
          <div>
            <Alert
              type="success"
              message="✅ Sheet موجود است"
              description={`Spreadsheet ID: ${spreadsheetId}`}
              style={{ marginBottom: 16 }}
            />
            
            <Card title="📂 Tab های موجود" style={{ marginTop: 16 }}>
              <List
                dataSource={tabs}
                renderItem={tab => (
                  <List.Item>
                    <List.Item.Meta
                      avatar={<FolderOutlined />}
                      title={tab.title}
                      description={`Sheet ID: ${tab.sheetId} | Index: ${tab.index}`}
                    />
                  </List.Item>
                )}
              />
              
              <Button
                type="dashed"
                icon={<PlusOutlined />}
                onClick={() => setShowAddTabModal(true)}
                style={{ marginTop: 16, width: '100%' }}
              >
                اضافه کردن Tab جدید
              </Button>
            </Card>
          </div>
        )}
      </Card>

      <Modal
        title="📂 اضافه کردن Tab جدید"
        open={showAddTabModal}
        onOk={handleAddTab}
        onCancel={() => setShowAddTabModal(false)}
        okText="اضافه کن"
        cancelText="لغو"
      >
        <Input
          placeholder="نام Tab (مثلاً: پروژه های هنگامه)"
          value={newTabName}
          onChange={(e) => setNewTabName(e.target.value)}
        />
      </Modal>
    </div>
  );
}

export default SheetManagement;
```

---

## 🎯 خلاصه تغییرات:

### ✅ نسبت به نسخه قبل:
1. **Auto-detect Tabs**: دیگه نیازی به تعریف دستی نیست
2. **Add Tab from Dashboard**: می‌تونی از پنل Tab جدید اضافه کنی
3. **ساختار دقیق**: مطابق با فایل فعلی (17 ستون + 12 ستون)
4. **Save to DB**: Sheet ID در دیتابیس/JSON ذخیره میشه

### ✅ Environment Variables ساده‌شده:
```env
# فقط این یکی کافیه:
GOOGLE_SHEETS_CREDENTIALS=./credentials.json

# باقی خودکار:
# - Spreadsheet ID → از DB/JSON خونده میشه
# - Tab Names → خودکار Detect میشن
```

---

موفق باشی! 🚀
