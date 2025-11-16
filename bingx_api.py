# bingx_api.py - Monitoreo REAL con BingX API
import os
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BingXMonitor:
    def __init__(self):
        self.base_url = "https://open-api.bingx.com"
        
        # ✅ FORMATO CORRECTO para Forex en BingX
        self.simbolos_forex = {
            'USDCAD': 'USD-CAD', 
            'USDJPY': 'USD-JPY',
            'AUDUSD': 'AUD-USD',
            'EURGBP': 'EUR-GBP', 
            'GBPUSD': 'GBP-USD'
        }
    
    def obtener_precio_real(self, simbolo):
        """Obtener precio REAL de BingX"""
        try:
            bingx_symbol = self.simbolos_forex.get(simbolo)
            if not bingx_symbol:
                logger.warning(f"Símbolo no soportado: {simbolo}")
                return None
            
            url = f"{self.base_url}/openApi/spot/v1/ticker/price"
            params = {'symbol': bingx_symbol}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0 and 'data' in data:
                    precio = float(data['data']['price'])
                    logger.info(f"✅ Precio REAL {simbolo}: {precio:.5f}")
                    return precio
            
            logger.warning(f"❌ No se pudo obtener precio para {simbolo}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error BingX API {simbolo}: {e}")
            return None
    
    def obtener_datos_tecnicos(self, simbolo, intervalo='5m', limite=50):
        """Obtener datos para análisis técnico"""
        try:
            bingx_symbol = self.simbolos_forex.get(simbolo)
            if not bingx_symbol:
                return None
            
            url = f"{self.base_url}/openApi/spot/v1/market/klines"
            params = {
                'symbol': bingx_symbol,
                'interval': intervalo,
                'limit': limite
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0 and 'data' in data:
                    return self._procesar_datos_tecnicos(data['data'])
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error datos técnicos {simbolo}: {e}")
            return None
    
    def _procesar_datos_tecnicos(self, klines_data):
        """Procesar datos de velas para análisis técnico"""
        if not klines_data:
            return None
        
        try:
            # ✅ FORMATO CORRECTO de velas BingX: [timestamp, open, high, low, close, volume]
            closes = [float(candle[4]) for candle in klines_data]  # Precio cierre
            
            # Calcular RSI simple
            rsi = self._calcular_rsi_simple(closes)
            
            # Determinar tendencia
            tendencia = self._determinar_tendencia(closes)
            
            return {
                'precio_actual': closes[-1],
                'rsi': rsi,
                'tendencia': tendencia,
                'volatilidad': (max(closes) - min(closes)) / min(closes) * 100,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            logger.error(f"❌ Error procesando datos técnicos: {e}")
            return None
    
    def _calcular_rsi_simple(self, closes, periodo=14):
        """Calcular RSI simplificado"""
        if len(closes) < periodo + 1:
            return 50  # Valor neutral por defecto
        
        gains = []
        losses = []
        
        for i in range(1, len(closes)):
            cambio = closes[i] - closes[i-1]
            if cambio > 0:
                gains.append(cambio)
            else:
                losses.append(abs(cambio))
        
        avg_gain = sum(gains[-periodo:]) / periodo if gains else 0
        avg_loss = sum(losses[-periodo:]) / periodo if losses else 0
        
        if avg_loss == 0:
            return 100 if avg_gain > 0 else 50
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    def _determinar_tendencia(self, closes, periodo=20):
        """Determinar tendencia basada en medias móviles"""
        if len(closes) < periodo:
            return "LATERAL"
        
        corto_plazo = sum(closes[-10:]) / 10
        largo_plazo = sum(closes[-periodo:]) / periodo
        
        if corto_plazo > largo_plazo * 1.002:
            return "ALCISTA"
        elif corto_plazo < largo_plazo * 0.998:
            return "BAJISTA"
        else:
            return "LATERAL"
    
    def verificar_conexion(self):
        """Verificar que BingX API está funcionando"""
        try:
            test_symbol = 'USD-CAD'
            url = f"{self.base_url}/openApi/spot/v1/ticker/price"
            params = {'symbol': test_symbol}
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    print("✅ BingX API: CONEXIÓN EXITOSA")
                    return True
            
            print("❌ BingX API: ERROR DE CONEXIÓN")
            return False
            
        except Exception as e:
            print(f"❌ BingX API: ERROR - {e}")
            return False
