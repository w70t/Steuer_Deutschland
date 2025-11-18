# 📝 Changelog

## Version 1.1.0 - Enhanced Local Error Tracking

### ✅ Added
- **Advanced local error tracking system** with comprehensive details
- **Multiple log files** for better organization:
  - `logs/tax_bot.log` - Main operations log
  - `logs/errors.log` - Errors only with full stack traces
  - `logs/errors_detailed.jsonl` - JSON format for analysis
- **Error statistics** displayed on bot startup
- **Complete error context logging**:
  - Exact timestamp
  - Error type and message
  - User ID (if applicable)
  - Full context (input data, operation)
  - Complete stack trace
  - Local variables at each frame
- **ERROR_TRACKING.md** - Comprehensive documentation in Arabic and English
- **Automatic log rotation** and retention policies

### ❌ Removed
- **Sentry integration** - No longer requires external error tracking service
- **sentry-sdk** dependency
- All Sentry-related configuration options

### 🔄 Changed
- **requirements.txt** - Replaced sentry-sdk with colorama for colored logs
- **config/settings.py** - Removed Sentry config, added enhanced logging config
- **.env.example** - Updated with new logging configuration options
- **main.py** - Replaced Sentry with local error tracker
- **README.md** - Updated error tracking section
- **DEPLOYMENT.md** - Removed Sentry references

### 🎯 Benefits
- ✅ 100% local error tracking
- ✅ No external dependencies or costs
- ✅ Complete privacy and data control
- ✅ Enhanced debugging with full context
- ✅ Easy to analyze errors (JSON format)
- ✅ No internet connection required
- ✅ Faster error logging
- ✅ Better Arabic support in logs

### 📊 Migration Notes

**Old Configuration (.env):**
```env
SENTRY_DSN=your_sentry_dsn_here
ENABLE_SENTRY=false
```

**New Configuration (.env):**
```env
ERROR_LOG_FILE=logs/errors.log
ENABLE_DETAILED_ERRORS=true
ENABLE_STACK_TRACE=true
```

**Old Usage:**
```python
import sentry_sdk
sentry_sdk.capture_exception(error)
```

**New Usage:**
```python
from bot.utils import track_error

track_error(
    error=e,
    context={'data': value},
    user_id=user.id,
    operation='operation_name'
)
```

---

## Version 1.0.0 - Initial Release

### ✅ Features
- German tax calculation based on official BMF formulas
- 10 languages support
- All 6 tax classes
- Church tax and social security calculations
- Automated tax law updates monitoring
- Admin approval system
- Calculation history
- SQLite database
- Docker support
- Comprehensive documentation

### 📚 Documentation
- README.md
- DEPLOYMENT.md
- EXAMPLES.md
- LICENSE
