# simulador_avanzado.py - SIMULACIÓN MÁS REALISTA
import numpy as np
import random
from datetime import datetime, timedelta

class SimuladorAvanzado:
    def __init__(self):
        self.volatilidad_historica = {
            'EURUSD': 0.0008, 'USDCAD': 0.0009, 'EURCHF': 0.0007, 'EURAUD': 0.0012,
            'XAUUSD': 0.005, 'XAGUSD': 0.008, 'OILUSD': 0.015, 'XPTUSD': 0.006
        }
    
    def simular_movimiento_realista(self, par, direccion, precio_inicial, duracion_horas=1):
        """Simular movimiento de precio REALISTA basado en volatilidad histórica"""
        volatilidad = self.volatilidad_historica.get(par, 0.005)
        
        # Simular camino de precio (random walk con drift)
        precios = [precio_inicial]
        steps = duracion_horas * 12  # 5-min intervals
        
        for i in range(steps):
            # Drift basado en dirección (ligera tendencia según señal)
            drift_direction = 1 if direccion == "COMPRA" else -1
            drift = volatilidad * 0.05 * drift_direction
            
            # Movimiento aleatorio (distribución normal)
            movimiento = np.random.normal(drift, volatilidad)
            
            # Añadir algo de mean reversion
            if i > 10:
                mean_price = np.mean(precios[-10:])
                reversion = (mean_price - precios[-1]) * 0.01
                movimiento += reversion
            
            nuevo_precio = precios[-1] * (1 + movimiento)
            precios.append(max(nuevo_precio, 0.0001))  # Evitar precios negativos
        
        return precios
    
    def simular_operacion_realista(self, operacion, duracion_maxima=6):
        """Simular operación de forma REALISTA"""
        par = operacion['par']
        direccion = operacion['direccion']
        precio_entrada = operacion['precio_entrada']
        
        # Generar camino de precio realista (más corto para simulación más rápida)
        camino_precio = self.simular_movimiento_realista(par, direccion, precio_entrada, duracion_maxima)
        
        # Verificar TP/SL en cada paso del camino
        for precio in camino_precio:
            resultado = self._verificar_objetivos(operacion, precio)
            if resultado:
                return resultado
        
        # Si no se alcanzó TP/SL en el tiempo máximo, cerrar al precio final
        precio_final = camino_precio[-1]
        profit_pct = self._calcular_profit(operacion, precio_final)
        
        if profit_pct > 0:
            resultado_str = 'TP1'
        else:
            resultado_str = 'SL'
            
        return {
            'resultado': resultado_str,
            'precio_cierre': precio_final,
            'profit': profit_pct
        }
    
    def _verificar_objetivos(self, operacion, precio_actual):
        """Verificar si se alcanzó TP o SL"""
        if operacion['direccion'] == "COMPRA":
            if precio_actual >= operacion['tp2']:
                return {'resultado': 'TP2', 'precio_cierre': precio_actual}
            elif precio_actual >= operacion['tp1']:
                return {'resultado': 'TP1', 'precio_cierre': precio_actual}
            elif precio_actual <= operacion['sl']:
                return {'resultado': 'SL', 'precio_cierre': precio_actual}
        else:  # VENTA
            if precio_actual <= operacion['tp2']:
                return {'resultado': 'TP2', 'precio_cierre': precio_actual}
            elif precio_actual <= operacion['tp1']:
                return {'resultado': 'TP1', 'precio_cierre': precio_actual}
            elif precio_actual >= operacion['sl']:
                return {'resultado': 'SL', 'precio_cierre': precio_actual}
        
        return None
    
    def _calcular_profit(self, operacion, precio_cierre):
        """Calcular porcentaje de profit"""
        if operacion['direccion'] == "COMPRA":
            profit_pct = ((precio_cierre - operacion['precio_promedio']) / operacion['precio_promedio']) * 100
        else:
            profit_pct = ((operacion['precio_promedio'] - precio_cierre) / operacion['precio_promedio']) * 100
        
        # Aplicar leverage
        leverage = operacion.get('leverage', 1)
        return profit_pct * leverage
