# 📚 Usage Examples

## Example Calculations

### Example 1: Single Person, No Church Tax

**Input:**
- Annual gross income: 45,000€
- Tax class: 1 (Single)
- Children: 0
- Church tax: No

**Expected Output:**
- Income tax: ~8,500€
- Solidarity surcharge: ~0€ (below threshold)
- Social security: ~9,150€
- **Net annual income: ~27,350€**
- **Net monthly income: ~2,280€**

### Example 2: Married Couple, Higher Earner

**Input:**
- Annual gross income: 65,000€
- Tax class: 3 (Married, higher income)
- Children: 2
- Church tax: Yes

**Expected Output:**
- Income tax: ~10,200€
- Solidarity surcharge: ~560€
- Church tax: ~820€
- Social security: ~13,200€
- **Net annual income: ~40,220€**
- **Net monthly income: ~3,350€**

### Example 3: Single Parent

**Input:**
- Annual gross income: 38,000€
- Tax class: 2 (Single parent)
- Children: 1
- Church tax: No

**Expected Output:**
- Income tax: ~5,800€ (with single parent relief)
- Solidarity surcharge: ~0€
- Social security: ~7,730€
- **Net annual income: ~24,470€**
- **Net monthly income: ~2,040€**

### Example 4: High Earner

**Input:**
- Annual gross income: 120,000€
- Tax class: 1 (Single)
- Children: 0
- Church tax: Yes

**Expected Output:**
- Income tax: ~39,500€
- Solidarity surcharge: ~2,170€
- Church tax: ~3,160€
- Social security: ~12,600€ (capped)
- **Net annual income: ~62,570€**
- **Net monthly income: ~5,215€**

## Bot Conversation Examples

### Example 1: Basic Calculation Flow

```
User: /start

Bot: 🇩🇪 Willkommen beim deutschen Steuerrechner!

Ich helfe Ihnen, Ihre Steuern und Abgaben in Deutschland zu berechnen.

Wählen Sie eine Option:
[💶 Steuern berechnen] [📋 Meine Berechnungen]
[⚙️ Einstellungen] [❓ Hilfe]

User: [Clicks "💶 Steuern berechnen"]

Bot: 💰 Bitte geben Sie Ihr jährliches Bruttoeinkommen ein:

(Beispiel: 45000)
[❌ Abbrechen]

User: 45000

Bot: 📑 Wählen Sie Ihre Steuerklasse:

1️⃣ Klasse 1: Alleinstehend
2️⃣ Klasse 2: Alleinerziehend
3️⃣ Klasse 3: Verheiratet (höheres Einkommen)
4️⃣ Klasse 4: Verheiratet (ähnliches Einkommen)
5️⃣ Klasse 5: Verheiratet (niedrigeres Einkommen)
6️⃣ Klasse 6: Zweitjob

[1️⃣ Klasse 1] [2️⃣ Klasse 2]
[3️⃣ Klasse 3] [4️⃣ Klasse 4]
[5️⃣ Klasse 5] [6️⃣ Klasse 6]
[❌ Abbrechen]

User: [Clicks "1️⃣ Klasse 1"]

Bot: 👶 Haben Sie Kinder? Wenn ja, wie viele?

[0] [1] [2]
[3] [4] [5+]
[❌ Abbrechen]

User: [Clicks "0"]

Bot: ⛪ Zahlen Sie Kirchensteuer?

[Ja] [Nein]
[❌ Abbrechen]

User: [Clicks "Nein"]

Bot: ⏳ Berechne Ihre Steuern...

Bot: 📊 Steuerberechnung 2024

💰 Bruttoeinkommen: 45,000.00€

📉 Abzüge:
• Einkommensteuer: 8,486.00€
• Solidaritätszuschlag: 0.00€
• Kirchensteuer: 0.00€
• Krankenversicherung: 3,285.00€
• Rentenversicherung: 4,185.00€
• Arbeitslosenversicherung: 585.00€
• Pflegeversicherung: 765.00€

💸 Gesamtabzüge: 17,306.00€
✅ Nettoeinkommen: 27,694.00€

📅 Monatlich:
• Brutto: 3,750.00€
• Netto: 2,307.83€

[💶 Steuern berechnen] [📊 Hauptmenü]
```

### Example 2: Language Change

```
User: /start

Bot: 🇩🇪 Willkommen beim deutschen Steuerrechner!
...

User: [Clicks "⚙️ Einstellungen"]

Bot: ⚙️ Einstellungen

Passen Sie Ihre Präferenzen an:

[🌍 Sprache]
[◀️ Zurück]

User: [Clicks "🌍 Sprache"]

Bot: 🌍 Sprache wählen

Wählen Sie Ihre bevorzugte Sprache:

[🇩🇪 Deutsch] [🇸🇦 العربية]
[🇹🇷 Türkçe] [🇵🇱 Polski]
[🇷🇺 Русский] [🇮🇹 Italiano]
[🇷🇴 Română] [🇬🇧 English]
[🇬🇷 Ελληνικά] [🇭🇷 Hrvatski]
[◀️ Zurück]

User: [Clicks "🇬🇧 English"]

Bot: ✅ Language set to English

[📊 Main Menu]

User: [Clicks "📊 Main Menu"]

Bot: 📊 Main Menu

Select an option:

[💶 Calculate Tax] [📋 My Calculations]
[⚙️ Settings] [❓ Help]
```

### Example 3: Admin Update Notification

```
Bot (to Admin): 🔔 Neue Steueraktualisierung erkannt!

Titel: Anpassung Grundfreibetrag 2025
Quelle: Bundesministerium der Finanzen
Typ: allowance
URL: https://www.bundesfinanzministerium.de/...

Änderungen:
• Grundfreibetrag: 11.604€ → 11.784€
• Gültig ab: 01.01.2025

Gültig ab: 01.01.2025

Möchten Sie diese Änderungen anwenden?

[✅ Genehmigen] [❌ Ablehnen]

Admin: [Clicks "✅ Genehmigen"]

Bot: ✅ Aktualisierung genehmigt und angewendet!
```

## API Usage Examples (For Development)

### Using the Tax Calculator Directly

```python
from bot.services.tax_calculator import GermanTaxCalculator

# Initialize calculator
calculator = GermanTaxCalculator(year=2024)

# Calculate taxes
result = calculator.calculate_net_income(
    annual_gross=45000,
    tax_class=1,
    children=0,
    church_tax=False
)

print(f"Gross: {result['gross_annual']}€")
print(f"Income Tax: {result['income_tax']}€")
print(f"Net: {result['net_annual']}€")
print(f"Monthly Net: {result['net_monthly']}€")
```

### Using the Translation System

```python
from bot.utils import t

# Get translation
message = t('welcome', lang='de')
print(message)

# With parameters
message = t(
    'calculation_result',
    lang='en',
    year=2024,
    gross='45,000.00',
    net='27,694.00'
)
print(message)
```

### Monitoring Tax Updates

```python
from bot.services.tax_update_monitor import tax_update_monitor
import asyncio

async def check_updates():
    updates = await tax_update_monitor.check_for_updates()
    for update in updates:
        print(f"Found update: {update['title']}")
        print(f"Source: {update['source_name']}")
        print(f"URL: {update['source_url']}")

asyncio.run(check_updates())
```

## Testing Examples

### Run All Tests

```bash
pytest
```

### Run Specific Test

```bash
pytest tests/test_tax_calculator.py::test_middle_income_class_1 -v
```

### Run with Coverage

```bash
pytest --cov=bot --cov-report=html
```

## Common Use Cases

### 1. Student Part-time Job

- Income: 12,000€/year
- Tax class: 1
- Expected: Very low or no income tax

### 2. Junior Developer

- Income: 42,000€/year
- Tax class: 1
- Expected: ~26,500€ net

### 3. Senior Developer

- Income: 75,000€/year
- Tax class: 3 (married)
- Expected: ~48,000€ net

### 4. Manager

- Income: 110,000€/year
- Tax class: 1
- Expected: ~62,000€ net

### 5. Freelancer (approximate)

- Income: 60,000€/year
- Tax class: 1
- Note: Actual freelancer taxes are more complex

## Error Handling Examples

### Invalid Income

```
User: abc123

Bot: ❌ Ungültiger Betrag. Bitte geben Sie eine Zahl ein.
```

### Network Error (Update Check)

```
Log: ERROR - Error checking BMF: Connection timeout
Action: Bot continues with cached data
```

### Database Error

```
Log: ERROR - Database connection failed
Action: Bot restarts and reconnects
User: Sees error message, can retry
```

## Integration Examples

### With ELSTER (Future)

```python
# Export calculation for ELSTER
def export_to_elster(calculation):
    return {
        'Zeile 4': calculation['gross_annual'],
        'Zeile 31': calculation['income_tax'],
        # ... more fields
    }
```

### With PDF Generator (Future)

```python
# Generate PDF report
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def generate_pdf_report(calculation, filename):
    c = canvas.Canvas(filename, pagesize=A4)
    c.drawString(100, 800, f"Tax Report {calculation['year']}")
    c.drawString(100, 780, f"Gross: {calculation['gross_annual']}€")
    # ... more content
    c.save()
```

These examples demonstrate the complete functionality of the German Tax Calculator Bot!
