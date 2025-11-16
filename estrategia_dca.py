# estrategia_dca.py - Estrategia REAL con datos BingX
import random
from datetime import datetime
from config import PARAMETROS_POR_PAR
from bingx_api import BingXMonitor

class EstrategiaDCA:
    def __init__(self):
        self.operaciones_activas = {}
        self.bingx = BingXMonitor()
    
    def generar_señal_real(self, par):
        """Generar señal REAL con datos BingX"""
        params = PARAMETROS_POR_PAR.get(par, PARAMETROS_POR_PAR['USDCAD'])
        
        # Obtener datos REALES de BingX
        datos_reales = self.bingx.obtener_datos_tecnicos(par)
        
        if datos_reales:
            # Usar datos REALES de BingX
            precio = datos_reales['precio_actual']
            rsi = datos_reales['rsi']
            tendencia = datos_reales['tendencia']
        else:
            # Fallback a datos simulados si BingX falla
            precio = self._precio_simulado(par)
            rsi = random.randint(30, 70)
            tendencia = "ALCISTA" if rsi < 40 else "BAJISTA" if rsi > 60 else "LATERAL"
        
        # Dirección basada en análisis REAL
        if tendencia == "ALCISTA":
            direccion = "COMPRA"
        elif tendencia == "BAJISTA":
            direccion = "VENTA"
        else:
            direccion = random.choice(['COMPRA', 'VENTA'])
        
        # Calcular niveles REALES respetando backtesting
        if direccion == "COMPRA":
            tp1 = precio * (1 + params['tp_niveles'][0])
            tp2 = precio * (1 + params['tp_niveles'][1])
            sl = precio * (1 - params['sl'])
            dca_1 = precio * (1 - params['dca_niveles'][0])
            dca_2 = precio * (1 - params['dca_niveles'][1])
        else:
            tp1 = precio * (1 - params['tp_niveles'][0])
            tp2 = precio * (1 - params['tp_niveles'][1])
            sl = precio * (1 + params['sl'])
            dca_1 = precio * (1 + params['dca_niveles'][0])
            dca_2 = precio * (1 + params['dca_niveles'][1])
        
        return {
            'par': par,
            'direccion': direccion,
            'precio_actual': round(precio, 5),
            'tp1': round(tp1, 5),
            'tp2': round(tp2, 5),
            'sl': round(sl, 5),
            'dca_1': round(dca_1, 5),
            'dca_2': round(dca_2, 5),
            'rsi': rsi,
            'tendencia': tendencia,
            'winrate_esperado': params['winrate'],
            'rentabilidad_esperada': params['rentabilidad'],
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'fuente_datos': 'BINGX' if datos_reales else 'SIMULADO'
        }
    
    def _precio_simulado(self, par):
        """Precio simulado como fallback"""
        precios_base = {
            'USDCAD': 1.3450, 'USDJPY': 148.50, 'AUDUSD': 0.6520,
            'EURGBP': 0.8550, 'GBPUSD': 1.2650
        }
        return precios_base.get(par, 1.0000) * random.uniform(0.998, 1.002)
