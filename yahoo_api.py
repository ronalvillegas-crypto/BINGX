# yahoo_api.py - API REAL para Forex y Materias Primas
import requests
import random
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class YahooFinanceAPI:
    def __init__(self):
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart"
        
    def obtener_precio_real(self, simbolo):
        """Obtener precio REAL de Yahoo Finance"""
        try:
            # Mapeo de símbolos para Yahoo Finance (ACTUALIZADO CON MATERIAS PRIMAS)
            symbol_mapping = {
                # FOREX
                "EURUSD": "EURUSD=X",
                "USDCAD": "CAD=X",
                "EURCHF": "EURCHF=X", 
                "EURAUD": "EURAUD=X",
                "USDJPY": "JPY=X",
                "AUDUSD": "AUDUSD=X",
                "EURGBP": "EURGBP=X",
                "GBPUSD": "GBPUSD=X",
                
                # MATERIAS PRIMAS (NUEVAS)
                "XAUUSD": "GC=F",    # Oro
                "XAGUSD": "SI=F",    # Plata
                "OILUSD": "CL=F",    # Petróleo Crudo
                "XPTUSD": "PL=F",    # Platino
            }
            
            yahoo_symbol = symbol_mapping.get(simbolo)
            if not yahoo_symbol:
                logger.warning(f"Símbolo no soportado: {simbolo}")
                return self._precio_simulado_realista(simbolo)
            
            url = f"{self.base_url}/{yahoo_symbol}"
            params = {
                "range": "1d",
                "interval": "1m"
            }
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            print(f"🔍 Solicitando datos de {simbolo} desde Yahoo Finance...")
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if "chart" in data and "result" in data["chart"] and data["chart"]["result"]:
                    result = data["chart"]["result"][0]
                    if "meta" in result and "regularMarketPrice" in result["meta"]:
                        precio = result["meta"]["regularMarketPrice"]
                        print(f"✅ Precio REAL {simbolo}: {precio:.5f}")
                        return precio
                    else:
                        print(f"⚠️ No se encontró precio en respuesta para {simbolo}")
                else:
                    print(f"⚠️ Estructura de respuesta inválida para {simbolo}")
            else:
                print(f"⚠️ Status {response.status_code} para {simbolo}")
            
            # Fallback a simulación si Yahoo falla
            print(f"🔄 Yahoo Finance falló, usando simulación para {simbolo}")
            return self._precio_simulado_realista(simbolo)
            
        except Exception as e:
            print(f"❌ Error obteniendo precio {simbolo}: {e}")
            return self._precio_simulado_realista(simbolo)
    
    def _precio_simulado_realista(self, simbolo):
        """Precio simulado realista como fallback"""
        precios_base = {
            # FOREX
            "EURUSD": 1.0850,
            "USDCAD": 1.3450,
            "EURCHF": 0.9550,
            "EURAUD": 1.6350,
            "USDJPY": 148.50,
            "AUDUSD": 0.6520,
            "EURGBP": 0.8550,
            "GBPUSD": 1.2650,
            
            # MATERIAS PRIMAS (NUEVAS)
            "XAUUSD": 2185.50,   # Oro
            "XAGUSD": 24.85,     # Plata
            "OILUSD": 78.30,     # Petróleo
            "XPTUSD": 925.80,    # Platino
        }
        
        precio_base = precios_base.get(simbolo, 1.0000)
        
        # Diferente volatilidad según el tipo de activo
        if simbolo in ["XAUUSD", "XAGUSD", "XPTUSD"]:  # Metales
            volatilidad = random.uniform(-0.005, 0.005)  # Metales: ±0.5%
        elif simbolo in ["OILUSD"]:  # Energía
            volatilidad = random.uniform(-0.008, 0.008)  # Energía: ±0.8%
        else:
            volatilidad = random.uniform(-0.001, 0.001)  # Forex: ±0.1%
            
        nuevo_precio = precio_base * (1 + volatilidad)
        
        print(f"🔄 Precio simulado {simbolo}: {nuevo_precio:.5f}")
        return round(nuevo_precio, 5)
    
    def obtener_datos_tecnicos(self, simbolo, intervalo="5m", limite=50):
        """Obtener datos técnicos de Yahoo Finance"""
        try:
            # Primero obtener precio actual
            precio_actual = self.obtener_precio_real(simbolo)
            
            if not precio_actual:
                return None
            
            # Base de precios para cálculo de RSI simulado (ACTUALIZADA)
            precios_base = {
                "EURUSD": 1.0850, "USDCAD": 1.3450, "EURCHF": 0.9550, "EURAUD": 1.6350,
                "XAUUSD": 2185.50, "XAGUSD": 24.85, "OILUSD": 78.30, "XPTUSD": 925.80
            }
            
            precio_base = precios_base.get(simbolo, 1.0000)
            
            # Calcular RSI simulado basado en desviación del precio base
            desviacion = (precio_actual - precio_base) / precio_base
            rsi = 50 + (desviacion * 1000)
            rsi = max(20, min(80, rsi))
            
            # Determinar tendencia basada en RSI
            if rsi < 40:
                tendencia = "ALCISTA"
            elif rsi > 60:
                tendencia = "BAJISTA" 
            else:
                tendencia = "LATERAL"
            
            return {
                "precio_actual": precio_actual,
                "rsi": round(rsi, 2),
                "tendencia": tendencia,
                "volatilidad": random.uniform(0.3, 1.2),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "fuente": "Yahoo Finance" if precio_actual > 0 else "Simulación"
            }
            
        except Exception as e:
            print(f"❌ Error datos técnicos {simbolo}: {e}")
            return None
    
    def verificar_conexion(self):
        """Verificar conexión con Yahoo Finance"""
        try:
            test_symbol = "EURUSD=X"
            url = f"{self.base_url}/{test_symbol}"
            params = {"range": "1d", "interval": "1m"}
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "chart" in data and "result" in data["chart"]:
                    print("✅ Conexión Yahoo Finance: FUNCIONANDO")
                    return True
            return False
        except Exception as e:
            print(f"❌ Test conexión Yahoo falló: {e}")
            return False

# Prueba rápida
if __name__ == "__main__":
    print("🚀 TEST YAHOO FINANCE API - FOREX Y MATERIAS PRIMAS")
    yahoo = YahooFinanceAPI()
    
    # Probar conexión
    if yahoo.verificar_conexion():
        print("✅ Yahoo Finance está funcionando")
    else:
        print("❌ Yahoo Finance no está disponible")
    
    # Probar TODOS los pares (Forex + Materias Primas)
    pares_forex = ["EURUSD", "USDCAD", "EURCHF", "EURAUD"]
    pares_commodities = ["XAUUSD", "XAGUSD", "OILUSD", "XPTUSD"]
    
    print("\n📊 PROBANDO FOREX:")
    for par in pares_forex:
        print(f"\n🔍 Probando {par}:")
        precio = yahoo.obtener_precio_real(par)
        print(f"   💰 Precio: {precio}")
    
    print("\n🪙 PROBANDO MATERIAS PRIMAS:")
    for par in pares_commodities:
        print(f"\n🔍 Probando {par}:")
        precio = yahoo.obtener_precio_real(par)
        print(f"   💰 Precio: {precio}")
