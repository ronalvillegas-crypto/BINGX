# analisis_tecnico.py - ESTRATEGIA S/R REAL DEL BACKTESTING
import random
from datetime import datetime, timedelta

class AnalisisTechnicoSR:
    def __init__(self):
        self.niveles_sr_historicos = {}
        
    def detectar_niveles_sr(self, par, datos_precios):
        """Detectar niveles de Support/Resistance basados en price action"""
        niveles_base = {
            'EURUSD': {'support': [1.0780, 1.0820], 'resistance': [1.0920, 1.0950]},
            'USDCAD': {'support': [1.3380, 1.3420], 'resistance': [1.3520, 1.3560]},
            'EURCHF': {'support': [0.9480, 0.9520], 'resistance': [0.9620, 0.9660]},
            'EURAUD': {'support': [1.6280, 1.6320], 'resistance': [1.6450, 1.6480]}
        }
        
        return niveles_base.get(par, {'support': [1.0000, 1.0050], 'resistance': [1.0100, 1.0150]})
    
    def analizar_estructura_mercado(self, par, precio_actual, tendencia, rsi):
        """Análisis completo de estructura de mercado S/R"""
        niveles_sr = self.detectar_niveles_sr(par, [])
        
        distancia_support = min([abs(precio_actual - s) for s in niveles_sr['support']])
        distancia_resistance = min([abs(precio_actual - r) for r in niveles_sr['resistance']])
        
        # Condiciones COMPRA (Rebote en Support)
        if distancia_support < distancia_resistance * 0.5:
            if rsi < 35 and tendencia == "ALCISTA":
                señal = "COMPRA"
                confianza = "ALTA"
                motivo = "Rebote en Support + RSI Oversold + Tendencia Alcista"
            elif rsi < 40:
                señal = "COMPRA" 
                confianza = "MEDIA"
                motivo = "Acercamiento a Support + RSI Bajista"
            else:
                señal = None
                confianza = "BAJA"
                motivo = "Sin señal clara"
                
        # Condiciones VENTA (Rechazo en Resistance)  
        elif distancia_resistance < distancia_support * 0.5:
            if rsi > 65 and tendencia == "BAJISTA":
                señal = "VENTA"
                confianza = "ALTA" 
                motivo = "Rechazo en Resistance + RSI Overbought + Tendencia Bajista"
            elif rsi > 60:
                señal = "VENTA"
                confianza = "MEDIA"
                motivo = "Acercamiento a Resistance + RSI Alcista"
            else:
                señal = None
                confianza = "BAJA"
                motivo = "Sin señal clara"
                
        else:
            señal = None
            confianza = "BAJA"
            motivo = "Zona neutral - fuera de niveles S/R clave"
        
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
        return (analisis['señal'] == "COMPRA" and 
                analisis['confianza'] in ["ALTA", "MEDIA"] and
                analisis['zona_actual'] == "SUPPORT")
    
    def es_zona_venta_optima(self, analisis):
        return (analisis['señal'] == "VENTA" and 
                analisis['confianza'] in ["ALTA", "MEDIA"] and
                analisis['zona_actual'] == "RESISTANCE")
