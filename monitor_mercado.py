# monitor_mercado.py - Monitoreo optimizado con Yahoo Finance
import time
import threading
from datetime import datetime, timedelta
from config import TOP_5_PARES, RISK_MANAGEMENT
from yahoo_api import YahooFinanceAPI
from estrategia_dca import EstrategiaDCA
from gestor_operaciones import GestorOperaciones
from telegram_bot import TelegramBotReal

class MonitorMercado:
    def __init__(self):
        self.yahoo = YahooFinanceAPI()
        self.estrategia = EstrategiaDCA()
        self.gestor = GestorOperaciones()
        self.telegram = TelegramBotReal()
        self.monitoreando = False
        self.ultima_señal_por_par = {}
        
        # GESTIÓN DE RIESGO MEJORADA
        self.max_drawdown = RISK_MANAGEMENT['max_drawdown']
        self.consecutive_loss_limit = RISK_MANAGEMENT['consecutive_loss_limit']
        self.capital_inicial = RISK_MANAGEMENT['capital_inicial']
        self.capital_actual = self.capital_inicial
        self.consecutive_losses = 0
        self.total_operaciones = 0
        self.operaciones_ganadoras = 0
        
    def verificar_riesgo_global(self):
        """Verificar condiciones de riesgo global"""
        if self.capital_actual < self.capital_inicial * (1 - self.max_drawdown):
            mensaje = f"⛔ STOP-LOSS GLOBAL ACTIVADO\nCapital actual: ${self.capital_actual:.2f} (Límite: ${self.capital_inicial * (1 - self.max_drawdown):.2f})"
            self.telegram.enviar_mensaje(mensaje)
            print(f"⛔ STOP-LOSS GLOBAL: Capital ${self.capital_actual:.2f}")
            return False
            
        if self.consecutive_losses >= self.consecutive_loss_limit:
            mensaje = f"⏸️ PAUSA POR PÉRDIDAS CONSECUTIVAS\n{self.consecutive_losses} pérdidas seguidas (Límite: {self.consecutive_loss_limit})"
            self.telegram.enviar_mensaje(mensaje)
            print(f"⏸️ PAUSA: {self.consecutive_losses} pérdidas consecutivas")
            return False
            
        return True
    
    def actualizar_estado_riesgo(self, profit):
        """Actualizar estado de riesgo después de cada operación"""
        self.capital_actual += profit
        self.total_operaciones += 1
        
        if profit > 0:
            self.operaciones_ganadoras += 1
            self.consecutive_losses = 0  # Resetear contador
        else:
            self.consecutive_losses += 1
        
        # Calcular estadísticas
        win_rate = (self.operaciones_ganadoras / self.total_operaciones * 100) if self.total_operaciones > 0 else 0
        print(f"📊 Estadísticas: Ops: {self.total_operaciones}, Win Rate: {win_rate:.1f}%, Capital: ${self.capital_actual:.2f}, Pérdidas consecutivas: {self.consecutive_losses}")
    
    def analizar_par(self, par):
        """Analizar un par en busca de oportunidades REALES"""
        try:
            # Verificar riesgo global antes de analizar
            if not self.verificar_riesgo_global():
                return None
            
            # Obtener datos en tiempo real
            datos_reales = self.yahoo.obtener_datos_tecnicos(par)
            
            if not datos_reales:
                print(f"📡 No se pudieron obtener datos para {par}")
                return None
            
            print(f"🔍 Analizando {par}: RSI={datos_reales['rsi']}, Tendencia={datos_reales['tendencia']}, Volatilidad={datos_reales.get('volatilidad', 0):.2f}")
            
            # GENERAR SEÑAL CON ESTRATEGIA OPTIMIZADA
            señal = self.estrategia.generar_señal_real(par)
            
            if señal:
                # Evitar señales repetidas (mínimo 2 horas entre señales del mismo par)
                ultima_señal = self.ultima_señal_por_par.get(par)
                if ultima_señal and (datetime.now() - ultima_señal).seconds < 7200:
                    print(f"⏰ Señal de {par} ignorada (muy reciente)")
                    return None
                
                self.ultima_señal_por_par[par] = datetime.now()
                print(f"🎯 SEÑAL CONFIRMADA en {par}! Confianza: {señal.get('confianza', 'ALTA')}")
                return señal
                
            return None
            
        except Exception as e:
            print(f"❌ Error analizando {par}: {e}")
            return None
    
    def ejecutar_señal(self, señal):
        """Ejecutar una señal detectada"""
        try:
            # Verificar riesgo una última vez antes de ejecutar
            if not self.verificar_riesgo_global():
                print("⛔ Operación cancelada por gestión de riesgo")
                return
            
            # Abrir operación
            operacion_id = self.gestor.abrir_operacion(señal)
            
            # Enviar a Telegram con info de riesgo
            mensaje_extra = f"\n📊 <b>Estado Riesgo:</b>\n• Capital: ${self.capital_actual:.2f}\n• Pérdidas consecutivas: {self.consecutive_losses}"
            self.telegram.enviar_señal_completa(señal, mensaje_extra)
            
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
                        # Operación CERRADA - actualizar gestión de riesgo
                        profit = resultado['operacion']['profit']
                        self.actualizar_estado_riesgo(profit)
                        
                        # Enviar notificación con info de riesgo
                        self.telegram.enviar_cierre_operacion(resultado['operacion'], self.consecutive_losses, self.capital_actual)
                        print(f"📊 OPERACIÓN CERRADA: {operacion_id} - {resultado['resultado']} - Profit: {profit:.2f}")
                        break
                except Exception as e:
                    print(f"❌ Error en seguimiento {operacion_id}: {e}")
                    
                intentos += 1
            
            if intentos >= max_intentos:
                print(f"⏰ Seguimiento timeout para {operacion_id}")
        
        threading.Thread(target=seguir, daemon=True).start()
    
    def reiniciar_riesgo(self):
        """Reiniciar contadores de riesgo (para testing)"""
        self.consecutive_losses = 0
        self.capital_actual = self.capital_inicial
        self.total_operaciones = 0
        self.operaciones_ganadoras = 0
        print("🔄 Contadores de riesgo reiniciados")
    
    def obtener_estadisticas_riesgo(self):
        """Obtener estadísticas actuales de riesgo"""
        win_rate = (self.operaciones_ganadoras / self.total_operaciones * 100) if self.total_operaciones > 0 else 0
        return {
            'capital_actual': self.capital_actual,
            'capital_inicial': self.capital_inicial,
            'drawdown_actual': ((self.capital_inicial - self.capital_actual) / self.capital_inicial * 100),
            'total_operaciones': self.total_operaciones,
            'operaciones_ganadoras': self.operaciones_ganadoras,
            'win_rate': win_rate,
            'perdidas_consecutivas': self.consecutive_losses,
            'limite_perdidas_consecutivas': self.consecutive_loss_limit,
            'limite_drawdown': self.max_drawdown * 100
        }
    
    def iniciar_monitoreo(self):
        """Iniciar monitoreo continuo"""
        self.monitoreando = True
        print("🔍 INICIANDO MONITOREO EN TIEMPO REAL...")
        print(f"📊 Pares monitoreados: {TOP_5_PARES}")
        print(f"💰 Capital inicial: ${self.capital_inicial}")
        print(f"⛔ Stop-loss global: {self.max_drawdown*100}% (${self.capital_inicial * (1 - self.max_drawdown):.2f})")
        print(f"📉 Máx pérdidas consecutivas: {self.consecutive_loss_limit}")
        print("🎯 Estrategia: S/R Etapa 1 Optimizada")
        
        # Enviar mensaje de inicio a Telegram
        mensaje_inicio = f"🤖 <b>BOT OPTIMIZADO INICIADO</b>\n\n📊 <b>Configuración S/R Etapa 1:</b>\n• Pares: {', '.join(TOP_5_PARES)}\n• Capital: ${self.capital_inicial}\n• Stop-loss: {self.max_drawdown*100}%\n• Máx pérdidas: {self.consecutive_loss_limit}\n• Estrategia: S/R Optimizada"
        self.telegram.enviar_mensaje(mensaje_inicio)
        
        ciclo = 0
        while self.monitoreando:
            try:
                ciclo += 1
                print(f"🔄 Ciclo de monitoreo #{ciclo} - {datetime.now().strftime('%H:%M:%S')} - Capital: ${self.capital_actual:.2f}")
                
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
        
        # Enviar mensaje de resumen
        stats = self.obtener_estadisticas_riesgo()
        mensaje_resumen = f"🛑 <b>BOT DETENIDO</b>\n\n📊 <b>Resumen S/R Etapa 1:</b>\n• Capital final: ${stats['capital_actual']:.2f}\n• Operaciones: {stats['total_operaciones']}\n• Win Rate: {stats['win_rate']:.1f}%\n• Drawdown: {stats['drawdown_actual']:.1f}%"
        self.telegram.enviar_mensaje(mensaje_resumen)
        
        print("🛑 MONITOREO DETENIDO")

# Instancia global - ESTO ES IMPORTANTE PARA LA IMPORTACIÓN
monitor = MonitorMercado()
