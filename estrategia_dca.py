# estrategia_dca.py - ESTRATEGIA S/R REAL CON INDICADORES REALES
import random
from datetime import datetime
from config import PARAMETROS_POR_PAR
from yahoo_api import YahooFinanceAPI
from analisis_tecnico import AnalisisTechnicoSR
from indicadores_reales import IndicadoresReales  # NUEVO

class EstrategiaDCA:
    def __init__(self):
        self.operaciones_activas = {}
        self.yahoo = YahooFinanceAPI()
        self.analisis_sr = AnalisisTechnicoSR()
        self.indicadores_reales = IndicadoresReales()  # NUEVO
    
    def generar_señal_real(self, par):
        """Generar señal REAL con indicadores REALES"""
        try:
            params = PARAMETROS_POR_PAR.get(par, PARAMETROS_POR_PAR['EURUSD'])
            
            # Obtener datos TÉCNICOS REALES (NUEVO)
            datos_reales = self.obtener_datos_tecnicos_reales(par)
            
            if not datos_reales:
                print(f"❌ No se pudieron obtener datos técnicos reales para {par}")
                return None
            
            precio = datos_reales['precio_actual']
            rsi = datos_reales['rsi']
            tendencia = datos_reales['tendencia']
            fuente = datos_reales['fuente']
            
            print(f"🔍 Analizando {par} - Precio: {precio:.5f}, RSI: {rsi}, Tendencia: {tendencia}, Fuente: {fuente}")
            
            # 🎯 ANÁLISIS S/R REAL (ESTRATEGIA BACKTESTING)
            analisis_sr = self.analisis_sr.analizar_estructura_mercado(
                par, precio, tendencia, rsi
            )
            
            # Solo generar señal si el análisis S/R es favorable
            if not analisis_sr['señal']:
                print(f"📊 {par}: {analisis_sr['motivo']}")
                return None
            
            # Verificar condiciones óptimas según backtesting
            if (analisis_sr['señal'] == "COMPRA" and 
                not self.analisis_sr.es_zona_compra_optima(analisis_sr)):
                print(f"📊 {par}: Condiciones compra no óptimas - {analisis_sr['motivo']}")
                return None
                
            if (analisis_sr['señal'] == "VENTA" and 
                not self.analisis_sr.es_zona_venta_optima(analisis_sr)):
                print(f"📊 {par}: Condiciones venta no óptimas - {analisis_sr['motivo']}") 
                return None
            
            direccion = analisis_sr['señal']
            confianza = analisis_sr['confianza']
            
            print(f"🎯 SEÑAL S/R CONFIRMADA: {par} {direccion} - {analisis_sr['motivo']}")
            
            # Calcular niveles con parámetros optimizados del backtesting
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
                # NUEVOS DATOS S/R
                'estrategia': 'S/R Etapa 1',
                'niveles_sr': analisis_sr['niveles_sr'],
                'zona_actual': analisis_sr['zona_actual'],
                'motivo_señal': analisis_sr['motivo'],
                'distancia_support': analisis_sr['distancia_support'],
                'distancia_resistance': analisis_sr['distancia_resistance']
            }
            
        except Exception as e:
            print(f"❌ Error en generar_señal_real: {e}")
            return None
    
    def obtener_datos_tecnicos_reales(self, par):
        """Obtener datos técnicos REALES usando IndicadoresReales"""
        try:
            # Usar el nuevo módulo de indicadores reales
            datos = self.indicadores_reales.obtener_indicadores_reales(par)
            
            if datos and datos['precio_actual']:
                return datos
            else:
                # Fallback al método anterior si el nuevo falla
                return self.yahoo.obtener_datos_tecnicos(par)
                
        except Exception as e:
            print(f"❌ Error obteniendo datos técnicos reales: {e}")
            # Fallback al método anterior
            return self.yahoo.obtener_datos_tecnicos(par)
