# config.py - PARÁMETROS OPTIMIZADOS S/R ETAPA 1
import os

# Configuración Telegram
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# 🎯 PARÁMETROS BACKTESTING S/R ETAPA 1 OPTIMIZADOS
PARAMETROS_POR_PAR = {
    'EURUSD': {  # ALTA RENTABILIDAD BACKTESTING
        'winrate': 63.4,
        'rentabilidad': 210.23,
        'leverage': 20,
        'dca_niveles': [0.005, 0.010],    # OPTIMIZADO S/R
        'tp_niveles': [0.015, 0.025],     # OPTIMIZADO S/R  
        'sl': 0.012
    },
    'USDCAD': {  # ALTA RENTABILIDAD BACKTESTING
        'winrate': 63.2,
        'rentabilidad': 168.16,
        'leverage': 20,
        'dca_niveles': [0.006, 0.012],
        'tp_niveles': [0.018, 0.030],
        'sl': 0.015
    },
    'EURCHF': {  # RENTABLE BACKTESTING
        'winrate': 48.9,
        'rentabilidad': 0.61,
        'leverage': 15,
        'dca_niveles': [0.008, 0.016],
        'tp_niveles': [0.012, 0.020],
        'sl': 0.018
    },
    'EURAUD': {  # MÁXIMA RENTABILIDAD BACKTESTING
        'winrate': 64.3,
        'rentabilidad': 322.94,
        'leverage': 20,
        'dca_niveles': [0.004, 0.008],
        'tp_niveles': [0.020, 0.035],
        'sl': 0.010
    }
}

# ✅ PARES OPTIMIZADOS BACKTESTING
TOP_5_PARES = ['EURUSD', 'USDCAD', 'EURCHF', 'EURAUD']

# 🎯 GESTIÓN DE RIESGO OPTIMIZADA
RISK_MANAGEMENT = {
    'max_drawdown': 0.50,
    'consecutive_loss_limit': 5,
    'capital_inicial': 1000
}
