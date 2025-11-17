# config.py - Configuraciones OPTIMIZADAS CON ESTRATEGIA S/R ETAPA 1
import os

# Configuración Telegram
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# Configuración BingX (solo lectura para monitoreo)
BINGX_API_KEY = os.environ.get('BINGX_API_KEY', '')
BINGX_SECRET_KEY = os.environ.get('BINGX_SECRET_KEY', '')

# 🎯 PARÁMETROS OPTIMIZADOS BASADOS EN BACKTESTING S/R ETAPA 1
PARAMETROS_POR_PAR = {
    'EURUSD': {  # NUEVO - ALTA RENTABILIDAD
        'winrate': 63.4,
        'rentabilidad': 210.23,
        'leverage': 20,
        'dca_niveles': [0.005, 0.010],    # OPTIMIZADO
        'tp_niveles': [0.015, 0.025],     # OPTIMIZADO
        'sl': 0.012
    },
    'USDCAD': {  # MANTENER - ALTA RENTABILIDAD
        'winrate': 63.2,
        'rentabilidad': 168.16,
        'leverage': 20,
        'dca_niveles': [0.006, 0.012],
        'tp_niveles': [0.018, 0.030],
        'sl': 0.015
    },
    'EURCHF': {  # NUEVO - RENTABLE
        'winrate': 48.9,
        'rentabilidad': 0.61,
        'leverage': 15,  # Leverage más conservador
        'dca_niveles': [0.008, 0.016],
        'tp_niveles': [0.012, 0.020],
        'sl': 0.018
    },
    'EURAUD': {  # NUEVO - MÁXIMA RENTABILIDAD
        'winrate': 64.3,
        'rentabilidad': 322.94,
        'leverage': 20,
        'dca_niveles': [0.004, 0.008],
        'tp_niveles': [0.020, 0.035],
        'sl': 0.010
    }
}

# ✅ PARES OPTIMIZADOS BASADOS EN BACKTESTING
TOP_5_PARES = ['EURUSD', 'USDCAD', 'EURCHF', 'EURAUD']

# ⚠️ EXCLUIR PARES NO RENTABLES: EURGBP, EURJPY

# 🎯 PARÁMETROS GESTIÓN DE RIESGO OPTIMIZADOS
RISK_MANAGEMENT = {
    'max_drawdown': 0.50,  # Más conservador: 50% stop-loss global
    'consecutive_loss_limit': 5,  # Más estricto: 5 pérdidas consecutivas
    'capital_inicial': 1000
}
