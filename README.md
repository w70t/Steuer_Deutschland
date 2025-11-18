# 🇩🇪 German Tax Calculator Bot

A comprehensive Telegram bot for calculating German income taxes and social security contributions. The bot supports 10 languages and automatically monitors official German tax sources for updates.

## ✨ Features

- **🧮 Accurate Tax Calculations**: Based on official formulas from the Bundesministerium der Finanzen (BMF)
- **🌍 Multi-language Support**: 10 languages (German, Arabic, Turkish, Polish, Russian, Italian, Romanian, English, Greek, Croatian)
- **📊 All Tax Classes**: Support for all 6 German tax classes (Steuerklassen 1-6)
- **👶 Child Allowances**: Automatic calculation of child benefits
- **⛪ Church Tax**: Optional church tax calculation
- **💼 Social Security**: Comprehensive social security contributions (health, pension, unemployment, care insurance)
- **🔄 Auto-updates**: Monitors official sources for tax law changes
- **👨‍💼 Admin Approval**: New updates require admin approval before application
- **📝 History**: Users can view their calculation history
- **🔒 Secure**: All data stored securely with error tracking

## 📋 Requirements

- Python 3.9+
- Telegram Bot Token (get from [@BotFather](https://t.me/botfather))
- SQLite (included) or PostgreSQL

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Steuer_Deutschland.git
cd Steuer_Deutschland
```

### 2. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_TELEGRAM_ID=your_telegram_id_here
```

To get your Telegram ID:
1. Start a chat with [@userinfobot](https://t.me/userinfobot)
2. Copy your numeric ID

### 4. Run the Bot

```bash
python main.py
```

## 📁 Project Structure

```
Steuer_Deutschland/
├── bot/
│   ├── handlers/          # Telegram bot handlers
│   │   ├── start.py       # Start and main menu
│   │   ├── calculation.py # Tax calculation flow
│   │   ├── settings.py    # Settings and language
│   │   ├── admin.py       # Admin notifications
│   │   └── history.py     # Calculation history
│   ├── models/            # Database models
│   │   ├── user.py        # User model
│   │   ├── calculation.py # Tax calculation model
│   │   ├── tax_update.py  # Tax update model
│   │   └── database.py    # Database engine
│   ├── services/          # Business logic
│   │   ├── tax_calculator.py        # Tax calculation engine
│   │   └── tax_update_monitor.py    # Update monitoring
│   ├── locales/          # Translation files (10 languages)
│   │   ├── de/messages.json
│   │   ├── ar/messages.json
│   │   ├── tr/messages.json
│   │   ├── pl/messages.json
│   │   ├── ru/messages.json
│   │   ├── it/messages.json
│   │   ├── ro/messages.json
│   │   ├── en/messages.json
│   │   ├── el/messages.json
│   │   └── hr/messages.json
│   └── utils/            # Utilities
│       └── i18n.py       # Internationalization
├── config/
│   └── settings.py       # Configuration
├── data/                 # SQLite database (created automatically)
├── logs/                 # Log files (created automatically)
├── main.py              # Entry point
├── requirements.txt     # Dependencies
├── .env.example        # Environment template
└── README.md           # This file
```

## 🎯 Usage

### For Users

1. Start the bot: `/start`
2. Select your language
3. Click "Calculate Tax"
4. Enter your annual gross income
5. Select your tax class (1-6)
6. Enter number of children
7. Indicate if you pay church tax
8. Get detailed breakdown of taxes and net income

### For Administrators

The bot will automatically:
- Check official German tax sources every 24 hours (configurable)
- Send notifications when new tax updates are detected
- Wait for admin approval before applying changes

When you receive an update notification:
1. Review the changes
2. Click "Approve" to apply or "Reject" to ignore
3. Approved changes are automatically applied to the bot

## ⚙️ Configuration

### Environment Variables

All configuration is done via environment variables in `.env`:

```env
# Required
TELEGRAM_BOT_TOKEN=your_bot_token
ADMIN_TELEGRAM_ID=your_telegram_id

# Database (optional, defaults to SQLite)
DATABASE_URL=sqlite+aiosqlite:///./data/tax_bot.db

# Error Tracking (optional, for Sentry)
SENTRY_DSN=your_sentry_dsn
ENABLE_SENTRY=false

# Update Monitoring
CHECK_UPDATES_INTERVAL_HOURS=24
TAX_SOURCES_CHECK_ENABLED=true

# Official Sources (default values provided)
BMF_URL=https://www.bundesfinanzministerium.de
BZST_URL=https://www.bzst.de
ELSTER_URL=https://www.elster.de

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/tax_bot.log

# Bot Settings
DEFAULT_LANGUAGE=de
MAX_CALCULATION_HISTORY=50

# Auto-update Settings
AUTO_APPLY_UPDATES=false
REQUIRE_ADMIN_APPROVAL=true
```

## 🗂️ Database

The bot uses SQLAlchemy with async support. By default, it uses SQLite, but you can use PostgreSQL:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/taxbot
```

Tables are created automatically on first run.

## 🌍 Supported Languages

1. 🇩🇪 **German** (Deutsch) - Default
2. 🇸🇦 **Arabic** (العربية)
3. 🇹🇷 **Turkish** (Türkçe)
4. 🇵🇱 **Polish** (Polski)
5. 🇷🇺 **Russian** (Русский)
6. 🇮🇹 **Italian** (Italiano)
7. 🇷🇴 **Romanian** (Română)
8. 🇬🇧 **English**
9. 🇬🇷 **Greek** (Ελληνικά)
10. 🇭🇷 **Croatian** (Hrvatski)

## 📊 Tax Calculation Details

### Tax Classes (Steuerklassen)

1. **Class 1**: Single, divorced, widowed
2. **Class 2**: Single parent with children
3. **Class 3**: Married, higher-earning spouse
4. **Class 4**: Married, both spouses earn similarly
5. **Class 5**: Married, lower-earning spouse
6. **Class 6**: Second or additional job

### Calculated Items

- **Income Tax** (Einkommensteuer)
- **Solidarity Surcharge** (Solidaritätszuschlag) - 5.5% on income tax
- **Church Tax** (Kirchensteuer) - 8-9% depending on state
- **Health Insurance** (Krankenversicherung) - 14.6% (employee: 7.3%)
- **Pension Insurance** (Rentenversicherung) - 18.6% (employee: 9.3%)
- **Unemployment Insurance** (Arbeitslosenversicherung) - 2.6% (employee: 1.3%)
- **Care Insurance** (Pflegeversicherung) - 3.4% (employee: 1.7%)

### Official Sources

All calculations are based on official data from:
- **BMF**: Bundesministerium der Finanzen
- **BZSt**: Bundeszentralamt für Steuern
- **ELSTER**: Electronic tax declaration system

## 🔧 Development

### Adding a New Language

1. Create a new directory in `bot/locales/` (e.g., `bot/locales/fr/`)
2. Create `messages.json` with all required keys (use `de/messages.json` as template)
3. Add language code to `SUPPORTED_LANGUAGES` in `config/settings.py`
4. Add language name to `get_language_name()` in `bot/utils/i18n.py`

### Updating Tax Formulas

Tax formulas are in `bot/services/tax_calculator.py`. Update the `calculate_income_tax()` method with new formulas when tax laws change.

### Testing

```bash
pytest
```

## 📝 Logging & Error Tracking

### Log Files

The bot uses an advanced local error tracking system with multiple log files:

**Main Log** (`logs/tax_bot.log`):
- All operations (INFO, WARNING, ERROR)
- Rotation: 10 MB
- Retention: 30 days

**Error Log** (`logs/errors.log`):
- Errors only with full stack traces
- Rotation: 5 MB
- Retention: 90 days

**Detailed Errors** (`logs/errors_detailed.jsonl`):
- JSON format for easy analysis
- One error per line
- Includes full context and traceback details

### What Gets Logged

Every error includes:
- ⏰ Exact timestamp
- 🏷️ Error type and message
- 👤 User ID (if applicable)
- 📊 Full context (input data, operation)
- 📜 Complete stack trace
- 🔍 Local variables at each frame

### Viewing Logs

```bash
# Real-time error monitoring
tail -f logs/errors.log

# Last 50 errors
tail -n 50 logs/errors.log

# Search for specific error
grep "ValueError" logs/errors.log
```

See [ERROR_TRACKING.md](ERROR_TRACKING.md) for detailed documentation.

## 🔐 Security

- All user data is stored locally and encrypted
- Database uses parameterized queries (SQL injection protection)
- No data is shared with third parties
- Admin functions are protected by Telegram ID verification

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Contact: your-email@example.com

## 🎯 Roadmap

- [ ] Add support for freelancers (Freiberufler)
- [ ] Trade tax calculation (Gewerbesteuer)
- [ ] PDF report generation
- [ ] Annual tax estimation
- [ ] Integration with ELSTER API
- [ ] Mobile app version

## 🙏 Acknowledgments

- Tax formulas based on official BMF publications
- Built with python-telegram-bot
- Multi-language support powered by the amazing community

---

**⚠️ Disclaimer**: This bot provides estimates for informational purposes only. For official tax calculations and advice, please consult a tax professional (Steuerberater) or use official tools like ELSTER.