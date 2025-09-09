from flask import Blueprint, request, jsonify, current_app
import hashlib
from app.utils.auth import gerar_token_jwt, verificar_token_jwt, adicionar_token_blacklist, token_required, obter_token_do_header
from app.utils.validators import validar_dados_login_seguro, validar_email_telefone_seguro, sanitizar_entrada
from app.services.api_externa import api_externa_service

# Cria o blueprint de autenticação
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def criar_hash_senha(senha: str) -> str:
    """
    Cria um hash SHA256 da senha de forma segura
    """
    if not isinstance(senha, str):
        raise ValueError("Senha deve ser uma string")
    
    try:
        # Sanitiza antes de fazer hash
        senha_limpa = sanitizar_entrada(senha)
        return hashlib.sha256(senha_limpa.encode('utf-8')).hexdigest()
    except ValueError as e:
        raise ValueError(f"Senha contém caracteres não permitidos: {str(e)}")

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Rota de login que consome API externa do Oracle APEX
    Com proteções contra SQL Injection
    """
    try:
        email_telefone = request.json.get('email_telefone')
        senha = request.json.get('senha')
        if not email_telefone or not senha:
            return jsonify({
                'success': False,
                'message': 'Email/RA e senha são obrigatórios'
            }), 400
        senha_hash = criar_hash_senha(senha)
        print (senha_hash)
        sucesso, resposta = api_externa_service.autenticar_usuario(email_telefone, senha_hash)
        if not sucesso:
            mensagem = resposta.get('erro') or resposta.get('mensagem') or resposta.get('message') or 'Erro na autenticação'
            return jsonify({
                'success': False,
                'message': mensagem
            }), 401
        token = gerar_token_jwt(resposta)
        return jsonify({
            'success': True,
            'message': 'Login realizado com sucesso',
            'token': token,
            'usuario': resposta,
            'expires_in': int(current_app.config['JWT_EXPIRATION_DELTA'].total_seconds())
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Erro no login: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """
    Rota para logout (adiciona token à blacklist)
    """
    try:
        token = obter_token_do_header()
        
        if token:
            # Adiciona o token à blacklist
            adicionar_token_blacklist(token)
            
            return jsonify({
                'success': True,
                'message': 'Logout realizado com sucesso'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Token não encontrado'
            }), 400
    
    except Exception as e:
        current_app.logger.error(f"Erro no logout: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500

@auth_bp.route('/verify-token', methods=['POST'])
@token_required
def verify_token():
    """
    Rota para verificar se um token é válido
    """
    try:
        # Obtém informações do usuário atual do token (já validado pelo decorator)
        usuario_atual = request.current_user
        
        return jsonify({
            'success': True,
            'message': 'Token válido',
            'valid': True,
            'usuario': usuario_atual
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Erro na verificação de token: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500

@auth_bp.route('/refresh', methods=['POST'])
@token_required
def refresh_token():
    """
    Rota para renovar um token válido
    """
    try:
        # Obtém informações do usuário atual do token
        usuario_atual = request.current_user
        
        # Adiciona o token atual à blacklist
        token_atual = obter_token_do_header()
        if token_atual:
            adicionar_token_blacklist(token_atual)
        
        # Gera novo token usando as informações do token atual
        # Como os dados vêm da API externa, mantemos as informações do token
        usuario_info = {
           'usuario': usuario_atual
        }
        
        novo_token = gerar_token_jwt(usuario_info)
        
        current_app.logger.info(f"Token renovado para: {usuario_atual}")
        
        return jsonify({
            'success': True,
            'message': 'Token renovado com sucesso',
            'token': novo_token,
            'expires_in': int(current_app.config['JWT_EXPIRATION_DELTA'].total_seconds())
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Erro na renovação de token: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():


    try:
        email_telefone = request.json.get('email_telefone')
        nova_senha = request.json.get('senha')
        print(email_telefone, nova_senha)
        
        if not email_telefone or not nova_senha:
            return jsonify({
                'success': False,
                'message': 'Email e nova senha são obrigatórios'
            }), 400
        
        # Cria hash da nova senha
        nova_senha_hash = hashlib.sha256(nova_senha.encode()).hexdigest()
        
        # Chama a API externa
        sucesso, mensagem = api_externa_service.resetar_senha(email_telefone, nova_senha_hash)
        
        status_code = 200 if sucesso else 400
        return jsonify({
            'success': sucesso,
            'message': mensagem
        }), status_code
    
    except Exception as e:
        current_app.logger.error(f"Erro no reset de senha: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500
