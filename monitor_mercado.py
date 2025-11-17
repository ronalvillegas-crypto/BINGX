# monitor_mercado.py - Cambiar import a Yahoo Finance
import time
import threading
from datetime import datetime, timedelta
from config import TOP_5_PARES, RISK_MANAGEMENT
from yahoo_api import YahooFinanceAPI  # CAMBIADO
from estrategia_dca import EstrategiaDCA
from gestor_operaciones import GestorOperaciones
from telegram_bot import TelegramBotReal

class MonitorMercado:
    def __init__(self):
        self.yahoo = YahooFinanceAPI()  # CAMBIADO
        self.estrategia = EstrategiaDCA()
        self.gestor = GestorOperaciones()
        self.telegram = TelegramBotReal()
        self.monitoreando = False
        self.ultima_señal_por_par = {}
        
        # Resto del código igual...
        self.max_drawdown = RISK_MANAGEMENT['max_drawdown']
        self.consecutive_loss_limit = RISK_MANAGEMENT['consecutive_loss_limit']
        self.capital_inicial = RISK_MANAGEMENT['capital_inicial']
        self.capital_actual = self.capital_inicial
        self.consecutive_losses = 0
        self.total_operaciones = 0
        self.operaciones_ganadoras = 0

    # Resto de métodos igual (sin cambios)...
