# Telegram Finance Tracker Bot

A personal finance tracking bot built with Python, Telegram API, and Google Sheets.
Designed to simplify daily expense tracking and create a structured financial system.

---

## Features

* 📲 Register expenses directly from Telegram
* 📊 Automatic categorization (custom categories supported)
* 💳 Multiple payment methods
* 📈 Real-time summary of expenses
* ☁️ Google Sheets integration as database
* 🔒 Private access (restricted by Chat ID)

---

## Tech Stack

* Python
* python-telegram-bot
* Google Sheets API (gspread)
* OAuth2 (Service Account)
* Render (Cloud Deployment)
* Git & GitHub

---

## Project Structure

* `bot.py` → Main bot logic
* `requirements.txt` → Dependencies
* `.gitignore` → Ignore sensitive files
* `credenciales.json` → (Not included, handled via environment variables)

---

## ⚙️ Setup

### 1. Clone repository

```bash
git clone https://github.com/ClaudioChiotti/bot-finanzas.git
cd bot-finanzas
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Variables

Create the following variables:

* `TOKEN` → Telegram Bot Token
* `CHAT_ID` → Your Telegram Chat ID
* `GOOGLE_CREDS` → JSON credentials (Service Account)

---

##Google Sheets Structure

The system uses a spreadsheet with the following sheets:

* **Gastos** → Date | Category | Amount | Payment Method
* **Categorias** → List of categories
* **TiposPago** → List of payment methods

---

## Deployment

The bot is deployed on Render (free tier) and runs 24/7.

Steps:

1. Push code to GitHub
2. Connect repository to Render
3. Add environment variables
4. Deploy

---

## Security

Sensitive data such as credentials and tokens are handled via environment variables and are not stored in the repository.

---

## 📌 Future Improvements

* Daily/weekly expense alerts
* Monthly financial reports
* Budget tracking system
* Power BI dashboard integration

---

## Author

Claudio Chiotti
Aspiring Business Analyst | Data Enthusiast

---
