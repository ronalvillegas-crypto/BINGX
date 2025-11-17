# estrategia_dca.py - VERSIÓN OPTIMIZADA CON ESTRATEGIA S/R
import random
from datetime import datetime
from config import PARAMETROS_POR_PAR
from bingx_api import BingXMonitor

class EstrategiaDCA:
    def __init__(self):
        self.operaciones_activas = {}
        self.bingx = BingXMonitor()
    
    def generar_señal_real(self, par):
        """Generar señal REAL con estrategia S/R optimizada"""
        try:
            params = PARAMETROS_POR_PAR.get(par, PARAMETROS_POR_PAR['EURUSD'])  # Default cambiado a EURUSD
            
            # Obtener datos con fallback robusto
            datos_reales = self.bingx.obtener_datos_tecnicos(par)
            
            if datos_reales:
                # Usar datos REALES de BingX
                precio = datos_reales['precio_actual']
                rsi = datos_reales['rsi']
                tendencia = datos_reales['tendencia']
                fuente = datos_reales['fuente']
                volatilidad = datos_reales.get('volatilidad', 0.5)
                
                # 🎯 CONDICIONES MEJORADAS BASADAS EN S/R ETAPA 1
                condiciones_compra_alta = (
                    rsi < 32 and                    # Más sobrevendido
                    tendencia == "ALCISTA" and      # Tendencia confirmada
                    volatilidad < 0.8               # Baja volatilidad
                )
                
                condiciones_venta_alta = (
                    rsi > 68 and                    # Más sobrecomprado  
                    tendencia == "BAJISTA" and      # Tendencia confirmada
                    volatilidad < 0.8               # Baja volatilidad
                )
                
                # Asignar dirección y confianza
                if condiciones_compra_alta:
                    direccion = "COMPRA"
                    confianza = "ALTA"
                elif condiciones_venta_alta:
                    direccion = "VENTA" 
                    confianza = "ALTA"
                else:
                    # No operar si no hay condiciones óptimas
                    return None
                    
            else:
                # Fallback más conservador - no generar señales sin datos
                return None
            
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
                'volatilidad': volatilidad,
                'winrate_esperado': params['winrate'],
                'rentabilidad_esperada': params['rentabilidad'],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'fuente_datos': fuente,
                'leverage': params['leverage'],
                'confianza': confianza
            }
            
        except Exception as e:
            print(f"❌ Error crítico en generar_señal_real: {e}")
            return None  # No generar señales en caso de error
    
    def _precio_simulado_realista(self, par):
        """Precio simulado realista para fallback"""
        precios_base = {
            'EURUSD': 1.0850, 'USDCAD': 1.3450, 'EURCHF': 0.9550,
            'EURAUD': 1.6350, 'USDJPY': 148.50, 'AUDUSD': 0.6520,
            'EURGBP': 0.8550, 'GBPUSD': 1.2650
        }
        precio_base = precios_base.get(par, 1.0000)
        return precio_base * random.uniform(0.998, 1.002)
    
    def _señal_emergencia(self, par):
        """Señal de emergencia si todo falla - MÁS CONSERVADORA"""
        # En la estrategia optimizada, no generamos señales de emergencia
        return None
