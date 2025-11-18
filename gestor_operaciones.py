# gestor_operaciones.py - GESTIÓN REAL DE OPERACIONES CON SIMULACIÓN AVANZADA
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
        # IMPORTAR DENTRO DEL MÉTODO CUANDO SE NECESITE
        self.simulador = None
    
    def _get_simulador(self):
        """Obtener simulador (lazy loading)"""
        if self.simulador is None:
            from simulador_avanzado import SimuladorAvanzado
            self.simulador = SimuladorAvanzado()
        return self.simulador
    
    def abrir_operacion(self, señal):
        """Abrir operación REAL con seguimiento - TIMESTAMP CORREGIDO"""
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
            'timestamp_apertura': datetime.now(),  # ✅ OBJETO DATETIME
            'timestamp_cierre': None,
            'resultado': None,
            'profit': 0.0,
            'niveles_dca_activados': 0,
            'precio_promedio': señal['precio_actual'],
            'leverage': señal.get('leverage', 1)
        }
        
        self.operaciones_activas[operacion_id] = operacion
        self.estadisticas['total_operaciones'] += 1
        
        return operacion_id
    
    def simular_seguimiento(self, operacion_id):
        """Seguimiento MÁS REALISTA con simulador avanzado"""
        if operacion_id not in self.operaciones_activas:
            return None
        
        operacion = self.operaciones_activas[operacion_id]
        
        # Verificar DCA primero
        self._verificar_dca(operacion)
        
        # Usar simulador avanzado en lugar de movimiento aleatorio simple
        simulador = self._get_simulador()
        resultado = simulador.simular_operacion_realista(operacion)
        
        if resultado:
            # Calcular profit REALISTA
            profit = resultado.get('profit', self._calcular_profit_realista(operacion, resultado['precio_cierre']))
            
            operacion['estado'] = 'CERRADA'
            operacion['timestamp_cierre'] = datetime.now()  # ✅ OBJETO DATETIME
            operacion['resultado'] = resultado['resultado']
            operacion['profit'] = profit
            operacion['precio_cierre'] = resultado['precio_cierre']
            
            # Actualizar estadísticas
            if profit > 0:
                self.estadisticas['operaciones_ganadoras'] += 1
            else:
                self.estadisticas['operaciones_perdedoras'] += 1
            self.estadisticas['profit_total'] += profit
            
            # Mover a historial
            self.historial.append(operacion)
            del self.operaciones_activas[operacion_id]
            
            return {
                'operacion': operacion,
                'resultado': resultado['resultado'],
                'profit': profit
            }
        
        return {'operacion': operacion, 'resultado': None}
    
    def _verificar_dca(self, operacion):
        """Verificar y activar niveles DCA"""
        precio_actual = operacion['precio_actual']
        
        for nivel in operacion['dca_niveles']:
            if not nivel['activado']:
                if operacion['direccion'] == 'COMPRA':
                    if precio_actual <= nivel['precio']:
                        nivel['activado'] = True
                        operacion['niveles_dca_activados'] += 1
                        # Recalcular precio promedio
                        self._recalcular_precio_promedio(operacion)
                else:  # VENTA
                    if precio_actual >= nivel['precio']:
                        nivel['activado'] = True
                        operacion['niveles_dca_activados'] += 1
                        # Recalcular precio promedio
                        self._recalcular_precio_promedio(operacion)
    
    def _recalcular_precio_promedio(self, operacion):
        """Recalcular precio promedio después de DCA"""
        precios = [operacion['precio_entrada']]
        for nivel in operacion['dca_niveles']:
            if nivel['activado']:
                precios.append(nivel['precio'])
        
        operacion['precio_promedio'] = sum(precios) / len(precios)
    
    def _calcular_profit_realista(self, operacion, precio_cierre):
        """Calcular profit de forma REALISTA con leverage"""
        if operacion['direccion'] == "COMPRA":
            profit_pct = ((precio_cierre - operacion['precio_promedio']) / operacion['precio_promedio']) * 100
        else:
            profit_pct = ((operacion['precio_promedio'] - precio_cierre) / operacion['precio_promedio']) * 100
        
        # Aplicar leverage
        profit_final = profit_pct * operacion.get('leverage', 1)
        return round(profit_final, 2)
