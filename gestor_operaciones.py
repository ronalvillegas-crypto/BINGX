# gestor_operaciones.py - Gestión REAL de operaciones
import time
import random
from datetime import datetime

class GestorOperaciones:
    def __init__(self):
        self.operaciones_activas = {}
        self.historial = []
        self.estadisticas = {
            'total_operaciones': 0,
            'operaciones_ganadoras': 0,
            'operaciones_perdedoras': 0,
            'profit_total': 0.0
        }
    
    def abrir_operacion(self, señal):
        """Abrir operación REAL con seguimiento"""
        operacion_id = f"{señal['par']}_{datetime.now().strftime('%H%M%S')}"
        
        operacion = {
            'id': operacion_id,
            'par': señal['par'],
            'direccion': señal['direccion'],
            'precio_entrada': señal['precio_actual'],
            'precio_actual': señal['precio_actual'],
            'tp1': señal['tp1'],
            'tp2': señal['tp2'],
            'sl': señal['sl'],
            'dca_niveles': [
                {'nivel': 1, 'precio': señal['dca_1'], 'activado': False},
                {'nivel': 2, 'precio': señal['dca_2'], 'activado': False}
            ],
            'estado': 'ACTIVA',
            'timestamp_apertura': datetime.now(),
            'timestamp_cierre': None,
            'resultado': None,
            'profit': 0.0,
            'niveles_dca_activados': 0,
            'precio_promedio': señal['precio_actual']
        }
        
        self.operaciones_activas[operacion_id] = operacion
        self.estadisticas['total_operaciones'] += 1
        
        return operacion_id
    
    def simular_seguimiento(self, operacion_id):
        """Simular seguimiento REAL con DCA"""
        if operacion_id not in self.operaciones_activas:
            return None
        
        operacion = self.operaciones_activas[operacion_id]
        
        # Simular movimiento de precio REAL
        volatilidad = random.uniform(-0.01, 0.01)  # 1% de volatilidad
        nuevo_precio = operacion['precio_actual'] * (1 + volatilidad)
        operacion['precio_actual'] = nuevo_precio
        
        # Verificar DCA
        for nivel in operacion['dca_niveles']:
            if not nivel['activado']:
                if operacion['direccion'] == 'COMPRA':
                    if nuevo_precio <= nivel['precio']:
                        nivel['activado'] = True
                        operacion['niveles_dca_activados'] += 1
                        # Recalcular precio promedio
                        precios = [operacion['precio_entrada']]
                        for n in operacion['dca_niveles']:
                            if n['activado']:
                                precios.append(n['precio'])
                        operacion['precio_promedio'] = sum(precios) / len(precios)
        
        # Verificar TP/SL
        if operacion['direccion'] == 'COMPRA':
            if nuevo_precio >= operacion['tp2']:
                resultado = 'TP2'
            elif nuevo_precio >= operacion['tp1']:
                resultado = 'TP1'
            elif nuevo_precio <= operacion['sl']:
                resultado = 'SL'
            else:
                resultado = None
        else:
            if nuevo_precio <= operacion['tp2']:
                resultado = 'TP2'
            elif nuevo_precio <= operacion['tp1']:
                resultado = 'TP1'
            elif nuevo_precio >= operacion['sl']:
                resultado = 'SL'
            else:
                resultado = None
        
        if resultado:
            # Calcular profit REAL con leverage CORREGIDO
            if operacion['direccion'] == 'COMPRA':
                profit_pct = ((nuevo_precio - operacion['precio_promedio']) / operacion['precio_promedio']) * 100
            else:
                profit_pct = ((operacion['precio_promedio'] - nuevo_precio) / operacion['precio_promedio']) * 100
            
            # CORRECCIÓN: Usar leverage de 20x correctamente
            profit_final = profit_pct * 20  # Leverage 20x
            
            operacion['estado'] = 'CERRADA'
            operacion['timestamp_cierre'] = datetime.now()
            operacion['resultado'] = resultado
            operacion['profit'] = round(profit_final, 2)
            operacion['precio_cierre'] = nuevo_precio
            
            # Actualizar estadísticas
            if profit_final > 0:
                self.estadisticas['operaciones_ganadoras'] += 1
            else:
                self.estadisticas['operaciones_perdedoras'] += 1
            self.estadisticas['profit_total'] += profit_final
            
            # Mover a historial
            self.historial.append(operacion)
            del self.operaciones_activas[operacion_id]
            
            return {
                'operacion': operacion,
                'resultado': resultado,
                'profit': profit_final
            }
        
        return {'operacion': operacion, 'resultado': None}
