# 🚀 دليل سريع لتتبع الأخطاء | Quick Error Tracking Guide

## 📋 الملفات الرئيسية | Main Files

```
logs/
├── tax_bot.log              # جميع العمليات | All operations
├── errors.log               # الأخطاء فقط | Errors only
└── errors_detailed.jsonl    # تفاصيل JSON | JSON details
```

## 🔍 عرض الأخطاء | View Errors

### في الوقت الفعلي | Real-time
```bash
tail -f logs/errors.log
```

### آخر 20 خطأ | Last 20 Errors
```bash
tail -n 20 logs/errors.log
```

### البحث عن خطأ معين | Search for Error
```bash
grep "ValueError" logs/errors.log
```

## 📊 مثال على خطأ مسجل | Example Error Log

```
================================================================================
🚨 خطأ جديد | NEW ERROR
================================================================================
⏰ التوقيت | Time: 2024-01-15T14:30:45.123456
🏷️  نوع الخطأ | Error Type: ValueError
📝 رسالة الخطأ | Message: Invalid income value: -1000
⚙️  العملية | Operation: calculate_tax
👤 المستخدم | User ID: 123456789
📊 السياق | Context:
{
  "income": -1000,
  "tax_class": 1
}

📜 Stack Trace:
[Full traceback here...]

🔍 تفاصيل التتبع | Traceback Details:
  Frame #1: /app/bot/handlers/calculation.py:67
  Frame #2: /app/bot/services/tax_calculator.py:45
================================================================================
```

## 💻 استخدام في الكود | Usage in Code

```python
from bot.utils import track_error

try:
    result = calculate_something(data)
except Exception as e:
    track_error(
        error=e,
        context={'input': data},
        user_id=user_id,
        operation='calculate_something'
    )
```

## 📈 الحصول على الإحصائيات | Get Statistics

```python
from bot.utils import error_tracker

stats = error_tracker.get_error_statistics()
print(f"Total errors: {stats['total']}")
print(f"Most common: {stats['most_common_error']}")
```

## 🔧 تحليل JSON | Analyze JSON

```python
import json

# قراءة آخر 10 أخطاء | Read last 10 errors
with open('logs/errors_detailed.jsonl', 'r') as f:
    lines = f.readlines()
    for line in lines[-10:]:
        error = json.loads(line)
        print(f"{error['timestamp']}: {error['error_type']}")
```

## ⚙️ الإعدادات | Settings

في ملف `.env`:

```env
# المستوى | Level
LOG_LEVEL=INFO

# الملفات | Files
LOG_FILE=logs/tax_bot.log
ERROR_LOG_FILE=logs/errors.log

# التفاصيل | Details
ENABLE_DETAILED_ERRORS=true
ENABLE_STACK_TRACE=true
```

## 🎨 الألوان في Console | Console Colors

- 🟢 **INFO** - معلومات عامة
- 🟡 **WARNING** - تحذيرات
- 🔴 **ERROR** - أخطاء

## 📱 أمثلة سريعة | Quick Examples

### 1. مراقبة الأخطاء أثناء التشغيل
```bash
# في نافذة منفصلة
tail -f logs/errors.log
```

### 2. عد الأخطاء
```bash
grep "ERROR" logs/errors.log | wc -l
```

### 3. أخطاء اليوم
```bash
grep "$(date +%Y-%m-%d)" logs/errors.log
```

### 4. أكثر الأخطاء شيوعاً
```bash
grep "Error Type:" logs/errors.log | sort | uniq -c | sort -rn | head -5
```

## 🔒 الأمان | Security

- ✅ كل شيء محلي
- ✅ لا إرسال لخوادم خارجية
- ✅ السجلات آمنة
- ✅ حذف تلقائي للسجلات القديمة

## 📚 المزيد من التفاصيل | More Details

راجع [ERROR_TRACKING.md](ERROR_TRACKING.md) للوثائق الكاملة

See [ERROR_TRACKING.md](ERROR_TRACKING.md) for complete documentation
