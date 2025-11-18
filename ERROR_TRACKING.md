# 🔍 نظام تتبع الأخطاء المحلي | Local Error Tracking System

## 📋 نظرة عامة | Overview

هذا البوت يحتوي على نظام تتبع أخطاء محلي متقدم يسجل جميع الأخطاء بتفاصيل كاملة في ملفات السجلات، مما يسهل تحديد وحل المشاكل بسرعة.

This bot includes an advanced local error tracking system that logs all errors with full details in log files, making it easy to identify and resolve issues quickly.

## 📁 ملفات السجلات | Log Files

### 1. **logs/tax_bot.log**
- السجل الرئيسي لجميع العمليات
- Main log for all operations
- يحتوي على: INFO, WARNING, ERROR
- التدوير: كل 10 MB
- الاحتفاظ: 30 يوم

### 2. **logs/errors.log**
- سجل خاص بالأخطاء فقط
- Errors only log
- يحتوي على تفاصيل كاملة مع Stack Trace
- التدوير: كل 5 MB
- الاحتفاظ: 90 يوم

### 3. **logs/errors_detailed.jsonl**
- ملف JSON لكل خطأ (سطر واحد لكل خطأ)
- JSON file for each error (one line per error)
- سهل التحليل البرمجي
- Easy for programmatic analysis

## 🎯 ما يتم تسجيله | What Gets Logged

### معلومات أساسية | Basic Information
- ⏰ التوقيت الدقيق | Exact timestamp
- 🏷️ نوع الخطأ | Error type
- 📝 رسالة الخطأ | Error message
- ⚙️ العملية التي حدث فيها الخطأ | Operation where error occurred

### معلومات السياق | Context Information
- 👤 معرف المستخدم | User ID (if applicable)
- 💬 نص الرسالة | Message text
- 🔘 البيانات المرسلة | Callback data
- 📊 معلومات إضافية | Additional context

### معلومات تقنية | Technical Information
- 📜 Stack Trace كامل | Full stack trace
- 📂 المسار والملف | File path
- 🔢 رقم السطر | Line number
- 🔍 المتغيرات المحلية | Local variables
- 🗂️ تفاصيل كل Frame في التتبع | Details of each traceback frame

## 🚀 كيفية الاستخدام | How to Use

### في الكود | In Code

```python
from bot.utils import track_error

try:
    # Your code here
    result = calculate_tax(income)
except Exception as e:
    track_error(
        error=e,
        context={'income': income, 'tax_class': tax_class},
        user_id=user.id,
        operation='calculate_tax'
    )
```

### مثال على سجل خطأ | Error Log Example

```
================================================================================
🚨 خطأ جديد | NEW ERROR
================================================================================
⏰ التوقيت | Time: 2024-01-15T14:30:45.123456
🏷️  نوع الخطأ | Error Type: ValueError
📝 رسالة الخطأ | Message: Invalid income value: -1000
⚙️  العملية | Operation: calculate_tax
👤 المستخدم | User ID: 123456789
📊 السياق | Context: {
  "income": -1000,
  "tax_class": 1,
  "chat_id": 987654321
}

📜 Stack Trace:
Traceback (most recent call last):
  File "/app/bot/services/tax_calculator.py", line 45, in calculate_net_income
    if annual_gross <= 0:
        raise ValueError(f"Invalid income value: {annual_gross}")
ValueError: Invalid income value: -1000

🔍 تفاصيل التتبع | Traceback Details:

  Frame #1:
    File: /app/bot/handlers/calculation.py
    Function: receive_income
    Line: 67

  Frame #2:
    File: /app/bot/services/tax_calculator.py
    Function: calculate_net_income
    Line: 45

================================================================================
```

## 📊 إحصائيات الأخطاء | Error Statistics

عند بدء البوت، يعرض إحصائيات عن الأخطاء السابقة:

When the bot starts, it displays statistics about previous errors:

```
📊 Previous errors detected: 15
   Most common: ValueError
   Problematic operation: calculate_tax
```

## 🔧 الحصول على الإحصائيات برمجياً | Get Statistics Programmatically

```python
from bot.utils import error_tracker

# Get statistics
stats = error_tracker.get_error_statistics()
print(f"Total errors: {stats['total']}")
print(f"Most common error: {stats['most_common_error']}")
print(f"Affected users: {stats['affected_users']}")

# Get recent errors
recent_errors = error_tracker.get_recent_errors(limit=10)
for error in recent_errors:
    print(f"{error['timestamp']}: {error['error_type']}")
```

## 📈 تحليل الأخطاء | Error Analysis

### عرض آخر 20 خطأ | View Last 20 Errors

```bash
tail -n 100 logs/errors.log
```

### البحث عن خطأ معين | Search for Specific Error

```bash
grep "ValueError" logs/errors.log
```

### عرض أخطاء مستخدم معين | View Errors for Specific User

```bash
grep "User ID: 123456789" logs/errors.log
```

### تحليل ملف JSON | Analyze JSON File

```python
import json

errors = []
with open('logs/errors_detailed.jsonl', 'r') as f:
    for line in f:
        errors.append(json.loads(line))

# Count errors by type
from collections import Counter
error_types = Counter(e['error_type'] for e in errors)
print(error_types.most_common(5))
```

## ⚙️ الإعدادات | Configuration

في ملف `.env`:

```env
# Logging Configuration
LOG_LEVEL=INFO                      # مستوى التسجيل: DEBUG, INFO, WARNING, ERROR
LOG_FILE=logs/tax_bot.log          # ملف السجل الرئيسي
ERROR_LOG_FILE=logs/errors.log     # ملف سجل الأخطاء
ENABLE_DETAILED_ERRORS=true        # تفعيل التسجيل المفصل
ENABLE_STACK_TRACE=true            # تفعيل Stack Trace
```

## 🎨 ألوان السجلات | Log Colors

في Console:
- 🟢 **INFO**: أخضر | Green
- 🟡 **WARNING**: أصفر | Yellow
- 🔴 **ERROR**: أحمر | Red

## 📌 نصائح مهمة | Important Tips

### 1. مراقبة السجلات بشكل دوري
```bash
# في الوقت الفعلي
tail -f logs/errors.log

# آخر 50 سطر
tail -n 50 logs/errors.log
```

### 2. تنظيف السجلات القديمة
السجلات تحذف تلقائياً:
- logs/tax_bot.log: بعد 30 يوم
- logs/errors.log: بعد 90 يوم

### 3. النسخ الاحتياطي
```bash
# نسخ سجلات الأخطاء
cp logs/errors.log backups/errors_$(date +%Y%m%d).log
```

### 4. التنبيهات التلقائية
يمكن إنشاء سكريبت للتنبيه عند حدوث أخطاء:

```bash
#!/bin/bash
# check_errors.sh

ERROR_COUNT=$(tail -n 100 logs/errors.log | grep "ERROR" | wc -l)

if [ $ERROR_COUNT -gt 10 ]; then
    echo "⚠️ Warning: $ERROR_COUNT errors in last 100 lines!"
    # يمكن إرسال إشعار هنا
fi
```

## 🐛 حل المشاكل الشائعة | Common Issues Troubleshooting

### الخطأ: ValueError في حساب الضرائب
**السبب**: إدخال قيمة سالبة أو غير صالحة
**الحل**: التحقق من صحة المدخلات قبل الحساب

### الخطأ: Database connection failed
**السبب**: ملف قاعدة البيانات مفقود أو محمي
**الحل**:
```bash
mkdir -p data
chmod 755 data
```

### الخطأ: Telegram API timeout
**السبب**: مشاكل في الاتصال بالإنترنت
**الحل**: التحقق من الاتصال، إعادة تشغيل البوت

## 📱 مثال: تتبع خطأ في حساب الضرائب

```python
# في bot/handlers/calculation.py

try:
    result = tax_calculator.calculate_net_income(
        annual_gross=gross_income,
        tax_class=tax_class,
        children=children,
        church_tax=church_tax
    )
except ValueError as e:
    # تسجيل الخطأ مع جميع التفاصيل
    track_error(
        error=e,
        context={
            'gross_income': gross_income,
            'tax_class': tax_class,
            'children': children,
            'church_tax': church_tax,
            'operation_step': 'tax_calculation'
        },
        user_id=user.id,
        operation='calculate_net_income'
    )
    # إشعار المستخدم
    await update.message.reply_text("حدث خطأ في الحساب")
```

## 🔒 الأمان | Security

- ✅ لا يتم تسجيل معلومات حساسة (كلمات المرور، tokens)
- ✅ معرفات المستخدمين فقط، بدون أسماء
- ✅ السجلات محفوظة محلياً فقط
- ✅ لا مشاركة مع أطراف خارجية

## 📚 مراجع إضافية | Additional References

- [Loguru Documentation](https://loguru.readthedocs.io/)
- [Python Logging Best Practices](https://docs.python.org/3/howto/logging.html)
- [Error Handling in Python](https://docs.python.org/3/tutorial/errors.html)

---

**ملاحظة**: نظام تتبع الأخطاء هذا محلي 100% ولا يحتاج لخدمات خارجية.

**Note**: This error tracking system is 100% local and doesn't require external services.
