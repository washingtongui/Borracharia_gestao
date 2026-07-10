import os
import logging
import pyodbc
from dotenv import load_dotenv
from django.shortcuts import render

logger = logging.getLogger(__name__)

# Função auxiliar para manter o DRY (Don't Repeat Yourself)
def _get_db_connection():
    load_dotenv()
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={os.getenv('DB_HOST')};"
        f"DATABASE={os.getenv('DB_NAME')};"
        f"UID={os.getenv('DB_USER')};"
        f"PWD={os.getenv('DB_PASSWORD')}"
    )
    return pyodbc.connect(conn_str)

def _executar_sql(query):
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [col[0] for col in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        return columns, rows
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass

# --- Suas Views ---

def gestaoClientes(request):
    cpf = request.GET.get('cpf')
    cliente = None
    veiculos = []
    error_message = None

    if cpf:
        try:
            # 1. Busca o cliente pelo CPF
            # Usamos TOP 1 para garantir apenas um resultado
            cols_c, rows_c = _executar_sql(f"SELECT TOP 1 id_cliente, nome, cpf_cnpj, telefone, email FROM [dbo].[Clientes] WHERE cpf_cnpj = '{cpf}'")
            
            if rows_c:
                cliente = dict(zip(cols_c, rows_c[0]))
                
                # 2. Busca os veículos vinculados ao ID do cliente encontrado
                cols_v, rows_v = _executar_sql(f"SELECT * FROM [dbo].[Veiculos] WHERE id_cliente = {cliente['id_cliente']}")
                veiculos = [dict(zip(cols_v, row)) for row in rows_v]
            else:
                error_message = "Cliente não encontrado."
        except Exception as exc:
            logger.exception('Erro na busca')
            error_message = f'Erro na consulta: {exc}'

    return render(request, 'gestaoClientes.html', {
        'cliente': cliente, 
        'veiculos': veiculos, 
        'cpf_digitado': cpf,
        'error_message': error_message
    })

def estoque_geral(request):
    try:
        # Puxando os dados das suas Views no SQL Server
        columns_estoque, rows_estoque = _executar_sql("SELECT * FROM View_EstoqueAtual")
        columns_saidas, rows_saidas = _executar_sql("SELECT * FROM View_SaidaProdutos")

        # Converte para dicionários usando os nomes das colunas retornadas
        estoque = [dict(zip(columns_estoque, row)) for row in rows_estoque]
        saidas = [dict(zip(columns_saidas, row)) for row in rows_saidas]
        error_message = None
    except Exception as exc:
        estoque = []
        saidas = []
        logger.exception('Erro ao consultar estoque')
        error_message = f'Erro ao consultar estoque: {exc}'
        
    return render(request, 'estoque.html', {'estoque': estoque, 'saidas': saidas, 'error_message': error_message})