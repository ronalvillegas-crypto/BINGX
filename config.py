# config.py - Configuraciones centralizadas
import os

# Configuración Telegram
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# Configuración BingX (solo lectura para monitoreo)
BINGX_API_KEY = os.environ.get('BINGX_API_KEY', '')
BINGX_SECRET_KEY = os.environ.get('BINGX_SECRET_KEY', '')

# Parámetros Backtesting REALES (RESPETADOS)
PARAMETROS_POR_PAR = {
    'USDCAD': {
        'winrate': 85.0, 'rentabilidad': 536.5, 'leverage': 20,
        'dca_niveles': [0.004, 0.008], 'tp_niveles': [0.012, 0.020], 'sl': 0.015
    },
    'USDJPY': {
        'winrate': 75.0, 'rentabilidad': 390.1, 'leverage': 20,
        'dca_niveles': [0.005, 0.010], 'tp_niveles': [0.015, 0.025], 'sl': 0.020
    }
}

TOP_5_PARES = ['USDCAD', 'USDJPY', 'AUDUSD', 'EURGBP', 'GBPUSD']
