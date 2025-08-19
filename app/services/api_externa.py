import requests
import logging
import time
import os
from typing import Tuple, Dict, Any, Optional
from flask import current_app

class ApiExternaService:
    """Serviço para integração com API externa do Oracle APEX"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    @property
    def base_url(self):
        """URL base da API externa configurada no Flask"""
        return getattr(current_app.config, 'API_EXTERNA_BASE_URL', 
                      'https://oracleapex.com/ords/fazemcasa')
    
    @property
    def timeout(self):
        """Timeout configurado no Flask"""
        return getattr(current_app.config, 'API_EXTERNA_TIMEOUT', 60)
    
    @property
    def retries(self):
        """Número de tentativas configurado no Flask"""
        return getattr(current_app.config, 'API_EXTERNA_RETRIES', 3)
    
    def _fazer_requisicao(self, endpoint: str, method: str = 'POST', dados: Dict = None) -> Tuple[bool, Dict]:
        """
        Método genérico para fazer requisições à API externa
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            self.logger.info(f"Fazendo requisição {method} para {url}")
            
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Flask-Uninga-Gateway/1.0'
            }
            
            if method.upper() == 'POST':
                response = requests.post(
                    url, 
                    json=dados, 
                    timeout=self.timeout,
                    headers=headers
                )
            elif method.upper() == 'GET':
                response = requests.get(
                    url, 
                    params=dados, 
                    timeout=self.timeout,
                    headers=headers
                )
            else:
                return False, {"erro": f"Método {method} não suportado"}
            
            self.logger.info(f"Response status: {response.status_code}")
            
            # Verifica se a resposta foi bem-sucedida
            if response.status_code == 200 or response.status_code == 201:
                try:
                    resultado = response.json()
                    return True, resultado
                except ValueError:
                    # Se não conseguir fazer parse do JSON, retorna o texto
                    return True, {"data": response.text}
            else:
                return False, {
                    "erro": f"Erro na API externa",
                    "status_code": response.status_code,
                    "resposta": response.text[:500]  # Limita o tamanho da resposta
                }
                
        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout na requisição para {url}")
            return False, {"erro": "Timeout na comunicação com a API externa"}
        except requests.exceptions.ConnectionError:
            self.logger.error(f"Erro de conexão com {url}")
            return False, {"erro": "Erro de conexão com a API externa"}
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro na requisição: {str(e)}")
            return False, {"erro": f"Erro na requisição: {str(e)}"}
        
        except Exception as e:
            self.logger.error(f"Erro inesperado: {str(e)}")
            return False, {"erro": f"Erro inesperado: {str(e)}"}
    
    
    def autenticar_usuario(self, email_telefone: str, senha: str):
        """
        Autentica um usuário na API externa e retorna o JSON da resposta diretamente.
        """
        dados = {
            "email_telefone": email_telefone,
            "senha": senha
        }
        self.logger.info(f"Enviando dados para API externa: login='{email_telefone}', senha=[HASH:{senha[:10]}...]")
        sucesso, resposta = self._fazer_requisicao("/api/login", "POST", dados)
        print (resposta)
        self.logger.info(f"Resposta da API externa - Sucesso: {sucesso}, Dados: {resposta}")
        return sucesso, resposta
    
    def resetar_senha(self, email_telefone: str, nova_senha_hash: str) -> Tuple[bool, str]:
        """
        Reseta a senha de um usuário na API externa
        
        Args:
            email_telefone: Email ou RA do usuário
            nova_senha_hash: Nova senha já criptografada em SHA256
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        dados = {
            "email_telefone": email_telefone,
            "nova_senha": nova_senha_hash
        }
        
        self.logger.info(f"Enviando reset de senha para API externa: email_telefone='{email_telefone}'")
        
        sucesso, resposta = self._fazer_requisicao("/login/reset_senha", "POST", dados)
        
        if not sucesso:
            erro_msg = resposta.get("erro", "Erro ao resetar senha")
            self.logger.error(f"Falha no reset de senha: {erro_msg}")
            return False, erro_msg
        
        # Processa a resposta da API externa
        if isinstance(resposta, dict):
            self.logger.info(f"Resposta do reset de senha: {resposta}")
            
            # Se retornou NAO_ENCONTRADO, significa que o usuário não existe
            if resposta.get("status") == "NAO_ENCONTRADO":
                return False, "Usuário não encontrado"
            
            # Verifica se o reset foi bem-sucedido
            if (resposta.get("sucesso") or 
                resposta.get("success") or 
                resposta.get("status") == "OK" or
                resposta.get("status") == "SUCESSO" or
                resposta.get("status") == "sucesso"):  # Adicionado para reconhecer 'sucesso' minúsculo
                
                self.logger.info(f"Reset de senha bem-sucedido para {email_telefone}")
                return True, "Senha alterada com sucesso"
            else:
                # Se há uma mensagem de erro específica da API
                mensagem_erro = resposta.get("mensagem", 
                                           resposta.get("message", 
                                                      resposta.get("erro", "Erro ao alterar senha")))
                self.logger.warning(f"Falha no reset de senha - Resposta da API: {resposta}")
                return False, mensagem_erro
        else:
            self.logger.error(f"Formato de resposta inválido da API externa: {type(resposta)} - {resposta}")
            return False, "Erro interno na comunicação com a API externa"


# Instância global do serviço
api_externa_service = ApiExternaService()
