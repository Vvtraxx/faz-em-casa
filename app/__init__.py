"""
Inicializador do módulo app
"""
from flask import Flask, request, jsonify
from app.config import Config

def create_app(config_class=Config):
    """
    Factory function para criar a aplicação Flask
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configurar CORS manualmente
    @app.after_request
    def after_request(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    # Handler para preflight OPTIONS
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = jsonify({'status': 'ok'})
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            return response
    
    # Registrar blueprints
    from app.blueprints.main import main_bp
    from app.blueprints.auth import auth_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Handlers de erro globais
    @app.errorhandler(400)
    def bad_request(error):
        return {
            'success': False,
            'message': 'Requisição inválida',
            'error_code': 400
        }, 400

    @app.errorhandler(401)
    def unauthorized(error):
        return {
            'success': False,
            'message': 'Não autorizado',
            'error_code': 401
        }, 401

    @app.errorhandler(403)
    def forbidden(error):
        return {
            'success': False,
            'message': 'Acesso negado',
            'error_code': 403
        }, 403

    @app.errorhandler(404)
    def not_found(error):
        return {
            'success': False,
            'message': 'Recurso não encontrado',
            'error_code': 404
        }, 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return {
            'success': False,
            'message': 'Método não permitido',
            'error_code': 405
        }, 405

    @app.errorhandler(500)
    def internal_error(error):
        return {
            'success': False,
            'message': 'Erro interno do servidor',
            'error_code': 500
        }, 500

    # Adicionar headers de segurança
    @app.after_request
    def after_request(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    return app
