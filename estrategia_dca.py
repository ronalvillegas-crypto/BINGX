# estrategia_dca.py - ESTRATEGIA S/R REAL DEL BACKTESTING
import random
from datetime import datetime
from config import PARAMETROS_POR_PAR
from bingx_api import BingXMonitor
from analisis_tecnico import AnalisisTechnicoSR

class EstrategiaDCA:
    def __init__(self):
        self.operaciones_activas = {}
        self.bingx = BingXMonitor()
        self.analisis_sr = AnalisisTechnicoSR()
    
    def generar_señal_real(self, par):
        """Generar señal REAL con estrategia S/R del backtesting"""
        try:
            params = PARAMETROS_POR_PAR.get(par, PARAMETROS_POR_PAR['EURUSD'])
            
            datos_reales = self.bingx.obtener_datos_tecnicos(par)
            
            if not datos_reales:
                return None
            
            precio = datos_reales['precio_actual']
            rsi = datos_reales['rsi']
            tendencia = datos_reales['tendencia']
            fuente = datos_reales['fuente']
            
            # ANÁLISIS S/R REAL
            analisis_sr = self.analisis_sr.analizar_estructura_mercado(
                par, precio, tendencia, rsi
            )
            
            if not analisis_sr['señal']:
                print(f"📊 {par}: Sin señal S/R - {analisis_sr['motivo']}")
                return None
            
            if (analisis_sr['señal'] == "COMPRA" and 
                not self.analisis_sr.es_zona_compra_optima(analisis_sr)):
                print(f"📊 {par}: Condiciones compra no óptimas")
                return None
                
            if (analisis_sr['señal'] == "VENTA" and 
                not self.analisis_sr.es_zona_venta_optima(analisis_sr)):
                print(f"📊 {par}: Condiciones venta no óptimas") 
                return None
            
            direccion = analisis_sr['señal']
            confianza = analisis_sr['confianza']
            
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
                'confianza': confianza,
                'estrategia': 'S/R Etapa 1',
                'niveles_sr': analisis_sr['niveles_sr'],
                'zona_actual': analisis_sr['zona_actual'],
                'motivo_señal': analisis_sr['motivo']
            }
            
        except Exception as e:
            print(f"❌ Error en generar_señal_real S/R: {e}")
            return None
