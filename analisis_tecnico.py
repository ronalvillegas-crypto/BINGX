# analisis_tecnico.py - CON DETECCIÓN REAL DE S/R
import numpy as np
import random
from datetime import datetime, timedelta
from indicadores_reales import IndicadoresReales

class AnalisisTechnicoSR:
    def __init__(self):
        self.niveles_sr_historicos = {}
        self.indicadores = IndicadoresReales()
        
    def detectar_niveles_sr(self, par, datos_precios):
        """Detectar niveles de Support/Resistance REALES"""
        return self.detectar_niveles_sr_reales(par)
        
    def detectar_niveles_sr_reales(self, par):
        """Detectar niveles S/R REALES basados en datos históricos"""
        try:
            datos = self.indicadores.obtener_datos_historicos(par, "3mo", "4h")
            
            if not datos or len(datos['close']) < 100:
                print(f"⚠️ Datos insuficientes para S/R real de {par}, usando niveles base")
                return self._niveles_sr_base(par)
            
            highs = [h for h in datos['high'] if h is not None]
            lows = [l for l in datos['low'] if l is not None]
            closes = [c for c in datos['close'] if c is not None]
            
            if len(highs) < 50 or len(lows) < 50:
                return self._niveles_sr_base(par)
            
            # Detectar resistance (niveles donde el precio rechazó)
            resistances = self._detectar_pivots(highs, window=5, is_high=True)
            
            # Detectar support (niveles donde el precio rebotó)
            supports = self._detectar_pivots(lows, window=5, is_high=False)
            
            # Filtrar niveles relevantes (últimos 2 meses)
            precio_actual = closes[-1] if closes else self._get_precio_actual(par)
            resistances_relevantes = [r for r in resistances if r > precio_actual * 0.98]
            supports_relevantes = [s for s in supports if s < precio_actual * 1.02]
            
            # Ordenar y tomar los 2 más cercanos
            resistances_relevantes.sort()
            supports_relevantes.sort(reverse=True)
            
            niveles = {
                'support': supports_relevantes[:2] if supports_relevantes else self._niveles_sr_base(par)['support'],
                'resistance': resistances_relevantes[:2] if resistances_relevantes else self._niveles_sr_base(par)['resistance']
            }
            
            print(f"🏔️ {par} - S/R REALES: Support {[round(s, 4) for s in niveles['support']]}, Resistance {[round(r, 4) for r in niveles['resistance']]}")
            
            return niveles
            
        except Exception as e:
            print(f"❌ Error detectando S/R reales {par}: {e}")
            return self._niveles_sr_base(par)
    
    def _detectar_pivots(self, prices, window=5, is_high=True):
        """Detectar puntos pivote en los precios"""
        pivots = []
        
        for i in range(window, len(prices) - window):
            if prices[i] is None:
                continue
                
            if is_high:
                # Pivot high: el punto más alto en la ventana
                window_prices = [p for p in prices[i-window:i+window+1] if p is not None]
                if window_prices and prices[i] == max(window_prices):
                    pivots.append(prices[i])
            else:
                # Pivot low: el punto más bajo en la ventana
                window_prices = [p for p in prices[i-window:i+window+1] if p is not None]
                if window_prices and prices[i] == min(window_prices):
                    pivots.append(prices[i])
        
        # Eliminar duplicados cercanos (cluster de precios)
        pivots_unicos = []
        if pivots:
            avg_price = np.mean([p for p in pivots if p is not None])
            tolerance = avg_price * 0.002  # 0.2% de tolerancia
            
            for pivot in sorted(pivots):
                if not pivots_unicos or abs(pivot - pivots_unicos[-1]) > tolerance:
                    pivots_unicos.append(pivot)
        
        return pivots_unicos
    
    def _get_precio_actual(self, par):
        """Obtener precio actual como fallback"""
        from yahoo_api import YahooFinanceAPI
        yahoo = YahooFinanceAPI()
        return yahoo.obtener_precio_real(par) or 1.0
    
    def _niveles_sr_base(self, par):
        """Niveles base como fallback"""
        niveles_base = {
            'EURUSD': {'support': [1.0780, 1.0820], 'resistance': [1.0920, 1.0950]},
            'USDCAD': {'support': [1.3380, 1.3420], 'resistance': [1.3520, 1.3560]},
            'EURCHF': {'support': [0.9480, 0.9520], 'resistance': [0.9620, 0.9660]},
            'EURAUD': {'support': [1.6280, 1.6320], 'resistance': [1.6450, 1.6480]},
            'XAUUSD': {'support': [2170, 2180], 'resistance': [2200, 2210]},
            'XAGUSD': {'support': [24.50, 24.70], 'resistance': [25.00, 25.20]},
            'OILUSD': {'support': [77.0, 77.5], 'resistance': [79.0, 79.5]},
            'XPTUSD': {'support': [920, 925], 'resistance': [935, 940]},
        }
        return niveles_base.get(par, {'support': [1.0000, 1.0050], 'resistance': [1.0100, 1.0150]})
    
    def analizar_estructura_mercado(self, par, precio_actual, tendencia, rsi):
        """Análisis completo de estructura de mercado S/R"""
        # Obtener niveles S/R REALES
        niveles_sr = self.detectar_niveles_sr_reales(par)
        
        # Determinar proximidad a niveles clave
        distancia_support = min([abs(precio_actual - s) for s in niveles_sr['support']])
        distancia_resistance = min([abs(precio_actual - r) for r in niveles_sr['resistance']])
        
        # Determinar umbral según tipo de activo
        if par in ['XAUUSD', 'XAGUSD', 'XPTUSD']:  # Metales
            umbral_proximidad = precio_actual * 0.005  # 0.5%
        elif par in ['OILUSD']:  # Energía
            umbral_proximidad = precio_actual * 0.008  # 0.8%
        else:  # Forex
            umbral_proximidad = precio_actual * 0.002  # 0.2%
        
        # 🎯 ESTRATEGIA S/R ETAPA 1 - APLICABLE A TODOS LOS ACTIVOS
        condiciones_compra_alta = (
            distancia_support < umbral_proximidad and  # Cerca de support
            rsi < 32 and                              # RSI oversold
            tendencia == "ALCISTA"                    # Tendencia alcista
        )
        
        condiciones_venta_alta = (
            distancia_resistance < umbral_proximidad and  # Cerca de resistance
            rsi > 68 and                                  # RSI overbought  
            tendencia == "BAJISTA"                        # Tendencia bajista
        )
        
        # Condiciones COMPRA
        if condiciones_compra_alta:
            señal = "COMPRA"
            confianza = "ALTA"
            motivo = f"🎯 REBOTE S/R: {par} en Support + RSI Oversold + Tendencia Alcista"
        elif distancia_support < umbral_proximidad and rsi < 35:
            señal = "COMPRA" 
            confianza = "MEDIA"
            motivo = f"📊 {par} cerca de Support + RSI Bajista"
        else:
            señal = None
            confianza = "BAJA"
            motivo = f"❌ {par} - Condiciones no óptimas para compra"
                
        # Condiciones VENTA  
        if condiciones_venta_alta:
            señal = "VENTA"
            confianza = "ALTA" 
            motivo = f"🎯 RECHAZO S/R: {par} en Resistance + RSI Overbought + Tendencia Bajista"
        elif distancia_resistance < umbral_proximidad and rsi > 65:
            señal = "VENTA"
            confianza = "MEDIA"
            motivo = f"📊 {par} cerca de Resistance + RSI Alcista"
        
        if señal is None:
            confianza = "BAJA"
            motivo = f"⚡ {par} - Fuera de zonas S/R clave"
        
        return {
            'señal': señal,
            'confianza': confianza,
            'motivo': motivo,
            'niveles_sr': niveles_sr,
            'distancia_support': round(distancia_support, 5),
            'distancia_resistance': round(distancia_resistance, 5),
            'zona_actual': "SUPPORT" if distancia_support < distancia_resistance else "RESISTANCE" if distancia_resistance < distancia_support else "NEUTRAL"
        }
    
    def es_zona_compra_optima(self, analisis):
        """Verificar si es zona de compra óptima según S/R"""
        return (analisis['señal'] == "COMPRA" and 
                analisis['confianza'] in ["ALTA", "MEDIA"] and
                analisis['zona_actual'] == "SUPPORT")
    
    def es_zona_venta_optima(self, analisis):
        """Verificar si es zona de venta óptima según S/R"""
        return (analisis['señal'] == "VENTA" and 
                analisis['confianza'] in ["ALTA", "MEDIA"] and
                analisis['zona_actual'] == "RESISTANCE")
