import os
import json
import pytz
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    filters,
    ContextTypes
)
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, time

# ========= CONFIG =========
TOKEN = os.getenv("TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
NOMBRE_SHEET = "Financial_Tracking_System"

# ========= VALIDACIÓN =========
if not TOKEN:
    raise ValueError("Falta TOKEN en variables de entorno")

if not CHAT_ID:
    raise ValueError("Falta CHAT_ID en variables de entorno")

creds_json = os.getenv("GOOGLE_CREDS")

if not creds_json:
    raise ValueError("Falta GOOGLE_CREDS en variables de entorno")

# ========= GOOGLE SHEETS =========
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = json.loads(creds_json)

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    creds_dict,
    scope
)

client = gspread.authorize(creds)
libro = client.open(NOMBRE_SHEET)

sheet_gastos = libro.worksheet("Gastos")
sheet_categorias = libro.worksheet("Categorias")
sheet_pagos = libro.worksheet("TiposPago")

# ========= FUNCIONES =========
def cargar_categorias():
    data = sheet_categorias.get_all_values()
    return [fila[0] for fila in data[1:] if fila]

def cargar_pagos():
    data = sheet_pagos.get_all_values()
    return [fila[0] for fila in data[1:] if fila]

def obtener_resumen():
    data = sheet_gastos.get_all_records()
    resumen = {}

    for fila in data:
        try:
            cat = fila["Categoria"]
            monto = float(fila["Monto"])
        except:
            continue

        resumen[cat] = resumen.get(cat, 0) + monto

    texto = "📊 Resumen:\n"
    for k, v in resumen.items():
        texto += f"{k}: S/{v:.2f}\n"

    return texto

# ========= MENÚ =========
menu = [
    ["Registrar Gasto"],
    ["Ver Resumen"],
    ["Nueva Categoría"],
    ["Nuevo Tipo de Pago"]
]

markup_menu = ReplyKeyboardMarkup(menu, resize_keyboard=True)

# ========= START =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hola Claudio! ¿En qué te ayudo?",
        reply_markup=markup_menu
    )

# ========= RECORDATORIO =========
async def recordatorio(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=CHAT_ID,
        text="📌 ¿Registraste todos tus gastos del día?"
    )

# ========= HANDLER =========
async def manejar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # 🔒 SOLO TU CHAT
    if update.message.chat_id != CHAT_ID:
        return

    texto = update.message.text

    # VOLVER
    if texto == "Volver":
        context.user_data.clear()
        await start(update, context)
        return

    # MENÚ PRINCIPAL
    if texto == "Registrar Gasto":
        context.user_data["estado"] = "tipo_pago"

        tipos_pago = cargar_pagos()
        botones = [[t] for t in tipos_pago] + [["Volver"]]

        await update.message.reply_text(
            "Selecciona tipo de pago:",
            reply_markup=ReplyKeyboardMarkup(botones, resize_keyboard=True)
        )
        return

    if texto == "Ver Resumen":
        await update.message.reply_text(obtener_resumen(), reply_markup=markup_menu)
        return

    if texto == "Nueva Categoría":
        context.user_data["estado"] = "nueva_categoria"
        await update.message.reply_text("Escribe la nueva categoría:")
        return

    if texto == "Nuevo Tipo de Pago":
        context.user_data["estado"] = "nuevo_pago"
        await update.message.reply_text("Escribe el nuevo tipo de pago:")
        return

    # ========= FLUJO REGISTRO =========
    estado = context.user_data.get("estado")

    if estado == "tipo_pago":
        context.user_data["tipo_pago"] = texto
        context.user_data["estado"] = "categoria"

        categorias = cargar_categorias()
        botones = [[c] for c in categorias] + [["Volver"]]

        await update.message.reply_text(
            "Selecciona categoría:",
            reply_markup=ReplyKeyboardMarkup(botones, resize_keyboard=True)
        )
        return

    if estado == "categoria":
        context.user_data["categoria"] = texto
        context.user_data["estado"] = "monto"

        await update.message.reply_text("Ingresa el monto:")
        return

    if estado == "monto":
        try:
            monto = float(texto)
        except:
            await update.message.reply_text("Monto inválido")
            return

        sheet_gastos.append_row([
            datetime.now().strftime("%Y-%m-%d"),
            context.user_data["categoria"],
            monto,
            context.user_data["tipo_pago"]
        ])

        await update.message.reply_text(
            f"✔ Registrado: S/{monto}",
            reply_markup=markup_menu
        )

        context.user_data.clear()
        return

    # ========= NUEVA CATEGORÍA =========
    if estado == "nueva_categoria":
        sheet_categorias.append_row([texto])
        context.user_data.clear()

        await update.message.reply_text(
            f"Categoría agregada: {texto}",
            reply_markup=markup_menu
        )
        return

    # ========= NUEVO PAGO =========
    if estado == "nuevo_pago":
        sheet_pagos.append_row([texto])
        context.user_data.clear()

        await update.message.reply_text(
            f"Tipo de pago agregado: {texto}",
            reply_markup=markup_menu
        )
        return


# ========= MAIN =========
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar))

# ========= ZONA HORARIA PERÚ =========
zona = pytz.timezone("America/Lima")

#app.job_queue.run_daily(
#    recordatorio,
#    time(hour=22, minute=0, tzinfo=zona)
#)

print("Bot corriendo...")
app.run_polling()