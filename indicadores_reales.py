# indicadores_reales.py - CÁLCULO REAL DE INDICADORES
import requests
import numpy as np
from datetime import datetime, timedelta

class IndicadoresReales:
    def __init__(self):
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart"
    
    def obtener_datos_historicos(self, simbolo, periodo="1mo", intervalo="1h"):
        """Obtener datos históricos REALES de Yahoo Finance"""
        try:
            symbol_mapping = {
                "EURUSD": "EURUSD=X", "USDCAD": "CAD=X", "EURCHF": "EURCHF=X", "EURAUD": "EURAUD=X",
                "XAUUSD": "GC=F", "XAGUSD": "SI=F", "OILUSD": "CL=F", "XPTUSD": "PL=F"
            }
            
            yahoo_symbol = symbol_mapping.get(simbolo)
            if not yahoo_symbol:
                return None
            
            url = f"{self.base_url}/{yahoo_symbol}"
            params = {
                'range': periodo,
                'interval': intervalo
            }
            
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                    result = data['chart']['result'][0]
                    timestamps = result['timestamp']
                    prices = result['indicators']['quote'][0]
                    
                    # Extraer precios de cierre
                    closes = prices['close']
                    highs = prices['high']
                    lows = prices['low']
                    
                    return {
                        'timestamp': timestamps,
                        'close': closes,
                        'high': highs,
                        'low': lows
                    }
            return None
            
        except Exception as e:
            print(f"❌ Error datos históricos {simbolo}: {e}")
            return None
    
    def calcular_rsi_real(self, precios, periodo=14):
        """Calcular RSI REAL con fórmula estándar"""
        if len(precios) < periodo + 1:
            return 50  # Valor neutral si no hay suficientes datos
        
        # Calcular cambios de precio
        deltas = np.diff(precios)
        
        # Separar ganancias y pérdidas
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        # Calcular promedio de ganancias/pérdidas
        avg_gains = []
        avg_losses = []
        
        for i in range(periodo, len(gains)):
            avg_gain = np.mean(gains[i-periodo:i])
            avg_loss = np.mean(losses[i-periodo:i])
            avg_gains.append(avg_gain)
            avg_losses.append(avg_loss)
        
        if not avg_gains or not avg_losses:
            return 50
        
        # Calcular RS y RSI
        rs_values = []
        for i in range(len(avg_gains)):
            if avg_losses[i] == 0:
                rs = 100  # Evitar división por cero
            else:
                rs = avg_gains[i] / avg_losses[i]
            rsi = 100 - (100 / (1 + rs))
            rs_values.append(rsi)
        
        return round(float(rs_values[-1]), 2) if rs_values else 50
    
    def determinar_tendencia(self, precios, periodo=20):
        """Determinar tendencia REAL basada en medias móviles"""
        if len(precios) < periodo:
            return "LATERAL"
        
        # Calcular medias móviles
        ma_rapida = np.mean(precios[-periodo//2:])  # MA rápida (10 periodos)
        ma_lenta = np.mean(precios[-periodo:])      # MA lenta (20 periodos)
        
        # Determinar tendencia
        if ma_rapida > ma_lenta * 1.002:  # 0.2% de diferencia
            return "ALCISTA"
        elif ma_rapida < ma_lenta * 0.998:
            return "BAJISTA"
        else:
            return "LATERAL"
    
    def obtener_indicadores_reales(self, simbolo):
        """Obtener todos los indicadores REALES"""
        try:
            # Obtener datos históricos (último mes, 1h timeframe)
            datos = self.obtener_datos_historicos(simbolo, "1mo", "1h")
            
            if not datos or len(datos['close']) < 50:
                print(f"⚠️ Datos insuficientes para {simbolo}, usando cálculo básico")
                return self._indicadores_basicos(simbolo)
            
            precios_cierre = [p for p in datos['close'] if p is not None]
            
            if len(precios_cierre) < 20:
                return self._indicadores_basicos(simbolo)
            
            # Calcular indicadores REALES
            rsi_real = self.calcular_rsi_real(precios_cierre)
            tendencia_real = self.determinar_tendencia(precios_cierre)
            
            print(f"📊 {simbolo} - RSI REAL: {rsi_real}, Tendencia REAL: {tendencia_real}")
            
            return {
                'rsi': rsi_real,
                'tendencia': tendencia_real,
                'precio_actual': precios_cierre[-1],
                'fuente': 'Cálculo Real'
            }
            
        except Exception as e:
            print(f"❌ Error calculando indicadores reales {simbolo}: {e}")
            return self._indicadores_basicos(simbolo)
    
    def _indicadores_basicos(self, simbolo):
        """Fallback a cálculo básico si falla el real"""
        from yahoo_api import YahooFinanceAPI
        yahoo = YahooFinanceAPI()
        precio = yahoo.obtener_precio_real(simbolo)
        
        # Cálculo básico mejorado
        precios_base = {"EURUSD": 1.0850, "XAUUSD": 2185.50, "USDCAD": 1.3450}
        precio_base = precios_base.get(simbolo, precio if precio else 1.0)
        
        if precio:
            desviacion = (precio - precio_base) / precio_base
            rsi = 50 + (desviacion * 30)  # Menos sensible que antes
            rsi = max(10, min(90, rsi))
        else:
            rsi = 50
        
        # Tendencia básica
        if rsi < 40:
            tendencia = "ALCISTA"
        elif rsi > 60:
            tendencia = "BAJISTA"
        else:
            tendencia = "LATERAL"
        
        return {
            'rsi': round(rsi, 2),
            'tendencia': tendencia,
            'precio_actual': precio,
            'fuente': 'Cálculo Básico'
        }
