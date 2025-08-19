import logging
from datetime import datetime
from flask import request, current_app
from typing import Dict, Any

class SecurityLogger:
    """Logger especializado para eventos de segurança"""
    
    def __init__(self):
        self.logger = logging.getLogger('security')
        self.logger.setLevel(logging.WARNING)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '[%(asctime)s] SECURITY %(levelname)s: %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_sql_injection_attempt(self, campo: str, valor: str, ip: str = None):
        """Log tentativa de SQL Injection"""
        ip = ip or self._get_client_ip()
        self.logger.critical(
            f"SQL_INJECTION_ATTEMPT - Campo: {campo}, Valor: {valor[:100]}, IP: {ip}"
        )
    
    def log_suspicious_login(self, email_telefone: str, reason: str, ip: str = None):
        """Log tentativa de login suspeita"""
        ip = ip or self._get_client_ip()
        self.logger.warning(
            f"SUSPICIOUS_LOGIN - Email/RA: {email_telefone}, Motivo: {reason}, IP: {ip}"
        )
    
    def log_invalid_data(self, endpoint: str, data: Dict[str, Any], ip: str = None):
        """Log dados inválidos recebidos"""
        ip = ip or self._get_client_ip()
        self.logger.warning(
            f"INVALID_DATA - Endpoint: {endpoint}, Data: {str(data)[:200]}, IP: {ip}"
        )
    
    def _get_client_ip(self) -> str:
        """Obtém IP do cliente"""
        try:
            # Verifica headers de proxy
            if request.headers.get('X-Forwarded-For'):
                return request.headers.get('X-Forwarded-For').split(',')[0].strip()
            elif request.headers.get('X-Real-IP'):
                return request.headers.get('X-Real-IP')
            else:
                return request.remote_addr or 'unknown'
        except:
            return 'unknown'

# Instância global
security_logger = SecurityLogger()