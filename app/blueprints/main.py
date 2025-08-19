from flask import Blueprint, jsonify, redirect, request

# Cria o blueprint principal
main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def index():
    """Redireciona para a documentação da API"""
    return redirect('/doc')

@main_bp.route('/login', methods=['GET', 'POST'])
def login_redirect():
    """Redireciona para a rota de login correta"""
    return redirect('/auth/login')

@main_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint de verificação de saúde da API"""
    return jsonify({
        'success': True,
        'message': 'API está funcionando',
        'service': 'API Flask Uninga - Gateway Oracle APEX',
        'version': '1.0.0'
    }), 200


@main_bp.route('/doc', methods=['GET'])
@main_bp.route('/doc/', methods=['GET'])
def swagger_ui():
    """Interface do Swagger UI"""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>API Flask Uninga - Swagger UI</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.25.0/swagger-ui.css" />
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@3.25.0/swagger-ui-bundle.js"></script>
    <script>
        window.onload = function() {
            SwaggerUIBundle({
                url: '/swagger.json',
                dom_id: '#swagger-ui',
                deepLinking: true
            });
        };
    </script>
</body>
</html>
    """

@main_bp.route('/swagger.json', methods=['GET'])
def swagger_json():
    """Especificação OpenAPI em JSON"""
    return jsonify({
        "openapi": "3.0.0",
        "info": {
            "title": "API Flask Uninga - Gateway Oracle APEX",
            "version": "1.0.0",
            "description": "Gateway de Autenticação para Oracle APEX da Uninga",
            "contact": {
                "name": "Equipe Uninga",
                "email": "dev@uninga.edu.br"
            }
        },
        "servers": [
            {
                "url": "/",
                "description": "Servidor atual (relativo)"
            },
            {
                "url": "http://localhost:5000",
                "description": "Servidor de desenvolvimento"
            },
            {
                "url": "https://uninga-backend.vercel.app",
                "description": "Servidor de produção"
            }
        ],
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "JWT Token. Formato: Bearer <token>"
                }
            },
            "schemas": {
                "LoginRequest": {
                    "type": "object",
                    "required": ["email_telefone", "senha"],
                    "properties": {
                        "email_telefone": {
                            "type": "string",
                            "description": "Email ou RA do usuário. Para RA aceita vários formatos: 200378-25, 200378.25, 200378 25, etc. (caracteres não numéricos são removidos automaticamente)",
                            "example": "44984023495"
                        },
                        "senha": {
                            "type": "string",
                            "description": "Senha do usuário",
                            "example": "123456789"
                        }
                    }
                },
                "ResetPasswordRequest": {
                    "type": "object",
                    "required": ["email_telefone", "senha"],
                    "properties": {
                        "email_telefone": {
                            "type": "string",
                            "description": "Email ou RA do usuário. Para RA aceita vários formatos: 200378-25, 200378.25, 200378 25, etc.",
                            "example": "email@uninga.edu.br ou 200378-25"
                        },
                        "senha": {
                            "type": "string",
                            "description": "Nova senha do usuário (será automaticamente criptografada)",
                            "example": "novaSenha123"
                        }
                    }
                },
                "LoginResponse": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean", "example": True},
                        "message": {"type": "string", "example": "Login realizado com sucesso"},
                        "data": {
                            "type": "object",
                            "properties": {
                                "access_token": {"type": "string", "example": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."},
                                "refresh_token": {"type": "string", "example": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."},
                                "expires_in": {"type": "integer", "example": 3600},
                                "token_type": {"type": "string", "example": "Bearer"},
                                "user_info": {
                                    "type": "object",
                                    "properties": {
                                        "identificador": {"type": "string", "example": "teste@uninga.edu.br"},
                                        "nome": {"type": "string", "example": "TESTE USUÁRIO"},
                                        "email": {"type": "string", "example": "teste@uninga.edu.br"},
                                        "tipo": {"type": "string", "example": "email"},
                                        "tipo_usuario": {"type": "string", "example": "PROFESSOR"},
                                        "nivel_acesso": {"type": "string", "example": "1"},
                                        "permissoes": {"type": "array", "items": {"type": "string"}, "example": ["user", "professor"]}
                                    }
                                }
                            }
                        }
                    }
                },
                "ErrorResponse": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean", "example": False},
                        "message": {"type": "string", "example": "Erro na operação"},
                        "error_code": {"type": "integer", "example": 400}
                    }
                }
            }
        },
        "paths": {
            "/health": {
                "get": {
                    "tags": ["Sistema"],
                    "summary": "Verificação de saúde",
                    "description": "Endpoint para verificar se a API está funcionando corretamente",
                    "responses": {
                        "200": {
                            "description": "API funcionando normalmente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {"type": "boolean", "example": True},
                                            "message": {"type": "string", "example": "API está funcionando"},
                                            "service": {"type": "string", "example": "API Flask Uninga - Gateway Oracle APEX"},
                                            "version": {"type": "string", "example": "1.0.0"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/auth/login": {
                "post": {
                    "tags": ["Autenticação"],
                    "summary": "Login do usuário",
                    "description": "Autentica um usuário usando email/RA e senha. Para RAs, aceita vários formatos (200378-25, 200378.25, 200378 25) e caracteres não numéricos são automaticamente removidos. A senha é automaticamente convertida para hash SHA256 antes de ser enviada para a API Oracle APEX",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/LoginRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Login realizado com sucesso",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/LoginResponse"}
                                }
                            }
                        },
                        "401": {
                            "description": "Credenciais inválidas",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            }
                        },
                        "400": {
                            "description": "Dados inválidos",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "/auth/logout": {
                "post": {
                    "tags": ["Autenticação"],
                    "summary": "Logout do usuário",
                    "description": "Invalida o token JWT atual adicionando-o à blacklist",
                    "security": [{"BearerAuth": []}],
                    "responses": {
                        "200": {
                            "description": "Logout realizado com sucesso",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {"type": "boolean"},
                                            "message": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "Token inválido",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "/auth/verify-token": {
                "post": {
                    "tags": ["Autenticação"],
                    "summary": "Verificar token",
                    "description": "Verifica se um token JWT é válido através do header Authorization",
                    "security": [{"BearerAuth": []}],
                    "responses": {
                        "200": {
                            "description": "Token verificado",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {"type": "boolean", "example": True},
                                            "message": {"type": "string", "example": "Token válido"},
                                            "valid": {"type": "boolean", "example": True},
                                            "usuario": {
                                                "type": "object",
                                                "properties": {
                                                    "identificador": {"type": "string"},
                                                    "nome": {"type": "string"},
                                                    "tipo": {"type": "string"},
                                                    "permissoes": {"type": "array", "items": {"type": "string"}}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "Token inválido",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "/auth/refresh": {
                "post": {
                    "tags": ["Autenticação"],
                    "summary": "Renovar token",
                    "description": "Renova um token JWT usando o refresh token",
                    "security": [{"BearerAuth": []}],
                    "responses": {
                        "200": {
                            "description": "Token renovado com sucesso",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/LoginResponse"}
                                }
                            }
                        },
                        "401": {
                            "description": "Refresh token inválido",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "/auth/reset": {
                "post": {
                    "tags": ["Autenticação"],
                    "summary": "Reset de senha",
                    "description": "Altera a senha de um usuário usando email/RA. A nova senha é automaticamente criptografada com SHA256 antes de ser enviada para a API Oracle APEX",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ResetPasswordRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Senha alterada com sucesso",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {"type": "boolean", "example": True},
                                            "message": {"type": "string", "example": "Senha alterada com sucesso"}
                                        }
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Dados inválidos ou erro na alteração",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            }
                        },
                        "500": {
                            "description": "Erro interno do servidor",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }), 200

@main_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Rota não encontrada',
        'error_code': 404
    }), 404

@main_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'message': 'Método não permitido para esta rota',
        'error_code': 405
    }), 405

@main_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': 'Erro interno do servidor',
        'error_code': 500
    }), 500
