# config.py - CON COMPATIBILIDAD
import os

# Configuración Telegram
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# 🎯 PARÁMETROS BACKTESTING S/R ETAPA 1 OPTIMIZADOS
PARAMETROS_POR_PAR = {
    # FOREX (EXISTENTE)
    'EURUSD': {
        'winrate': 63.4,
        'rentabilidad': 210.23,
        'leverage': 20,
        'dca_niveles': [0.005, 0.010],
        'tp_niveles': [0.015, 0.025],
        'sl': 0.012,
        'tipo': 'forex'
    },
    'USDCAD': {
        'winrate': 63.2,
        'rentabilidad': 168.16,
        'leverage': 20,
        'dca_niveles': [0.006, 0.012],
        'tp_niveles': [0.018, 0.030],
        'sl': 0.015,
        'tipo': 'forex'
    },
    'EURCHF': {
        'winrate': 48.9,
        'rentabilidad': 0.61,
        'leverage': 15,
        'dca_niveles': [0.008, 0.016],
        'tp_niveles': [0.012, 0.020],
        'sl': 0.018,
        'tipo': 'forex'
    },
    'EURAUD': {
        'winrate': 64.3,
        'rentabilidad': 322.94,
        'leverage': 20,
        'dca_niveles': [0.004, 0.008],
        'tp_niveles': [0.020, 0.035],
        'sl': 0.010,
        'tipo': 'forex'
    },
    
    # MATERIAS PRIMAS (NUEVAS)
    'XAUUSD': {
        'winrate': 58.0,
        'rentabilidad': 145.0,
        'leverage': 10,
        'dca_niveles': [0.008, 0.016],
        'tp_niveles': [0.025, 0.040],
        'sl': 0.020,
        'tipo': 'commodity'
    },
    'XAGUSD': {
        'winrate': 55.0,
        'rentabilidad': 120.0,
        'leverage': 10,
        'dca_niveles': [0.010, 0.020],
        'tp_niveles': [0.030, 0.050],
        'sl': 0.025,
        'tipo': 'commodity'
    },
    'OILUSD': {
        'winrate': 56.0,
        'rentabilidad': 135.0,
        'leverage': 10,
        'dca_niveles': [0.012, 0.024],
        'tp_niveles': [0.035, 0.060],
        'sl': 0.030,
        'tipo': 'commodity'
    },
    'XPTUSD': {
        'winrate': 52.0,
        'rentabilidad': 95.0,
        'leverage': 8,
        'dca_niveles': [0.015, 0.030],
        'tp_niveles': [0.040, 0.070],
        'sl': 0.035,
        'tipo': 'commodity'
    }
}

# ✅ TODOS LOS PARES ACTIVOS (FOREX + MATERIAS PRIMAS)
TOP_PARES = [
    # FOREX (original)
    'EURUSD', 'USDCAD', 'EURCHF', 'EURAUD',
    # MATERIAS PRIMAS (nuevas)
    'XAUUSD', 'XAGUSD', 'OILUSD', 'XPTUSD'
]

# 🎯 MANTENER COMPATIBILIDAD - AGREGAR ESTA LÍNEA
TOP_5_PARES = TOP_PARES  # Para que otros archivos no fallen

# 🎯 GESTIÓN DE RIESGO OPTIMIZADA
RISK_MANAGEMENT = {
    'max_drawdown': 0.50,
    'consecutive_loss_limit': 5,
    'capital_inicial': 1000
}
