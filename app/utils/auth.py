"""
Módulo de autenticação JWT - Versão sem bcrypt
Atualizado: 2025-07-14 para remover dependência do bcrypt
"""
import jwt
from datetime import datetime
from flask import current_app, request, jsonify
from functools import wraps

# Blacklist para tokens revogados (em produção, use Redis ou banco de dados)
token_blacklist = set()

def gerar_token_jwt(usuario_info):
    """Gera um token JWT para o usuário"""
    payload = {
        'usuario_info': usuario_info,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + current_app.config['JWT_EXPIRATION_DELTA']
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def verificar_token_jwt(token):
    """Verifica se o token JWT é válido"""
    try:
        # Verifica se o token está na blacklist
        if token in token_blacklist:
            return None, "Token foi revogado"
        
        # Decodifica o token
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, "Token expirado"
    except jwt.InvalidTokenError:
        return None, "Token inválido"

def adicionar_token_blacklist(token):
    """Adiciona um token à blacklist"""
    token_blacklist.add(token)

def obter_token_do_header():
    """Extrai o token do header Authorization"""
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header.split(" ")[1]
    return None

def token_required(f):
    """Decorator para rotas que requerem autenticação"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Verifica se o token está no header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({
                    'success': False,
                    'message': 'Formato do token inválido'
                }), 401
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Token de acesso é obrigatório'
            }), 401
        
        payload, erro = verificar_token_jwt(token)
        if erro:
            return jsonify({
                'success': False,
                'message': erro
            }), 401
        
        # Adiciona as informações do usuário ao request
        request.current_user = payload
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator para rotas que requerem permissão de admin"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin' not in request.current_user.get('permissoes', []):
            return jsonify({
                'success': False,
                'message': 'Acesso negado: permissão de administrador necessária'
            }), 403
        return f(*args, **kwargs)
    
    return decorated


