"""
Enhanced Local Error Tracking System
تتبع الأخطاء المحلي المحسّن مع تفاصيل كاملة
"""
import traceback
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger
import json


class ErrorTracker:
    """نظام تتبع الأخطاء المحلي مع تفاصيل شاملة"""

    def __init__(self, error_log_file: str = 'logs/errors.log'):
        self.error_log_file = error_log_file
        self.setup_error_logging()

    def setup_error_logging(self):
        """إعداد ملف سجل الأخطاء المنفصل"""
        # إنشاء مجلد السجلات إذا لم يكن موجوداً
        Path(self.error_log_file).parent.mkdir(parents=True, exist_ok=True)

        # إضافة ملف خاص بالأخطاء فقط
        logger.add(
            self.error_log_file,
            format="<red>{time:YYYY-MM-DD HH:mm:ss}</red> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="ERROR",
            rotation="10 MB",
            retention="90 days",
            compression="zip",
            enqueue=True,
            backtrace=True,
            diagnose=True,
        )

    def track_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None,
        operation: Optional[str] = None
    ):
        """
        تتبع خطأ مع تفاصيل كاملة

        Args:
            error: الخطأ الذي حدث
            context: معلومات إضافية عن السياق
            user_id: معرف المستخدم (إن وجد)
            operation: العملية التي كانت تجري
        """
        # جمع معلومات الخطأ
        error_info = {
            'timestamp': datetime.utcnow().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'operation': operation or 'unknown',
            'user_id': user_id,
            'context': context or {},
        }

        # الحصول على Stack Trace الكامل
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if exc_traceback:
            tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            error_info['stack_trace'] = ''.join(tb_lines)
            error_info['traceback_details'] = self._extract_traceback_details(exc_traceback)

        # تسجيل الخطأ بشكل مفصل
        error_log = self._format_error_log(error_info)
        logger.error(error_log)

        # حفظ تفاصيل الخطأ في ملف JSON منفصل للتحليل السريع
        self._save_error_json(error_info)

        return error_info

    def _extract_traceback_details(self, tb) -> list:
        """استخراج تفاصيل Stack Trace بشكل منظم"""
        details = []
        while tb is not None:
            frame = tb.tb_frame
            details.append({
                'file': frame.f_code.co_filename,
                'function': frame.f_code.co_name,
                'line': tb.tb_lineno,
                'locals': {k: str(v)[:100] for k, v in frame.f_locals.items()}  # أول 100 حرف من كل متغير
            })
            tb = tb.tb_next
        return details

    def _format_error_log(self, error_info: Dict[str, Any]) -> str:
        """تنسيق رسالة الخطأ بشكل واضح وسهل القراءة"""
        log_parts = [
            "\n" + "="*80,
            "🚨 خطأ جديد | NEW ERROR",
            "="*80,
            f"⏰ التوقيت | Time: {error_info['timestamp']}",
            f"🏷️  نوع الخطأ | Error Type: {error_info['error_type']}",
            f"📝 رسالة الخطأ | Message: {error_info['error_message']}",
            f"⚙️  العملية | Operation: {error_info['operation']}",
        ]

        if error_info.get('user_id'):
            log_parts.append(f"👤 المستخدم | User ID: {error_info['user_id']}")

        if error_info.get('context'):
            log_parts.append(f"📊 السياق | Context: {json.dumps(error_info['context'], indent=2, ensure_ascii=False)}")

        if error_info.get('stack_trace'):
            log_parts.append("\n📜 Stack Trace:")
            log_parts.append(error_info['stack_trace'])

        if error_info.get('traceback_details'):
            log_parts.append("\n🔍 تفاصيل التتبع | Traceback Details:")
            for i, detail in enumerate(error_info['traceback_details'], 1):
                log_parts.append(f"\n  Frame #{i}:")
                log_parts.append(f"    File: {detail['file']}")
                log_parts.append(f"    Function: {detail['function']}")
                log_parts.append(f"    Line: {detail['line']}")

        log_parts.append("="*80 + "\n")

        return "\n".join(log_parts)

    def _save_error_json(self, error_info: Dict[str, Any]):
        """حفظ تفاصيل الخطأ في ملف JSON للتحليل السريع"""
        try:
            json_file = Path('logs/errors_detailed.jsonl')
            json_file.parent.mkdir(parents=True, exist_ok=True)

            # حفظ كل خطأ في سطر منفصل (JSONL format)
            with open(json_file, 'a', encoding='utf-8') as f:
                json.dump(error_info, f, ensure_ascii=False)
                f.write('\n')

        except Exception as e:
            logger.warning(f"Failed to save error JSON: {e}")

    def get_recent_errors(self, limit: int = 10) -> list:
        """الحصول على آخر الأخطاء من ملف JSON"""
        try:
            json_file = Path('logs/errors_detailed.jsonl')
            if not json_file.exists():
                return []

            errors = []
            with open(json_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    try:
                        errors.append(json.loads(line))
                    except:
                        continue

            return errors

        except Exception as e:
            logger.warning(f"Failed to read error JSON: {e}")
            return []

    def get_error_statistics(self) -> Dict[str, Any]:
        """إحصائيات عن الأخطاء"""
        errors = self.get_recent_errors(limit=100)

        if not errors:
            return {'total': 0}

        # تحليل الأخطاء
        error_types = {}
        operations = {}
        users = {}

        for error in errors:
            # حساب أنواع الأخطاء
            error_type = error.get('error_type', 'Unknown')
            error_types[error_type] = error_types.get(error_type, 0) + 1

            # حساب العمليات
            operation = error.get('operation', 'unknown')
            operations[operation] = operations.get(operation, 0) + 1

            # حساب المستخدمين
            user_id = error.get('user_id')
            if user_id:
                users[user_id] = users.get(user_id, 0) + 1

        return {
            'total': len(errors),
            'error_types': error_types,
            'operations': operations,
            'affected_users': len(users),
            'most_common_error': max(error_types.items(), key=lambda x: x[1])[0] if error_types else None,
            'most_problematic_operation': max(operations.items(), key=lambda x: x[1])[0] if operations else None,
        }


# Global instance
error_tracker = ErrorTracker()


def track_error(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    user_id: Optional[int] = None,
    operation: Optional[str] = None
):
    """
    دالة مساعدة سريعة لتتبع الأخطاء

    Usage:
        try:
            # some code
        except Exception as e:
            track_error(e, context={'input': data}, user_id=123, operation='calculate_tax')
    """
    return error_tracker.track_error(error, context, user_id, operation)
