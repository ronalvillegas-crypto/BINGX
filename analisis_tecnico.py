# analisis_tecnico.py - ESTRATEGIA S/R REAL DEL BACKTESTING
import random
from datetime import datetime, timedelta

class AnalisisTechnicoSR:
    def __init__(self):
        self.niveles_sr_historicos = {}
        
    def detectar_niveles_sr(self, par, datos_precios):
        """Detectar niveles de Support/Resistance basados en price action"""
        # Simulación de detección S/R real (en producción usaría datos históricos)
        niveles_base = {
            'EURUSD': {'support': [1.0780, 1.0820], 'resistance': [1.0920, 1.0950]},
            'USDCAD': {'support': [1.3380, 1.3420], 'resistance': [1.3520, 1.3560]},
            'EURCHF': {'support': [0.9480, 0.9520], 'resistance': [0.9620, 0.9660]},
            'EURAUD': {'support': [1.6280, 1.6320], 'resistance': [1.6450, 1.6480]}
        }
        
        return niveles_base.get(par, {'support': [1.0000, 1.0050], 'resistance': [1.0100, 1.0150]})
    
    def analizar_estructura_mercado(self, par, precio_actual, tendencia, rsi):
        """Análisis completo de estructura de mercado S/R - ESTRATEGIA BACKTESTING"""
        # Obtener niveles S/R
        niveles_sr = self.detectar_niveles_sr(par, [])
        
        # Determinar proximidad a niveles clave
        distancia_support = min([abs(precio_actual - s) for s in niveles_sr['support']])
        distancia_resistance = min([abs(precio_actual - r) for r in niveles_sr['resistance']])
        
        # 🎯 ESTRATEGIA S/R ETAPA 1 DEL BACKTESTING:
        # - Operar en rebotes de Support con RSI oversold + tendencia alcista
        # - Operar en rechazos de Resistance con RSI overbought + tendencia bajista
        # - Condiciones MÁS ESTRICTAS que la versión anterior
        
        # Condiciones COMPRA (Rebote en Support) - MÁS ESTRICTAS
        if distancia_support < 0.002:  # Muy cerca de support (20 pips)
            if rsi < 32 and tendencia == "ALCISTA":  # MÁS ESTRICTO
                señal = "COMPRA"
                confianza = "ALTA"
                motivo = "🎯 REBOTE S/R: Precio en Support + RSI Oversold + Tendencia Alcista"
            elif rsi < 35:  # Condición secundaria
                señal = "COMPRA" 
                confianza = "MEDIA"
                motivo = "📊 Acercamiento a Support + RSI Bajista"
            else:
                señal = None
                confianza = "BAJA"
                motivo = "❌ En Support pero RSI/Tendencia no óptimos"
                
        # Condiciones VENTA (Rechazo en Resistance) - MÁS ESTRICTAS  
        elif distancia_resistance < 0.002:  # Muy cerca de resistance (20 pips)
            if rsi > 68 and tendencia == "BAJISTA":  # MÁS ESTRICTO
                señal = "VENTA"
                confianza = "ALTA" 
                motivo = "🎯 RECHAZO S/R: Precio en Resistance + RSI Overbought + Tendencia Bajista"
            elif rsi > 65:  # Condición secundaria
                señal = "VENTA"
                confianza = "MEDIA"
                motivo = "📊 Acercamiento a Resistance + RSI Alcista"
            else:
                señal = None
                confianza = "BAJA"
                motivo = "❌ En Resistance pero RSI/Tendencia no óptimos"
                
        else:
            # Zona neutral - no operar (FILTRO IMPORTANTE)
            señal = None
            confianza = "BAJA"
            motivo = "⚡ Fuera de zonas S/R clave - NO OPERAR"
        
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
        """Verificar si es zona de compra óptima según S/R - BACKTESTING"""
        return (analisis['señal'] == "COMPRA" and 
                analisis['confianza'] in ["ALTA", "MEDIA"] and
                analisis['zona_actual'] == "SUPPORT")
    
    def es_zona_venta_optima(self, analisis):
        """Verificar si es zona de venta óptima según S/R - BACKTESTING"""
        return (analisis['señal'] == "VENTA" and 
                analisis['confianza'] in ["ALTA", "MEDIA"] and
                analisis['zona_actual'] == "RESISTANCE")
