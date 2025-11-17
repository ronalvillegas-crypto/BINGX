# config.py - Configuraciones centralizadas CON PARÁMETROS OPTIMIZADOS
import os

# Configuración Telegram
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# Configuración BingX (solo lectura para monitoreo)
BINGX_API_KEY = os.environ.get('BINGX_API_KEY', '')
BINGX_SECRET_KEY = os.environ.get('BINGX_SECRET_KEY', '')

# 🎯 PARÁMETROS BACKTESTING OPTIMIZADOS CON LEVERAGE 20x
PARAMETROS_POR_PAR = {
    'USDCAD': {
        'winrate': 61.0, 
        'rentabilidad': 315.6,  # Proyectado anual (26.3% mensual × 12)
        'leverage': 20,
        'dca_niveles': [0.006, 0.012],    # OPTIMIZADO: DCA 0.6%/1.2%
        'tp_niveles': [0.018, 0.030],     # OPTIMIZADO: TP 1.8%/3.0%
        'sl': 0.015
    },
    'USDJPY': {
        'winrate': 58.0, 
        'rentabilidad': 278.4,  # Proyectado anual (23.2% mensual × 12)
        'leverage': 20,
        'dca_niveles': [0.007, 0.014],    # OPTIMIZADO: DCA 0.7%/1.4%
        'tp_niveles': [0.020, 0.035],     # OPTIMIZADO: TP 2.0%/3.5%
        'sl': 0.020
    },
    'AUDUSD': {
        'winrate': 59.0, 
        'rentabilidad': 283.2,  # Proyectado anual (23.6% mensual × 12)
        'leverage': 20,
        'dca_niveles': [0.006, 0.012],    # OPTIMIZADO: DCA 0.6%/1.2%
        'tp_niveles': [0.018, 0.030],     # OPTIMIZADO: TP 1.8%/3.0%
        'sl': 0.015
    },
    'EURGBP': {
        'winrate': 57.0, 
        'rentabilidad': 273.6,  # Proyectado anual (22.8% mensual × 12)
        'leverage': 20,
        'dca_niveles': [0.007, 0.014],    # OPTIMIZADO: DCA 0.7%/1.4%
        'tp_niveles': [0.020, 0.035],     # OPTIMIZADO: TP 2.0%/3.5%
        'sl': 0.020
    },
    'GBPUSD': {
        'winrate': 60.0, 
        'rentabilidad': 288.0,  # Proyectado anual (24.0% mensual × 12)
        'leverage': 20,
        'dca_niveles': [0.006, 0.012],    # OPTIMIZADO: DCA 0.6%/1.2%
        'tp_niveles': [0.018, 0.030],     # OPTIMIZADO: TP 1.8%/3.0%
        'sl': 0.015
    }
}

# MANTENER PARES ORIGINALES
TOP_5_PARES = ['USDCAD', 'USDJPY', 'AUDUSD', 'EURGBP', 'GBPUSD']

# PARÁMETROS GESTIÓN DE RIESGO (NUEVO)
RISK_MANAGEMENT = {
    'max_drawdown': 0.70,  # Stop-loss global 70%
    'consecutive_loss_limit': 10,  # Límite pérdidas consecutivas
    'capital_inicial': 1000
}
