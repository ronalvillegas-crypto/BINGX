# monitor_mercado.py - Monitoreo en tiempo real (MEJORADO)
import time
import threading
from datetime import datetime, timedelta
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
        self.ultima_señal_por_par = {}
        
    def analizar_par(self, par):
        """Analizar un par en busca de oportunidades REALES"""
        try:
            # Obtener datos en tiempo real
            datos_reales = self.bingx.obtener_datos_tecnicos(par)
            
            if not datos_reales:
                print(f"📡 No se pudieron obtener datos para {par}")
                return None
            
            print(f"🔍 Analizando {par}: RSI={datos_reales['rsi']}, Tendencia={datos_reales['tendencia']}")
            
            # CONDICIONES PARA SEÑAL REAL (personaliza según tu estrategia)
            condiciones_compra = (
                datos_reales['rsi'] < 35 and      # Sobrevendido
                datos_reales['tendencia'] == 'ALCISTA' and  # Tendencia alcista
                datos_reales['volatilidad'] > 0.3  # Suficiente movimiento
            )
            
            condiciones_venta = (
                datos_reales['rsi'] > 65 and      # Sobrecomprado  
                datos_reales['tendencia'] == 'BAJISTA' and  # Tendencia bajista
                datos_reales['volatilidad'] > 0.3  # Suficiente movimiento
            )
            
            # Verificar si hay oportunidad
            if condiciones_compra or condiciones_venta:
                # Evitar señales repetidas (mínimo 2 horas entre señales del mismo par)
                ultima_señal = self.ultima_señal_por_par.get(par)
                if ultima_señal and (datetime.now() - ultima_señal).seconds < 7200:
                    print(f"⏰ Señal de {par} ignorada (muy reciente)")
                    return None
                
                # GENERAR SEÑAL REAL
                señal = self.estrategia.generar_señal_real(par)
                self.ultima_señal_por_par[par] = datetime.now()
                
                print(f"🎯 OPORTUNIDAD DETECTADA en {par}!")
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
            
            print(f"✅ SEÑAL EJECUTADA: {señal['par']} {señal['direccion']} - ID: {operacion_id}")
            
        except Exception as e:
            print(f"❌ Error ejecutando señal: {e}")
    
    def iniciar_seguimiento(self, operacion_id):
        """Seguir operación hasta cierre"""
        def seguir():
            intentos = 0
            max_intentos = 30  # Máximo 15 minutos (30 × 30 segundos)
            
            while intentos < max_intentos and self.monitoreando:
                time.sleep(30)  # Verificar cada 30 segundos
                
                try:
                    resultado = self.gestor.simular_seguimiento(operacion_id)
                    
                    if resultado and resultado['resultado']:
                        # Operación CERRADA - enviar notificación
                        self.telegram.enviar_cierre_operacion(resultado['operacion'])
                        print(f"📊 OPERACIÓN CERRADA: {operacion_id} - {resultado['resultado']}")
                        break
                except Exception as e:
                    print(f"❌ Error en seguimiento {operacion_id}: {e}")
                    
                intentos += 1
            
            if intentos >= max_intentos:
                print(f"⏰ Seguimiento timeout para {operacion_id}")
        
        threading.Thread(target=seguir, daemon=True).start()
    
    def iniciar_monitoreo(self):
        """Iniciar monitoreo continuo"""
        self.monitoreando = True
        print("🔍 INICIANDO MONITOREO EN TIEMPO REAL...")
        print(f"📊 Pares monitoreados: {TOP_5_PARES}")
        
        ciclo = 0
        while self.monitoreando:
            try:
                ciclo += 1
                print(f"🔄 Ciclo de monitoreo #{ciclo} - {datetime.now().strftime('%H:%M:%S')}")
                
                señales_generadas = 0
                for par in TOP_5_PARES:
                    if not self.monitoreando:
                        break
                        
                    # Analizar cada par
                    señal = self.analizar_par(par)
                    
                    if señal:
                        self.ejecutar_señal(señal)
                        señales_generadas += 1
                    
                    time.sleep(3)  # Pequeña pausa entre pares
                
                if señales_generadas == 0:
                    print("📊 No se detectaron oportunidades en este ciclo")
                
                # Esperar 2 minutos entre ciclos completos
                print("⏳ Esperando 2 minutos para próximo ciclo...")
                for i in range(120):  # 120 segundos = 2 minutos
                    if not self.monitoreando:
                        break
                    time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error en ciclo de monitoreo: {e}")
                time.sleep(30)  # Esperar 30 segundos antes de reintentar
    
    def detener_monitoreo(self):
        """Detener monitoreo"""
        self.monitoreando = False
        print("🛑 MONITOREO DETENIDO")

# Instancia global
monitor = MonitorMercado()
