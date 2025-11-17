# telegram_bot.py - Comunicaciones REALES CON GESTIÓN DE RIESGO
import requests
import logging
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
        """Enviar señal COMPLETA con todos los detalles"""
        emoji = "🟢" if señal['direccion'] == "COMPRA" else "🔴"
        confianza_emoji = "🎯" if señal.get('confianza') == 'ALTA' else "⚡" if señal.get('confianza') == 'MEDIA' else "⚠️"
        
        mensaje = f"""
{emoji} <b>SEÑAL DCA CONFIRMADA</b> {emoji}

🏆 <b>Par:</b> {señal['par']}
🎯 <b>Dirección:</b> {señal['direccion']}
💰 <b>Precio:</b> {señal['precio_actual']:.5f}
{confianza_emoji} <b>Confianza:</b> {señal.get('confianza', 'ALTA')}

📊 <b>Análisis:</b>
• RSI: {señal['rsi']}
• Tendencia: {señal['tendencia']}
• Fuente: {señal['fuente_datos']}

⚡ <b>Estrategia DCA:</b>
• Entrada: {señal['precio_actual']:.5f}
• DCA 1: {señal['dca_1']:.5f}
• DCA 2: {señal['dca_2']:.5f}
• TP1: {señal['tp1']:.5f}
• TP2: {señal['tp2']:.5f}
• SL: {señal['sl']:.5f}

🎯 <b>Backtesting:</b>
• WR Esperado: {señal['winrate_esperado']}%
• Profit Esperado: {señal['rentabilidad_esperada']}%
• Leverage: {señal['leverage']}x

{mensaje_extra}

⏰ <b>Hora:</b> {señal['timestamp']}
        """
        
        return self.enviar_mensaje(mensaje.strip())
    
    def enviar_cierre_operacion(self, operacion, consecutive_losses=0, capital_actual=1000):
        """Enviar cierre REAL de operación con gestión de riesgo"""
        emoji = "🏆" if operacion['profit'] > 0 else "🛑"
        
        mensaje = f"""
{emoji} <b>OPERACIÓN CERRADA</b> {emoji}

📈 <b>Par:</b> {operacion['par']}
🎯 <b>Resultado:</b> {operacion['resultado']}
💰 <b>Profit:</b> {operacion['profit']:+.2f}%

📊 <b>Resumen:</b>
• Entrada: {operacion['precio_entrada']:.5f}
• Cierre: {operacion['precio_cierre']:.5f}
• DCA Usados: {operacion['niveles_dca_activados']}/2
• Precio Promedio: {operacion['precio_promedio']:.5f}

📉 <b>Estado Riesgo:</b>
• Pérdidas Consecutivas: {consecutive_losses}
• Capital Actual: ${capital_actual:.2f}

⏰ <b>Duración:</b> {operacion['timestamp_cierre'].strftime('%H:%M:%S')}
        """
        
        return self.enviar_mensaje(mensaje.strip())
