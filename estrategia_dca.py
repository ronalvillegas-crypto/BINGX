# estrategia_dca.py - VERSIÓN MEJORADA CON GESTIÓN DE RIESGO
import random
from datetime import datetime
from config import PARAMETROS_POR_PAR
from bingx_api import BingXMonitor

class EstrategiaDCA:
    def __init__(self):
        self.operaciones_activas = {}
        self.bingx = BingXMonitor()
    
    def generar_señal_real(self, par):
        """Generar señal REAL con gestión de riesgo mejorada"""
        try:
            params = PARAMETROS_POR_PAR.get(par, PARAMETROS_POR_PAR['USDCAD'])
            
            # Obtener datos con fallback robusto
            datos_reales = self.bingx.obtener_datos_tecnicos(par)
            
            if datos_reales:
                # Usar datos REALES de BingX
                precio = datos_reales['precio_actual']
                rsi = datos_reales['rsi']
                tendencia = datos_reales['tendencia']
                fuente = datos_reales['fuente']
                
                # MEJORA: Análisis de tendencia más robusto
                if rsi < 35 and tendencia == "ALCISTA":
                    direccion = "COMPRA"
                    confianza = "ALTA"
                elif rsi > 65 and tendencia == "BAJISTA":
                    direccion = "VENTA" 
                    confianza = "ALTA"
                else:
                    # Estrategia original como fallback
                    if tendencia == "ALCISTA":
                        direccion = "COMPRA"
                    elif tendencia == "BAJISTA":
                        direccion = "VENTA"
                    else:
                        direccion = "COMPRA" if rsi < 50 else "VENTA"
                    confianza = "MEDIA"
                    
            else:
                # Fallback a simulación inteligente
                precio = self._precio_simulado_realista(par)
                rsi = random.randint(30, 70)
                tendencia = "ALCISTA" if rsi < 40 else "BAJISTA" if rsi > 60 else "LATERAL"
                fuente = 'SIMULADO'
                direccion = "COMPRA" if rsi < 50 else "VENTA"
                confianza = "MEDIA"
            
            # Calcular niveles con parámetros optimizados
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
                'fuente_datos': fuente,
                'leverage': params['leverage'],
                'confianza': confianza  # NUEVO: nivel de confianza
            }
            
        except Exception as e:
            print(f"❌ Error crítico en generar_señal_real: {e}")
            # Fallback de emergencia
            return self._señal_emergencia(par)
    
    def _precio_simulado_realista(self, par):
        """Precio simulado realista para fallback"""
        precios_base = {
            'USDCAD': 1.3450, 'USDJPY': 148.50, 'AUDUSD': 0.6520,
            'EURGBP': 0.8550, 'GBPUSD': 1.2650
        }
        precio_base = precios_base.get(par, 1.0000)
        return precio_base * random.uniform(0.998, 1.002)
    
    def _señal_emergencia(self, par):
        """Señal de emergencia si todo falla"""
        params = PARAMETROS_POR_PAR.get(par, PARAMETROS_POR_PAR['USDCAD'])
        precio = self._precio_simulado_realista(par)
        
        return {
            'par': par,
            'direccion': random.choice(['COMPRA', 'VENTA']),
            'precio_actual': round(precio, 5),
            'tp1': round(precio * 1.018, 5),
            'tp2': round(precio * 1.030, 5),
            'sl': round(precio * 0.985, 5),
            'dca_1': round(precio * 0.994, 5),
            'dca_2': round(precio * 0.988, 5),
            'rsi': 50,
            'tendencia': 'LATERAL',
            'winrate_esperado': params['winrate'],
            'rentabilidad_esperada': params['rentabilidad'],
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'fuente_datos': 'EMERGENCIA',
            'leverage': params['leverage'],
            'confianza': 'BAJA'
        }
