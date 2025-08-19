"""
Blueprint dedicado para Swagger
"""
from flask import Blueprint, jsonify

swagger_bp = Blueprint('swagger', __name__)

@swagger_bp.route('/doc')
@swagger_bp.route('/doc/')
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

@swagger_bp.route('/swagger.json')
def swagger_json():
    """Especificação OpenAPI em JSON"""
    return jsonify({
        "openapi": "3.0.0",
        "info": {
            "title": "API Flask Uninga",
            "version": "1.0.0",
            "description": "Gateway de Autenticação para Oracle APEX"
        },
        "paths": {
            "/": {
                "get": {
                    "summary": "Informações da API",
                    "responses": {
                        "200": {
                            "description": "Sucesso"
                        }
                    }
                }
            }
        }
    })

@swagger_bp.route('/test-swagger')
def test_swagger():
    """Rota de teste para verificar se o blueprint funciona"""
    return jsonify({
        "message": "Blueprint Swagger funcionando!",
        "status": "ok",
        "routes": ["/doc/", "/swagger.json", "/test-swagger"]
    })

@swagger_bp.route('/swagger.json')
def swagger_json():
    """Especificação OpenAPI em JSON"""
    swagger_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "API Flask Uninga - Gateway Oracle APEX",
            "version": "1.0.0",
            "description": "Gateway de Autenticação para Oracle APEX da Uninga"
        },
        "servers": [
            {
                "url": "http://localhost:5000",
                "description": "Servidor de desenvolvimento"
            }
        ],
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            },
            "schemas": {
                "LoginRequest": {
                    "type": "object",
                    "required": ["email_telefone", "senha"],
                    "properties": {
                        "email_telefone": {
                            "type": "string",
                            "description": "Email ou RA do usuário",
                            "example": "prof.viniciuszulianelli@uninga.edu.br"
                        },
                        "senha": {
                            "type": "string",
                            "description": "Senha do usuário",
                            "example": "1234"
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
                                        "identificador": {"type": "string"},
                                        "nome": {"type": "string"},
                                        "email": {"type": "string"},
                                        "tipo": {"type": "string"},
                                        "tipo_usuario": {"type": "string"},
                                        "permissoes": {"type": "array", "items": {"type": "string"}}
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
            "/": {
                "get": {
                    "tags": ["Sistema"],
                    "summary": "Informações da API",
                    "description": "Retorna informações gerais sobre a API",
                    "responses": {
                        "200": {
                            "description": "Informações da API",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "version": {"type": "string"},
                                            "description": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/health": {
                "get": {
                    "tags": ["Sistema"],
                    "summary": "Health Check",
                    "description": "Verifica o status da API",
                    "responses": {
                        "200": {
                            "description": "Status da API",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "timestamp": {"type": "string"},
                                            "version": {"type": "string"}
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
                    "description": "Autentica um usuário usando email/RA e senha",
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
                    "description": "Invalida o token JWT atual",
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
            "/user/profile": {
                "get": {
                    "tags": ["Usuário"],
                    "summary": "Perfil do usuário",
                    "description": "Retorna informações do perfil do usuário autenticado",
                    "security": [{"BearerAuth": []}],
                    "responses": {
                        "200": {
                            "description": "Perfil retornado com sucesso",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {"type": "boolean"},
                                            "data": {
                                                "type": "object",
                                                "properties": {
                                                    "identificador": {"type": "string"},
                                                    "nome": {"type": "string"},
                                                    "email": {"type": "string"},
                                                    "tipo_usuario": {"type": "string"},
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
            }
        }
    }
    
    return swagger_spec
