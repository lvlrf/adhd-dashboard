# 🚀 MEGA PROMPT: Dashboard Complete Update v2.1

## 🎯 خلاصه درخواست:

یک سیستم کامل مدیریت Task با این ویژگی‌ها:

### 1️⃣ مدیریت Task ها:
- ✅ تخصیص به "امروز" با تیک زدن
- ✅ Drag & Drop برای تغییر تاریخ
- ✅ ویرایش سریع inline

### 2️⃣ دسته‌بندی سفارشی:
- ✅ تماس‌ها
- ✅ لیست خرید
- ✅ کارهای خرد شخصی
- ✅ کارهای شخصی
- ✅ کارهای هنگامه
- ✅ روند پروژه (با مراحل)

### 3️⃣ سیستم تگ:
- ✅ تگ پروژه
- ✅ تگ شخص/مشتری
- ✅ تگ وابستگی

### 4️⃣ فیلترها:
- ✅ فیلتر هفته
- ✅ فیلتر ددلاین
- ✅ تارگت هفته

### 5️⃣ View های متنوع:
- ✅ List View
- ✅ Ribbon View
- ✅ Kanban View (Trello-like)
- ✅ Responsive

### 6️⃣ Recurring Tasks:
- ✅ روزانه / هفتگی / ماهانه

### 7️⃣ Notifications:
- ✅ Telegram Bot
- ✅ Google Calendar

---

## 📦 PART 1: Task Management Core

### Component: TaskCard (Improved)

```jsx
// در frontend/src/components/TaskCard.jsx

import { useState } from 'react';
import { Card, Checkbox, Tag, Button, Dropdown, Space, Tooltip } from 'antd';
import { 
  EditOutlined, 
  CalendarOutlined, 
  DeleteOutlined,
  UserOutlined,
  ProjectOutlined,
  LinkOutlined,
  BellOutlined
} from '@ant-design/icons';
import { useDrag, useDrop } from 'react-dnd';

function TaskCard({ task, onUpdate, onDelete, view = 'list' }) {
  const [isEditing, setIsEditing] = useState(false);
  
  // Drag & Drop
  const [{ isDragging }, drag] = useDrag({
    type: 'TASK',
    item: { id: task.id, currentDate: task.scheduledFor },
    collect: (monitor) => ({
      isDragging: monitor.isDragging()
    })
  });

  // تخصیص به امروز
  function assignToToday() {
    const today = new Date().toISOString().split('T')[0];
    onUpdate(task.id, { scheduledFor: today });
  }

  // نمایش آیکون دسته‌بندی
  function getCategoryIcon(category) {
    const icons = {
      'تماس‌ها': '📞',
      'لیست خرید': '🛒',
      'کارهای خرد شخصی': '✨',
      'کارهای شخصی': '🏠',
      'کارهای هنگامه': '💼',
      'پیگیری‌ها': '🔍',
      'پیش‌فاکتور': '📄',
      'تایید پرداخت': '💰',
      'دریافت تجهیزات': '📦',
      'انجام پروژه': '🔧',
      'تحویل پروژه': '✅',
      'رضایت‌نامه': '⭐',
      'آموزش': '📚',
      'پروژه عقب‌مانده': '⏰',
      'تعمیرات': '🔨',
      'ایده درآمدزایی': '💡'
    };
    return icons[category] || '📋';
  }

  // Ribbon View
  if (view === 'ribbon') {
    return (
      <div 
        ref={drag}
        style={{
          opacity: isDragging ? 0.5 : 1,
          cursor: 'move',
          padding: '8px',
          margin: '4px 0',
          background: '#fff',
          borderLeft: `4px solid ${getPriorityColor(task.importance)}`,
          borderRadius: '4px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
        }}
      >
        <Space size={4}>
          <Checkbox 
            checked={task.scheduledFor === new Date().toISOString().split('T')[0]}
            onChange={assignToToday}
          />
          <span>{getCategoryIcon(task.category)}</span>
          <span style={{ fontSize: 13 }}>{task.name}</span>
          {task.tags?.map(tag => (
            <Tag key={tag} size="small">{tag}</Tag>
          ))}
        </Space>
      </div>
    );
  }

  // Kanban View
  if (view === 'kanban') {
    return (
      <Card
        ref={drag}
        size="small"
        style={{
          opacity: isDragging ? 0.5 : 1,
          cursor: 'move',
          marginBottom: 8
        }}
        actions={[
          <Tooltip title="تخصیص به امروز">
            <Button 
              type="text" 
              icon={<CalendarOutlined />} 
              onClick={assignToToday}
            />
          </Tooltip>,
          <Tooltip title="ویرایش">
            <Button 
              type="text" 
              icon={<EditOutlined />} 
              onClick={() => setIsEditing(true)}
            />
          </Tooltip>
        ]}
      >
        <div>
          <div style={{ marginBottom: 8 }}>
            <Space>
              <span>{getCategoryIcon(task.category)}</span>
              <strong>{task.name}</strong>
            </Space>
          </div>
          
          {task.tags && (
            <div style={{ marginBottom: 8 }}>
              {task.tags.map(tag => (
                <Tag key={tag} size="small">{tag}</Tag>
              ))}
            </div>
          )}
          
          <Space size={8}>
            {task.energyLevel && (
              <Tag color={getEnergyColor(task.energyLevel)}>
                {task.energyLevel}
              </Tag>
            )}
            {task.estimatedTime && (
              <Tag>{task.estimatedTime}</Tag>
            )}
          </Space>
        </div>
      </Card>
    );
  }

  // List View (Default)
  return (
    <Card
      ref={drag}
      style={{
        opacity: isDragging ? 0.5 : 1,
        cursor: 'move',
        marginBottom: 16
      }}
      extra={
        <Space>
          <Checkbox 
            checked={task.scheduledFor === new Date().toISOString().split('T')[0]}
            onChange={assignToToday}
          >
            امروز
          </Checkbox>
          <Button icon={<EditOutlined />} onClick={() => setIsEditing(true)} />
          <Button icon={<DeleteOutlined />} onClick={() => onDelete(task.id)} danger />
        </Space>
      }
    >
      <Space direction="vertical" style={{ width: '100%' }}>
        <Space>
          <span style={{ fontSize: 18 }}>{getCategoryIcon(task.category)}</span>
          <h3>{task.name}</h3>
        </Space>
        
        {task.tags && task.tags.length > 0 && (
          <div>
            {task.tags.map(tag => {
              const tagType = tag.startsWith('👤') ? 'person' : 
                             tag.startsWith('📁') ? 'project' : 'dependency';
              return (
                <Tag 
                  key={tag}
                  icon={
                    tagType === 'person' ? <UserOutlined /> :
                    tagType === 'project' ? <ProjectOutlined /> :
                    <LinkOutlined />
                  }
                >
                  {tag}
                </Tag>
              );
            })}
          </div>
        )}
        
        <Space>
          <Tag color={getEnergyColor(task.energyLevel)}>{task.energyLevel}</Tag>
          <Tag color={getImportanceColor(task.importance)}>{task.importance}</Tag>
          <Tag>{task.estimatedTime}</Tag>
          {task.dueDate && (
            <Tag icon={<CalendarOutlined />} color="red">
              {task.dueDate}
            </Tag>
          )}
          {task.isRecurring && (
            <Tag icon={<BellOutlined />} color="purple">
              {task.recurringType}
            </Tag>
          )}
        </Space>
      </Space>
    </Card>
  );
}

function getPriorityColor(importance) {
  return importance === '🔴 High' ? '#ff4d4f' :
         importance === '🟡 Medium' ? '#faad14' : '#52c41a';
}

function getEnergyColor(energy) {
  return energy === '🔥 High' ? 'red' :
         energy === '⚡ Medium' ? 'orange' : 'green';
}

function getImportanceColor(importance) {
  return importance === '🔴 High' ? 'red' :
         importance === '🟡 Medium' ? 'gold' : 'green';
}

export default TaskCard;
```

---

## 📦 PART 2: Categories Management

### Component: CategoryManager

```jsx
// در frontend/src/components/CategoryManager.jsx

import { Select, Button, Modal, Input, Form } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useState } from 'react';

const DEFAULT_CATEGORIES = [
  { value: 'تماس‌ها', label: '📞 تماس‌ها', icon: '📞' },
  { value: 'لیست خرید', label: '🛒 لیست خرید', icon: '🛒' },
  { value: 'کارهای خرد شخصی', label: '✨ کارهای خرد شخصی', icon: '✨' },
  { value: 'کارهای شخصی', label: '🏠 کارهای شخصی', icon: '🏠' },
  { value: 'کارهای هنگامه', label: '💼 کارهای هنگامه', icon: '💼' },
];

const PROJECT_WORKFLOW_STAGES = [
  { value: 'پیگیری‌ها', label: '🔍 پیگیری‌ها (هنوز مشتری نیست)', icon: '🔍' },
  { value: 'پیش‌فاکتور', label: '📄 پیش‌فاکتور و ارسال دفاع', icon: '📄' },
  { value: 'تایید پرداخت', label: '💰 تایید پرداخت/پیش‌پرداخت', icon: '💰' },
  { value: 'دریافت تجهیزات', label: '📦 دریافت تجهیزات', icon: '📦' },
  { value: 'انجام پروژه', label: '🔧 انجام پروژه', icon: '🔧' },
  { value: 'تحویل پروژه', label: '✅ تحویل پروژه و مستندات', icon: '✅' },
  { value: 'رضایت‌نامه', label: '⭐ رضایت‌نامه و معرفی‌نامه', icon: '⭐' },
  { value: 'آموزش', label: '📚 آموزش‌ها / یادگیری‌ها', icon: '📚' },
  { value: 'پروژه عقب‌مانده', label: '⏰ پروژه‌های عقب‌مانده', icon: '⏰' },
  { value: 'تعمیرات', label: '🔨 پیگیری تعمیرات / گارانتی', icon: '🔨' },
  { value: 'ایده درآمدزایی', label: '💡 ایده‌های درآمدزایی', icon: '💡' }
];

function CategoryManager({ value, onChange }) {
  const [showAddModal, setShowAddModal] = useState(false);
  const [customCategories, setCustomCategories] = useState([]);
  const [form] = Form.useForm();

  const allCategories = [
    ...DEFAULT_CATEGORIES,
    ...PROJECT_WORKFLOW_STAGES,
    ...customCategories
  ];

  function handleAddCategory() {
    form.validateFields().then(values => {
      const newCategory = {
        value: values.name,
        label: `${values.icon} ${values.name}`,
        icon: values.icon
      };
      
      setCustomCategories([...customCategories, newCategory]);
      setShowAddModal(false);
      form.resetFields();
      
      // Save to backend/localStorage
      saveCustomCategories([...customCategories, newCategory]);
    });
  }

  async function saveCustomCategories(categories) {
    try {
      await fetch('/api/settings/categories', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ categories })
      });
    } catch (error) {
      console.error('Error saving categories:', error);
    }
  }

  return (
    <div>
      <Select
        value={value}
        onChange={onChange}
        style={{ width: '100%' }}
        placeholder="انتخاب دسته‌بندی"
        optionLabelProp="label"
        dropdownRender={menu => (
          <>
            {menu}
            <div style={{ padding: 8, borderTop: '1px solid #f0f0f0' }}>
              <Button 
                type="dashed" 
                icon={<PlusOutlined />}
                onClick={() => setShowAddModal(true)}
                block
              >
                دسته‌بندی جدید
              </Button>
            </div>
          </>
        )}
      >
        <Select.OptGroup label="دسته‌بندی‌های اصلی">
          {DEFAULT_CATEGORIES.map(cat => (
            <Select.Option key={cat.value} value={cat.value} label={cat.label}>
              {cat.label}
            </Select.Option>
          ))}
        </Select.OptGroup>
        
        <Select.OptGroup label="روند پروژه">
          {PROJECT_WORKFLOW_STAGES.map(cat => (
            <Select.Option key={cat.value} value={cat.value} label={cat.label}>
              {cat.label}
            </Select.Option>
          ))}
        </Select.OptGroup>
        
        {customCategories.length > 0 && (
          <Select.OptGroup label="دسته‌بندی‌های سفارشی">
            {customCategories.map(cat => (
              <Select.Option key={cat.value} value={cat.value} label={cat.label}>
                {cat.label}
              </Select.Option>
            ))}
          </Select.OptGroup>
        )}
      </Select>

      <Modal
        title="➕ اضافه کردن دسته‌بندی جدید"
        open={showAddModal}
        onOk={handleAddCategory}
        onCancel={() => setShowAddModal(false)}
      >
        <Form form={form} layout="vertical">
          <Form.Item 
            name="icon" 
            label="آیکون (ایموجی)"
            rules={[{ required: true, message: 'یک ایموجی انتخاب کن' }]}
          >
            <Input placeholder="مثلاً: 🎯" maxLength={2} />
          </Form.Item>
          <Form.Item 
            name="name" 
            label="نام دسته‌بندی"
            rules={[{ required: true, message: 'نام دسته‌بندی الزامی است' }]}
          >
            <Input placeholder="مثلاً: کارهای فوری" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default CategoryManager;
```

---

## 📦 PART 3: Tags System

### Component: TagsManager

```jsx
// در frontend/src/components/TagsManager.jsx

import { Select, Tag } from 'antd';
import { UserOutlined, ProjectOutlined, LinkOutlined } from '@ant-design/icons';

function TagsManager({ value = [], onChange, taskId }) {
  const [projects, setProjects] = useState([]);
  const [people, setPeople] = useState([]);

  useEffect(() => {
    loadTags();
  }, []);

  async function loadTags() {
    try {
      const response = await fetch('/api/tags');
      const data = await response.json();
      setProjects(data.projects || []);
      setPeople(data.people || []);
    } catch (error) {
      console.error('Error loading tags:', error);
    }
  }

  const allTags = [
    ...projects.map(p => ({ 
      value: `📁 ${p}`, 
      label: `📁 ${p}`,
      type: 'project' 
    })),
    ...people.map(p => ({ 
      value: `👤 ${p}`, 
      label: `👤 ${p}`,
      type: 'person' 
    }))
  ];

  function handleChange(selectedTags) {
    onChange(selectedTags);
  }

  function tagRender(props) {
    const { label, value, closable, onClose } = props;
    const type = value.startsWith('📁') ? 'project' : 
                 value.startsWith('👤') ? 'person' : 'dependency';
    
    const icon = type === 'project' ? <ProjectOutlined /> :
                 type === 'person' ? <UserOutlined /> :
                 <LinkOutlined />;
    
    const color = type === 'project' ? 'blue' :
                  type === 'person' ? 'green' : 'orange';

    return (
      <Tag
        color={color}
        closable={closable}
        onClose={onClose}
        icon={icon}
        style={{ marginRight: 3 }}
      >
        {label}
      </Tag>
    );
  }

  return (
    <Select
      mode="tags"
      value={value}
      onChange={handleChange}
      style={{ width: '100%' }}
      placeholder="انتخاب تگ (پروژه، شخص، وابستگی)"
      tagRender={tagRender}
      options={allTags}
    />
  );
}

export default TagsManager;
```

---

## 📦 PART 4: View Switcher

### Component: ViewSwitcher

```jsx
// در frontend/src/pages/TasksPage.jsx

import { Radio, Row, Col } from 'antd';
import { UnorderedListOutlined, AppstoreOutlined, TableOutlined } from '@ant-design/icons';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { useState } from 'react';

function TasksPage() {
  const [view, setView] = useState('list'); // 'list', 'ribbon', 'kanban'
  const [tasks, setTasks] = useState([]);

  return (
    <DndProvider backend={HTML5Backend}>
      <div style={{ padding: 24 }}>
        <Row justify="space-between" style={{ marginBottom: 16 }}>
          <Col>
            <h1>📋 لیست کارها</h1>
          </Col>
          <Col>
            <Radio.Group value={view} onChange={(e) => setView(e.target.value)}>
              <Radio.Button value="list">
                <UnorderedListOutlined /> لیست
              </Radio.Button>
              <Radio.Button value="ribbon">
                <TableOutlined /> ریبونی
              </Radio.Button>
              <Radio.Button value="kanban">
                <AppstoreOutlined /> کانبان
              </Radio.Button>
            </Radio.Group>
          </Col>
        </Row>

        {view === 'list' && <ListView tasks={tasks} />}
        {view === 'ribbon' && <RibbonView tasks={tasks} />}
        {view === 'kanban' && <KanbanView tasks={tasks} />}
      </div>
    </DndProvider>
  );
}
```

### ListView Component

```jsx
function ListView({ tasks }) {
  return (
    <div>
      {tasks.map(task => (
        <TaskCard key={task.id} task={task} view="list" />
      ))}
    </div>
  );
}
```

### RibbonView Component

```jsx
function RibbonView({ tasks }) {
  // Group by category
  const grouped = tasks.reduce((acc, task) => {
    const category = task.category || 'بدون دسته';
    if (!acc[category]) acc[category] = [];
    acc[category].push(task);
    return acc;
  }, {});

  return (
    <div style={{ display: 'flex', gap: 16, overflowX: 'auto' }}>
      {Object.entries(grouped).map(([category, categoryTasks]) => (
        <div 
          key={category}
          style={{
            minWidth: 280,
            background: '#f5f5f5',
            padding: 12,
            borderRadius: 8
          }}
        >
          <h3>{category} ({categoryTasks.length})</h3>
          <div>
            {categoryTasks.map(task => (
              <TaskCard key={task.id} task={task} view="ribbon" />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
```

### KanbanView Component

```jsx
import { useDrop } from 'react-dnd';

function KanbanView({ tasks }) {
  const statuses = ['Inbox', 'Next Action', 'In Progress', 'Waiting', 'Done'];

  function KanbanColumn({ status, tasks }) {
    const [{ isOver }, drop] = useDrop({
      accept: 'TASK',
      drop: (item) => {
        handleDrop(item.id, status);
      },
      collect: (monitor) => ({
        isOver: monitor.isOver()
      })
    });

    return (
      <div
        ref={drop}
        style={{
          minWidth: 280,
          background: isOver ? '#e6f7ff' : '#f5f5f5',
          padding: 12,
          borderRadius: 8,
          minHeight: 400
        }}
      >
        <h3>{status} ({tasks.length})</h3>
        <div>
          {tasks.map(task => (
            <TaskCard key={task.id} task={task} view="kanban" />
          ))}
        </div>
      </div>
    );
  }

  async function handleDrop(taskId, newStatus) {
    try {
      await fetch(`/api/tasks/${taskId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });
      // Reload tasks
    } catch (error) {
      console.error('Error updating task:', error);
    }
  }

  return (
    <div style={{ display: 'flex', gap: 16, overflowX: 'auto' }}>
      {statuses.map(status => {
        const statusTasks = tasks.filter(t => t.status === status);
        return (
          <KanbanColumn key={status} status={status} tasks={statusTasks} />
        );
      })}
    </div>
  );
}
```

---

## 📦 PART 5: Filters System

### Component: TaskFilters

```jsx
// در frontend/src/components/TaskFilters.jsx

import { Row, Col, Select, DatePicker, Button, Space } from 'antd';
import { FilterOutlined, ClearOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';

function TaskFilters({ filters, onFilterChange, onClearFilters }) {
  return (
    <div style={{ 
      background: '#fafafa', 
      padding: 16, 
      borderRadius: 8,
      marginBottom: 16 
    }}>
      <Row gutter={[16, 16]} align="middle">
        <Col xs={24} sm={12} md={6}>
          <Select
            placeholder="🗓️ فیلتر هفته"
            style={{ width: '100%' }}
            value={filters.week}
            onChange={(value) => onFilterChange('week', value)}
            allowClear
          >
            <Select.Option value="current">هفته جاری</Select.Option>
            <Select.Option value="next">هفته بعد</Select.Option>
            <Select.Option value="this-month">این ماه</Select.Option>
          </Select>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Select
            placeholder="⏰ فیلتر ددلاین"
            style={{ width: '100%' }}
            value={filters.deadline}
            onChange={(value) => onFilterChange('deadline', value)}
            allowClear
          >
            <Select.Option value="overdue">عقب‌افتاده</Select.Option>
            <Select.Option value="today">امروز</Select.Option>
            <Select.Option value="tomorrow">فردا</Select.Option>
            <Select.Option value="this-week">این هفته</Select.Option>
          </Select>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Select
            placeholder="📋 دسته‌بندی"
            style={{ width: '100%' }}
            value={filters.category}
            onChange={(value) => onFilterChange('category', value)}
            allowClear
          >
            <Select.Option value="تماس‌ها">📞 تماس‌ها</Select.Option>
            <Select.Option value="لیست خرید">🛒 لیست خرید</Select.Option>
            <Select.Option value="کارهای شخصی">🏠 کارهای شخصی</Select.Option>
            <Select.Option value="کارهای هنگامه">💼 کارهای هنگامه</Select.Option>
          </Select>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Space>
            <Button 
              icon={<FilterOutlined />}
              onClick={() => {/* Apply filters */}}
            >
              اعمال
            </Button>
            <Button 
              icon={<ClearOutlined />}
              onClick={onClearFilters}
            >
              پاک کردن
            </Button>
          </Space>
        </Col>
      </Row>

      {/* تارگت هفته */}
      <Row style={{ marginTop: 16 }}>
        <Col span={24}>
          <div style={{ 
            background: '#fff', 
            padding: 12, 
            borderRadius: 6,
            border: '2px dashed #1890ff'
          }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <strong>🎯 تارگت این هفته:</strong>
              <Select
                mode="multiple"
                placeholder="کارهایی که این هفته باید حتماً انجام بشن"
                style={{ width: '100%' }}
                value={filters.weekTarget}
                onChange={(value) => onFilterChange('weekTarget', value)}
              >
                {/* Load tasks dynamically */}
              </Select>
            </Space>
          </div>
        </Col>
      </Row>
    </div>
  );
}

export default TaskFilters;
```

---

## 📦 PART 6: Recurring Tasks

### Component: RecurringTaskForm

```jsx
// در frontend/src/components/RecurringTaskForm.jsx

import { Form, Select, InputNumber, Checkbox, Space } from 'antd';

function RecurringTaskForm() {
  return (
    <>
      <Form.Item 
        name="isRecurring" 
        valuePropName="checked"
      >
        <Checkbox>🔁 این کار تکرارشونده است</Checkbox>
      </Form.Item>

      <Form.Item
        noStyle
        shouldUpdate={(prev, curr) => prev.isRecurring !== curr.isRecurring}
      >
        {({ getFieldValue }) =>
          getFieldValue('isRecurring') ? (
            <>
              <Form.Item
                name="recurringType"
                label="نوع تکرار"
                rules={[{ required: true }]}
              >
                <Select placeholder="انتخاب نوع تکرار">
                  <Select.Option value="daily">روزانه</Select.Option>
                  <Select.Option value="weekly">هفتگی</Select.Option>
                  <Select.Option value="monthly">ماهانه</Select.Option>
                  <Select.Option value="custom">سفارشی</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="recurringInterval"
                label="هر چند وقت یکبار؟"
              >
                <InputNumber 
                  min={1} 
                  placeholder="مثلاً: 2 (هر 2 روز)" 
                  style={{ width: '100%' }}
                />
              </Form.Item>

              <Form.Item
                name="recurringDays"
                label="روزهای هفته (برای تکرار هفتگی)"
              >
                <Checkbox.Group>
                  <Checkbox value="saturday">شنبه</Checkbox>
                  <Checkbox value="sunday">یکشنبه</Checkbox>
                  <Checkbox value="monday">دوشنبه</Checkbox>
                  <Checkbox value="tuesday">سه‌شنبه</Checkbox>
                  <Checkbox value="wednesday">چهارشنبه</Checkbox>
                  <Checkbox value="thursday">پنجشنبه</Checkbox>
                  <Checkbox value="friday">جمعه</Checkbox>
                </Checkbox.Group>
              </Form.Item>

              <Form.Item
                name="recurringEndDate"
                label="تاریخ پایان تکرار (اختیاری)"
              >
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </>
          ) : null
        }
      </Form.Item>
    </>
  );
}

export default RecurringTaskForm;
```

### Backend: Recurring Tasks Scheduler

```javascript
// در backend/services/recurringTasksScheduler.js

const cron = require('node-cron');

// Run every day at midnight
cron.schedule('0 0 * * *', async () => {
  console.log('🔄 Checking recurring tasks...');
  await createRecurringTasks();
});

async function createRecurringTasks() {
  const recurringTasks = await db.query(`
    SELECT * FROM tasks 
    WHERE is_recurring = true 
    AND status != 'Done'
  `);

  for (const task of recurringTasks) {
    if (shouldCreateToday(task)) {
      await createTaskInstance(task);
    }
  }
}

function shouldCreateToday(task) {
  const today = new Date();
  const lastCreated = task.last_created_at ? new Date(task.last_created_at) : null;

  if (task.recurring_type === 'daily') {
    // Check if we already created today
    if (lastCreated && isSameDay(lastCreated, today)) {
      return false;
    }
    return true;
  }

  if (task.recurring_type === 'weekly') {
    const dayOfWeek = today.toLocaleDateString('en-US', { weekday: 'lowercase' });
    return task.recurring_days.includes(dayOfWeek);
  }

  if (task.recurring_type === 'monthly') {
    const dayOfMonth = today.getDate();
    return dayOfMonth === task.recurring_day_of_month;
  }

  return false;
}

async function createTaskInstance(task) {
  const newTask = {
    ...task,
    id: undefined,
    parent_recurring_id: task.id,
    scheduled_for: new Date().toISOString().split('T')[0],
    status: 'Next Action',
    created_at: new Date()
  };

  await db.query('INSERT INTO tasks SET ?', newTask);
  await db.query(
    'UPDATE tasks SET last_created_at = NOW() WHERE id = ?',
    [task.id]
  );
}

function isSameDay(date1, date2) {
  return date1.toDateString() === date2.toDateString();
}

module.exports = { createRecurringTasks };
```

---

## 📦 PART 7: Notifications System

### Telegram Bot Integration

```javascript
// در backend/services/telegramBot.js

const TelegramBot = require('node-telegram-bot-api');

const bot = new TelegramBot(process.env.TELEGRAM_BOT_TOKEN, { polling: true });

// Start command
bot.onText(/\/start/, async (msg) => {
  const chatId = msg.chat.id;
  
  await bot.sendMessage(chatId, `
سلام! 👋
من ربات یادآوری کارهای ADHD تو هستم.

برای فعال‌سازی، این کد رو وارد کن:
🔑 ${await generateActivationCode(chatId)}
  `);
});

async function generateActivationCode(chatId) {
  const code = Math.random().toString(36).substring(7).toUpperCase();
  
  await db.query(
    'INSERT INTO telegram_activations (chat_id, code, expires_at) VALUES (?, ?, DATE_ADD(NOW(), INTERVAL 10 MINUTE))',
    [chatId, code]
  );
  
  return code;
}

// Send notification
async function sendTaskReminder(userId, task) {
  const user = await db.query(
    'SELECT telegram_chat_id FROM users WHERE id = ?',
    [userId]
  );
  
  if (!user[0]?.telegram_chat_id) return;

  const message = `
⏰ یادآوری کار!

📋 ${task.name}
📁 ${task.category}
⏰ ددلاین: ${task.due_date}
⚡ انرژی: ${task.energy_level}

🔗 [مشاهده جزئیات](${process.env.APP_URL}/tasks/${task.id})
  `;

  await bot.sendMessage(user[0].telegram_chat_id, message, {
    parse_mode: 'Markdown'
  });
}

// Check tasks every hour
const cron = require('node-cron');
cron.schedule('0 * * * *', async () => {
  const tasks = await getTasksDueInNext24Hours();
  
  for (const task of tasks) {
    await sendTaskReminder(task.user_id, task);
  }
});

module.exports = { bot, sendTaskReminder };
```

### Google Calendar Integration

```javascript
// در backend/services/googleCalendar.js

const { google } = require('googleapis');

async function addTaskToCalendar(task, userCalendarId) {
  const auth = await getGoogleAuth();
  const calendar = google.calendar({ version: 'v3', auth });

  const event = {
    summary: task.name,
    description: `
📋 کار: ${task.name}
📁 دسته: ${task.category}
⚡ انرژی: ${task.energy_level}
🔴 اهمیت: ${task.importance}

🔗 لینک: ${process.env.APP_URL}/tasks/${task.id}
    `,
    start: {
      dateTime: new Date(task.scheduled_for).toISOString(),
      timeZone: 'Asia/Tehran'
    },
    end: {
      dateTime: new Date(task.scheduled_for + ' 23:59:59').toISOString(),
      timeZone: 'Asia/Tehran'
    },
    reminders: {
      useDefault: false,
      overrides: [
        { method: 'popup', minutes: 30 },
        { method: 'email', minutes: 60 }
      ]
    },
    colorId: getColorForImportance(task.importance)
  };

  const response = await calendar.events.insert({
    calendarId: userCalendarId,
    requestBody: event
  });

  return response.data;
}

function getColorForImportance(importance) {
  return importance === '🔴 High' ? '11' : // Red
         importance === '🟡 Medium' ? '5' : // Yellow
         '10'; // Green
}

// Sync on task create/update
async function syncTaskToCalendar(task, userId) {
  const user = await db.query(
    'SELECT google_calendar_id FROM users WHERE id = ?',
    [userId]
  );

  if (!user[0]?.google_calendar_id) return;

  await addTaskToCalendar(task, user[0].google_calendar_id);
}

module.exports = { addTaskToCalendar, syncTaskToCalendar };
```

---

## 📦 PART 8: Responsive Design

### CSS/Tailwind for Responsive

```css
/* در frontend/src/styles/responsive.css */

/* Mobile First Approach */
@media (max-width: 576px) {
  .task-card {
    padding: 8px;
    font-size: 14px;
  }

  .task-filters {
    flex-direction: column;
  }

  .view-switcher {
    width: 100%;
  }

  .kanban-column {
    min-width: 100%;
    margin-bottom: 16px;
  }

  .ribbon-view {
    flex-direction: column;
  }
}

/* Tablet */
@media (min-width: 577px) and (max-width: 992px) {
  .kanban-column {
    min-width: 45%;
  }

  .ribbon-view {
    flex-wrap: wrap;
  }
}

/* Desktop */
@media (min-width: 993px) {
  .kanban-column {
    min-width: 280px;
  }

  .task-card {
    transition: transform 0.2s, box-shadow 0.2s;
  }

  .task-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
}
```

---

## 🎯 خلاصه API Endpoints:

```javascript
// Tasks
GET    /api/tasks                    // لیست کارها (با فیلتر)
POST   /api/tasks                    // ایجاد کار جدید
PATCH  /api/tasks/:id                // بروزرسانی کار
DELETE /api/tasks/:id                // حذف کار
POST   /api/tasks/:id/assign-today   // تخصیص به امروز

// Categories
GET    /api/categories               // لیست دسته‌بندی‌ها
POST   /api/categories               // اضافه کردن دسته‌بندی

// Tags
GET    /api/tags                     // لیست تگ‌ها
POST   /api/tags                     // اضافه کردن تگ

// Recurring
POST   /api/recurring-tasks          // ایجاد کار تکرارشونده

// Notifications
POST   /api/telegram/activate        // فعال‌سازی Telegram
POST   /api/calendar/sync            // همگام‌سازی با Google Calendar
```

---

## 💡 نکات پیاده‌سازی:

### 1. Dependencies:
```bash
npm install react-dnd react-dnd-html5-backend
npm install node-telegram-bot-api
npm install googleapis
npm install node-cron
npm install dayjs
```

### 2. Environment Variables:
```env
TELEGRAM_BOT_TOKEN=your_bot_token
GOOGLE_CALENDAR_CREDENTIALS=./calendar-credentials.json
APP_URL=http://localhost:3000
```

### 3. Database Schema Updates:
```sql
ALTER TABLE tasks ADD COLUMN category VARCHAR(100);
ALTER TABLE tasks ADD COLUMN tags JSON;
ALTER TABLE tasks ADD COLUMN is_recurring BOOLEAN DEFAULT FALSE;
ALTER TABLE tasks ADD COLUMN recurring_type ENUM('daily', 'weekly', 'monthly', 'custom');
ALTER TABLE tasks ADD COLUMN recurring_days JSON;
ALTER TABLE tasks ADD COLUMN last_created_at DATETIME;

CREATE TABLE custom_categories (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  name VARCHAR(100),
  icon VARCHAR(10),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE telegram_activations (
  id INT PRIMARY KEY AUTO_INCREMENT,
  chat_id BIGINT,
  code VARCHAR(20),
  expires_at DATETIME,
  activated BOOLEAN DEFAULT FALSE
);
```

---

موفق باشی! 🚀

این یک سیستم کامل و حرفه‌ای است! 💪
