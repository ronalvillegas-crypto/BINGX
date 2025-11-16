# monitor_mercado.py - Monitoreo en tiempo real
import time
import threading
from datetime import datetime
from config import TOP_5_PARES
from bingx_api import BingXMonitor
from estrategia_dca import EstrategiaDCA
from gestor_operaciones import GestorOperaciones
from telegram_bot import TelegramBotReal

class MonitorMercado:
    def __init__(self):
        self.bingx = BingXMonitor()
        self.estrategia = EstrategiaDCA()
        self.gestor = GestorOperaciones()
        self.telegram = TelegramBotReal()
        self.monitoreando = False
        self.ultima_señal_por_par = {}  # Evitar señales repetidas
        
    def analizar_par(self, par):
        """Analizar un par en busca de oportunidades REALES"""
        try:
            # Obtener datos en tiempo real
            datos_reales = self.bingx.obtener_datos_tecnicos(par)
            
            if not datos_reales:
                return None
            
            # CONDICIONES PARA SEÑAL REAL (personaliza según tu estrategia)
            condiciones_compra = (
                datos_reales['rsi'] < 35 and 
                datos_reales['tendencia'] == 'ALCISTA' and
                datos_reales['volatilidad'] > 0.5
            )
            
            condiciones_venta = (
                datos_reales['rsi'] > 65 and 
                datos_reales['tendencia'] == 'BAJISTA' and
                datos_reales['volatilidad'] > 0.5
            )
            
            # Verificar si hay oportunidad
            if condiciones_compra or condiciones_venta:
                # Evitar señales repetidas (mínimo 1 hora entre señales del mismo par)
                ultima_señal = self.ultima_señal_por_par.get(par)
                if ultima_señal and (datetime.now() - ultima_señal).seconds < 3600:
                    return None
                
                # GENERAR SEÑAL REAL
                señal = self.estrategia.generar_señal_real(par)
                self.ultima_señal_por_par[par] = datetime.now()
                
                return señal
                
            return None
            
        except Exception as e:
            print(f"❌ Error analizando {par}: {e}")
            return None
    
    def ejecutar_señal(self, señal):
        """Ejecutar una señal detectada"""
        try:
            # Abrir operación
            operacion_id = self.gestor.abrir_operacion(señal)
            
            # Enviar a Telegram
            self.telegram.enviar_señal_completa(señal)
            
            # Iniciar seguimiento automático
            self.iniciar_seguimiento(operacion_id)
            
            print(f"✅ SEÑAL EJECUTADA: {señal['par']} {señal['direccion']}")
            
        except Exception as e:
            print(f"❌ Error ejecutando señal: {e}")
    
    def iniciar_seguimiento(self, operacion_id):
        """Seguir operación hasta cierre"""
        def seguir():
            intentos = 0
            while intentos < 50:  # Máximo 50 verificaciones
                time.sleep(30)  # Verificar cada 30 segundos
                
                resultado = self.gestor.simular_seguimiento(operacion_id)
                
                if resultado and resultado['resultado']:
                    # Operación CERRADA - enviar notificación
                    self.telegram.enviar_cierre_operacion(resultado['operacion'])
                    break
                    
                intentos += 1
        
        threading.Thread(target=seguir, daemon=True).start()
    
    def iniciar_monitoreo(self):
        """Iniciar monitoreo continuo"""
        self.monitoreando = True
        print("🔍 INICIANDO MONITOREO EN TIEMPO REAL...")
        
        while self.monitoreando:
            try:
                for par in TOP_5_PARES:
                    # Analizar cada par
                    señal = self.analizar_par(par)
                    
                    if señal:
                        self.ejecutar_señal(señal)
                    
                    time.sleep(2)  # Pequeña pausa entre pares
                
                # Esperar 1 minuto entre ciclos completos
                time.sleep(60)
                
            except Exception as e:
                print(f"❌ Error en ciclo de monitoreo: {e}")
                time.sleep(30)
    
    def detener_monitoreo(self):
        """Detener monitoreo"""
        self.monitoreando = False
        print("🛑 MONITOREO DETENIDO")

# Instancia global
monitor = MonitorMercado()
