# telegram_bot.py - Comunicaciones REALES CON ESTRATEGIA S/R
import requests
import logging
from datetime import datetime
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)

class TelegramBotReal:
    def __init__(self):
        self.token = TELEGRAM_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
    
    def enviar_mensaje(self, mensaje, parse_mode='HTML'):
        """Enviar mensaje REAL a Telegram"""
        try:
            if not self.token or not self.chat_id:
                return False
                
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': mensaje,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error Telegram: {e}")
            return False
    
    def enviar_señal_completa(self, señal, mensaje_extra=""):
        """Enviar señal COMPLETA con análisis S/R"""
        emoji = "🟢" if señal['direccion'] == "COMPRA" else "🔴"
        confianza_emoji = "🎯" if señal.get('confianza') == 'ALTA' else "⚡" if señal.get('confianza') == 'MEDIA' else "⚠️"
        
        # FORMATO MEJORADO PARA NIVELES S/R
        niveles_support = [round(s, 5) for s in señal.get('niveles_sr', {}).get('support', [])]
        niveles_resistance = [round(r, 5) for r in señal.get('niveles_sr', {}).get('resistance', [])]
        
        # TIMESTAMP MEJORADO
        timestamp_obj = datetime.strptime(señal['timestamp'], "%Y-%m-%d %H:%M:%S")
        timestamp_formateado = timestamp_obj.strftime("%d/%m/%Y %H:%M:%S")
        
        # SECCIÓN S/R MEJORADA
        info_sr = f"""
🎯 <b>ANÁLISIS S/R ETAPA 1:</b>
• Estrategia: {señal.get('estrategia', 'S/R Etapa 1')}
• Zona Actual: <b>{señal.get('zona_actual', 'N/A')}</b>
• Confianza: {confianza_emoji} {señal.get('confianza', 'ALTA')}

📊 <b>Niveles Clave:</b>
• Support: {niveles_support}
• Resistance: {niveles_resistance}
• Precio Actual: {señal['precio_actual']:.5f}

💡 <b>Motivo Señal:</b>
{señal.get('motivo_señal', 'Análisis técnico S/R')}
"""
        
        mensaje = f"""
{emoji} <b>🚀 SEÑAL S/R ETAPA 1 CONFIRMADA</b> {emoji}

🏆 <b>PAR:</b> {señal['par']}
🎯 <b>DIRECCIÓN:</b> <b>{señal['direccion']}</b>
💰 <b>PRECIO ENTRADA:</b> {señal['precio_actual']:.5f}

{info_sr}

📈 <b>ANÁLISIS TÉCNICO:</b>
• RSI: {señal['rsi']}
• Tendencia: {señal['tendencia']}
• Fuente Datos: {señal['fuente_datos']}

⚡ <b>ESTRATEGIA DCA OPTIMIZADA:</b>
• Entrada Principal: {señal['precio_actual']:.5f}
• DCA Nivel 1: {señal['dca_1']:.5f}
• DCA Nivel 2: {señal['dca_2']:.5f}
• Take Profit 1: {señal['tp1']:.5f}
• Take Profit 2: {señal['tp2']:.5f}
• Stop Loss: {señal['sl']:.5f}

🎯 <b>BACKTESTING S/R ETAPA 1:</b>
• Win Rate Esperado: {señal['winrate_esperado']}%
• Rentabilidad Esperada: {señal['rentabilidad_esperada']}%
• Leverage: {señal['leverage']}x

{mensaje_extra}

⏰ <b>HORA SEÑAL:</b> {timestamp_formateado}
        """
        
        return self.enviar_mensaje(mensaje.strip())
    
    def enviar_cierre_operacion(self, operacion, consecutive_losses=0, capital_actual=1000):
        """Enviar cierre REAL de operación con gestión de riesgo - CORREGIDO"""
        emoji = "🏆" if operacion['profit'] > 0 else "🛑"
        resultado_emoji = "✅" if operacion['profit'] > 0 else "❌"
        
        # CALCULAR DURACIÓN REAL - CORREGIDO
        if operacion['timestamp_cierre'] and operacion['timestamp_apertura']:
            duracion = operacion['timestamp_cierre'] - operacion['timestamp_apertura']
            horas = duracion.seconds // 3600
            minutos = (duracion.seconds % 3600) // 60
            segundos = duracion.seconds % 60
            duracion_str = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
        else:
            duracion_str = "N/A"
        
        mensaje = f"""
{emoji} <b>OPERACIÓN S/R CERRADA</b> {emoji}

📈 <b>Par:</b> {operacion['par']}
🎯 <b>Resultado:</b> {resultado_emoji} {operacion['resultado']}
💰 <b>Profit:</b> <b>{operacion['profit']:+.2f}%</b>

📊 <b>Resumen Operación:</b>
• Entrada: {operacion['precio_entrada']:.5f}
• Cierre: {operacion['precio_cierre']:.5f}
• DCA Usados: {operacion['niveles_dca_activados']}/2
• Precio Promedio: {operacion['precio_promedio']:.5f}

📉 <b>Estado Riesgo Actual:</b>
• Pérdidas Consecutivas: {consecutive_losses}
• Capital Actual: <b>${capital_actual:.2f}</b>
• Resultado Operación: {"GANADORA" if operacion['profit'] > 0 else "PERDEDORA"}

⏰ <b>Duración Real:</b> {duracion_str}
        """
        
        return self.enviar_mensaje(mensaje.strip())
    
    def enviar_alerta_riesgo(self, tipo_alerta, datos):
        """Enviar alertas de gestión de riesgo"""
        if tipo_alerta == "stop_loss_global":
            mensaje = f"""
🛑 <b>ALERTA STOP-LOSS GLOBAL</b>

⛔ <b>El bot ha sido detenido por stop-loss global</b>

📊 <b>Estadísticas Finales:</b>
• Capital Inicial: ${datos.get('capital_inicial', 1000):.2f}
• Capital Final: ${datos.get('capital_actual', 0):.2f}
• Drawdown: {datos.get('drawdown', 0):.1f}%
• Operaciones Totales: {datos.get('total_operaciones', 0)}
• Win Rate: {datos.get('win_rate', 0):.1f}%

🔒 <b>El bot requiere reinicio manual</b>
            """
        
        elif tipo_alerta == "perdidas_consecutivas":
            mensaje = f"""
⏸️ <b>ALERTA PÉRDIDAS CONSECUTIVAS</b>

📉 <b>Pausa automática activada</b>

📊 <b>Motivo:</b>
• {datos.get('perdidas_actuales', 0)} pérdidas consecutivas
• Límite: {datos.get('limite_perdidas', 5)} pérdidas

💰 <b>Estado Capital:</b>
• Capital Actual: ${datos.get('capital_actual', 0):.2f}
• Drawdown: {datos.get('drawdown', 0):.1f}%

🔄 <b>El bot se reanudará automáticamente</b>
            """
        
        elif tipo_alerta == "reinicio_riesgo":
            mensaje = f"""
🔄 <b>CONTADORES DE RIESGO REINICIADOS</b>

📊 <b>Nuevo inicio detectado:</b>
• Capital: ${datos.get('capital_actual', 1000):.2f}
• Pérdidas Consecutivas: 0
• Drawdown: 0.0%

🎯 <b>Estrategia S/R Etapa 1 activa</b>
• Pares: EURUSD, USDCAD, EURCHF, EURAUD
• Win Rate Esperado: 55-64%
            """
        
        else:
            mensaje = f"""
⚠️ <b>ALERTA DEL SISTEMA</b>

📝 <b>Mensaje:</b> {tipo_alerta}
📊 <b>Datos:</b> {datos}
            """
        
        return self.enviar_mensaje(mensaje.strip())
    
    def enviar_estadisticas_diarias(self, estadisticas):
        """Enviar resumen diario de operaciones"""
        mensaje = f"""
📊 <b>RESUMEN DIARIO - ESTRATEGIA S/R</b>

📈 <b>Estadísticas del Día:</b>
• Operaciones Totales: {estadisticas.get('total_operaciones', 0)}
• Operaciones Ganadoras: {estadisticas.get('operaciones_ganadoras', 0)}
• Operaciones Perdedoras: {estadisticas.get('operaciones_perdedoras', 0)}
• Win Rate: {estadisticas.get('win_rate', 0):.1f}%

💰 <b>Resultados Financieros:</b>
• Profit Total: {estadisticas.get('profit_total', 0):+.2f}%
• Capital Inicial: ${estadisticas.get('capital_inicial', 1000):.2f}
• Capital Actual: ${estadisticas.get('capital_actual', 1000):.2f}
• Drawdown: {estadisticas.get('drawdown_actual', 0):.1f}%

🎯 <b>Gestión de Riesgo:</b>
• Pérdidas Consecutivas: {estadisticas.get('perdidas_consecutivas', 0)}
• Operaciones Activas: {estadisticas.get('operaciones_activas', 0)}

⏰ <b>Actualizado:</b> {estadisticas.get('timestamp', 'N/A')}
        """
        
        return self.enviar_mensaje(mensaje.strip())
    
    def enviar_mensaje_inicio_bot(self, config):
        """Enviar mensaje de inicio del bot optimizado"""
        mensaje = f"""
🤖 <b>BOT S/R ETAPA 1 INICIADO</b>

🎯 <b>CONFIGURACIÓN OPTIMIZADA:</b>
• Estrategia: S/R Etapa 1 (Backtesting Comprobado)
• Pares Activos: {', '.join(config.get('pares', []))}
• Capital Inicial: ${config.get('capital_inicial', 1000):.2f}
• Stop-loss Global: {config.get('max_drawdown', 50)}%
• Máx Pérdidas Consecutivas: {config.get('consecutive_loss_limit', 5)}

📊 <b>EXPECTATIVAS BACKTESTING:</b>
• Win Rate: 55-64%
• Profit Factor: 1.45
• Retorno Esperado: 104-210%

⚡ <b>MÓDULOS ACTIVOS:</b>
• Monitor Mercado en Tiempo Real
• Estrategia S/R Etapa 1
• Gestión de Riesgo Avanzada
• Notificaciones Telegram

🔍 <b>El bot está monitoreando mercados...</b>
        """
        
        return self.enviar_mensaje(mensaje.strip())
