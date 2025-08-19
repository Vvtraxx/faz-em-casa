import re
from typing import Tuple, List, Dict, Any

def validar_email(email: str) -> bool:
    """
    Valida formato de email de forma segura
    """
    if not email or len(email) > 254:  # RFC 5321 limit
        return False
    
    # Regex rigorosa para email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))

def validar_ra_formato(ra: str) -> bool:
    """
    Valida formato de RA de forma muito rigorosa
    Remove caracteres especiais e valida apenas números
    """
    if not ra:
        return False
    
    # Remove APENAS hífens, pontos e espaços permitidos
    ra_limpo = re.sub(r'[-.\s]', '', ra)
    
    # Deve conter APENAS dígitos após limpeza
    if not ra_limpo.isdigit():
        return False
    
    # Deve ter entre 6 e 12 dígitos (ajuste conforme necessário)
    if len(ra_limpo) < 6 or len(ra_limpo) > 12:
        return False
    
    return True

def sanitizar_entrada(valor: str) -> str:
    """
    Sanitiza entrada removendo caracteres perigosos para SQL Injection
    """
    if not isinstance(valor, str):
        return ""
    
    # Remove caracteres perigosos para SQL
    caracteres_perigosos = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_", 
                           "DROP", "DELETE", "INSERT", "UPDATE", "SELECT", 
                           "UNION", "OR", "AND", "EXEC", "EXECUTE", "SCRIPT",
                           "<script", "</script", "javascript:", "vbscript:",
                           "onload=", "onerror=", "onclick="]
    
    valor_limpo = valor.strip()
    
    # Converte para minúsculo para verificação
    valor_lower = valor_limpo.lower()
    
    # Verifica se contém palavras SQL perigosas
    for palavra in caracteres_perigosos:
        if palavra.lower() in valor_lower:
            # Log da tentativa de injeção
            try:
                from app.utils.security_logger import security_logger
                security_logger.log_sql_injection_attempt("entrada", valor)
            except:
                pass  # Se não conseguir logar, continua sem falhar
            
            raise ValueError(f"Entrada contém caracteres ou comandos não permitidos")
    
    # Remove caracteres de controle
    valor_limpo = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', valor_limpo)
    
    return valor_limpo

def validar_email_telefone_seguro(email_telefone: str) -> Tuple[bool, str, str]:
    """
    Valida email ou RA de forma segura contra SQL Injection
    
    Returns:
        Tuple[bool, str, str]: (é_válido, tipo, valor_sanitizado)
    """
    if not email_telefone:
        return False, "", ""
    
    try:
        # Sanitiza primeiro
        email_telefone_limpo = sanitizar_entrada(email_telefone)
        
        # Verifica se é email
        if "@" in email_telefone_limpo:
            if validar_email(email_telefone_limpo):
                return True, "email", email_telefone_limpo
            else:
                return False, "", ""
        
        # Verifica se é RA
        if validar_ra_formato(email_telefone_limpo):
            return True, "ra", email_telefone_limpo
        
        return False, "", ""
        
    except ValueError as e:
        # Se sanitização falhou, é entrada maliciosa
        return False, "", ""

def validar_senha_segura(senha: str) -> Tuple[bool, List[str]]:
    """
    Valida senha de forma segura
    """
    erros = []
    
    if not senha:
        erros.append("Senha é obrigatória")
        return False, erros
    
    try:
        # Sanitiza a senha também
        senha_limpa = sanitizar_entrada(senha)
        
        # Verifica comprimento
        if len(senha_limpa) < 6:
            erros.append("Senha deve ter pelo menos 6 caracteres")
        
        if len(senha_limpa) > 128:
            erros.append("Senha muito longa (máximo 128 caracteres)")
        
        # Verifica se a senha original foi modificada na sanitização
        if len(senha_limpa) != len(senha):
            erros.append("Senha contém caracteres não permitidos")
        
        return len(erros) == 0, erros
        
    except ValueError:
        erros.append("Senha contém caracteres ou comandos não permitidos")
        return False, erros

def validar_dados_login_seguro(dados: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Valida dados de login de forma segura contra SQL Injection
    """
    erros = []
    
    if not dados:
        erros.append("Dados não fornecidos")
        return False, erros
    
    # Valida email_telefone
    email_telefone = dados.get('email_telefone', '')
    if not email_telefone:
        erros.append("Email ou RA é obrigatório")
    else:
        valido, tipo, valor_limpo = validar_email_telefone_seguro(email_telefone)
        if not valido:
            erros.append("Email ou RA em formato inválido ou contém caracteres não permitidos")
    
    # Valida senha
    senha = dados.get('senha', '')
    senha_valida, erros_senha = validar_senha_segura(senha)
    if not senha_valida:
        erros.extend(erros_senha)
    
    return len(erros) == 0, erros

# Mantém funções antigas para compatibilidade, mas com segurança
def normalizar_ra(ra: str) -> str:
    """
    Normaliza RA removendo caracteres especiais de forma segura
    """
    try:
        ra_sanitizado = sanitizar_entrada(ra)
        return re.sub(r'[-.\s]', '', ra_sanitizado)
    except ValueError:
        return ""  # Retorna vazio se entrada é maliciosa

def validar_ra(ra: str) -> bool:
    """
    Valida RA (mantido para compatibilidade)
    """
    return validar_ra_formato(ra)

def validar_dados_login(dados: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Função antiga mantida para compatibilidade, mas usando validação segura
    """
    return validar_dados_login_seguro(dados)
