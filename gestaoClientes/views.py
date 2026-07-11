import os
import logging
import pyodbc
from dotenv import load_dotenv
from django.shortcuts import render, redirect
from django.contrib import messages

logger = logging.getLogger(__name__)

# --- Conexão ---
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

# --- Execução Segura ---
def _executar_sql(query, params=()):
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        return columns, rows
    finally:
        try: cursor.close() 
        except: pass
        try: conn.close() 
        except: pass

# --- Views ---

def gestaoClientes(request):
    cpf = request.GET.get('cpf')
    cliente, veiculos, error_message = None, [], None

    if not cpf:
        request.session.pop('id_cliente_autorizado', None)
    
    if cpf:
        try:
            cols_c, rows_c = _executar_sql(
                "SELECT TOP 1 id_cliente, nome, cpf_cnpj, telefone, email FROM [dbo].[Clientes] WHERE cpf_cnpj = ?", 
                (cpf,)
            )
            if rows_c:
                cliente = dict(zip(cols_c, rows_c[0]))
                request.session['id_cliente_autorizado'] = cliente['id_cliente']
                
                cols_v, rows_v = _executar_sql(
                    "SELECT * FROM [dbo].[Veiculos] WHERE id_cliente = ?", 
                    (cliente['id_cliente'],)
                )
                veiculos = [dict(zip(cols_v, row)) for row in rows_v]
            else:
                error_message = "Cliente não encontrado."
                request.session.pop('id_cliente_autorizado', None)
        except Exception as exc:
            logger.exception('Erro na busca')
            error_message = f'Erro na consulta: {exc}'

    return render(request, 'gestaoClientes.html', {
        'cliente': cliente, 
        'veiculos': veiculos, 
        'cpf_digitado': cpf, 
        'error_message': error_message
    })

def cadastrar_usuario(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        cpf = request.POST.get('cpf')
        telefone = request.POST.get('telefone')
        email = request.POST.get('email')

        try:
            conn = _get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM [dbo].[Clientes] WHERE cpf_cnpj = ?", (cpf,))
            existe = cursor.fetchone()[0]

            if existe > 0:
                messages.warning(request, 'Atenção: Este CPF/CNPJ já está cadastrado!')
            else:
                sql = "INSERT INTO [dbo].[Clientes] (nome, cpf_cnpj, telefone, email) VALUES (?, ?, ?, ?)"
                cursor.execute(sql, (nome, cpf, telefone, email))
                conn.commit()
                messages.success(request, 'Cliente cadastrado com sucesso!')
            cursor.close()
            conn.close()
            return redirect('gestao_clientes')
        except Exception as e:
            logger.exception('Erro ao cadastrar cliente')
            messages.error(request, f'Erro ao salvar: {e}')

    return render(request, 'cadastroClientes.html')

def cadastrar_veiculo(request, id_cliente):
    id_autorizado = request.session.get('id_cliente_autorizado')
    if id_autorizado is None or int(id_cliente) != int(id_autorizado):
        messages.error(request, "Acesso negado.")
        return redirect('gestao_clientes')

    cols, rows = _executar_sql("SELECT id_cliente, nome FROM [dbo].[Clientes] WHERE id_cliente = ?", (id_cliente,))
    if not rows:
        messages.error(request, "Cliente não encontrado.")
        return redirect('gestao_clientes')
    
    cliente = dict(zip(cols, rows[0]))

    if request.method == 'POST':
        placa = request.POST.get('placa')
        try:
            conn = _get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM [dbo].[Veiculos] WHERE placa = ?", (placa,))
            existe = cursor.fetchone()[0]

            if existe > 0:
                messages.warning(request, f"Atenção: O veículo com placa {placa} já está cadastrado!")
            else:
                cursor.execute(
                    "INSERT INTO [dbo].[Veiculos] (id_cliente, placa, marca, modelo, ano) VALUES (?, ?, ?, ?, ?)",
                    (id_cliente, placa, request.POST.get('marca'), request.POST.get('modelo'), request.POST.get('ano'))
                )
                conn.commit()
                messages.success(request, f"Veículo cadastrado para {cliente['nome']}!")
            cursor.close()
            conn.close()
            return redirect('gestao_clientes')
        except Exception as e:
            messages.error(request, f"Erro ao salvar: {e}")

    return render(request, 'cadastroVeiculos.html', {'cliente': cliente})

def criar_nova_os(request, id_cliente):
    # 1. Busca dados iniciais (simplificado usando sua função _executar_sql)
    cols_c, rows_c = _executar_sql("SELECT nome FROM Clientes WHERE id_cliente = ?", (id_cliente,))
    cliente = {'nome': rows_c[0][0]} if rows_c else {'nome': 'Cliente não encontrado'}

    cols_v, rows_v = _executar_sql("SELECT id_veiculo, placa, modelo FROM Veiculos WHERE id_cliente = ?", (id_cliente,))
    veiculos = [dict(zip(cols_v, row)) for row in rows_v]

    cols_f, rows_f = _executar_sql("SELECT id_funcionario, nome_completo FROM Funcionarios")
    funcionarios = [dict(zip(cols_f, row)) for row in rows_f]

    # 2. Processamento POST
    if request.method == 'POST':
        conn = _get_db_connection()
        try:
            cursor = conn.cursor()
            # Inserção completa para atender às colunas obrigatórias do seu banco
            cursor.execute("""
                INSERT INTO [dbo].[OrdemServico] 
                (id_cliente, id_veiculo, id_funcionario, data_abertura, status_os, valor_total)
                OUTPUT Inserted.id_os
                VALUES (?, ?, ?, GETDATE(), 'Em Execução', 0.00)
            """, (id_cliente, request.POST.get('id_veiculo'), request.POST.get('id_funcionario')))
            
            id_nova_os = cursor.fetchone()[0]
            conn.commit()
            return redirect('adicionar_itens_os', id_os=id_nova_os)
        except Exception as e:
            logger.exception('Erro ao criar OS')
            messages.error(request, f"Erro ao criar OS: {e}")
        finally:
            conn.close()

    return render(request, 'criarNovaOs.html', {
        'cliente': cliente,
        'veiculos': veiculos,
        'funcionarios': funcionarios
    })

from django.shortcuts import render, redirect

def adicionar_itens_os(request, id_os):
    conn = _get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        # 1. Captura os dados do formulário
        produtos = request.POST.getlist('produto[]')
        qtds = request.POST.getlist('qtd[]')
        valores = request.POST.getlist('valor[]')
        observacoes = request.POST.get('observacoes') # Captura a observação
        
        valor_total_calculado = 0.0

        # 2. Insere os itens e calcula o valor total em memória
        for i in range(len(produtos)):
            if produtos[i]:
                valor_unitario = float(valores[i])
                quantidade = int(qtds[i])
                total_item = valor_unitario * quantidade
                valor_total_calculado += total_item

                cursor.execute("""
                    INSERT INTO [dbo].[ItensOrdemServico] (id_os, id_produto, quantidade, valor_unitario)
                    VALUES (?, ?, ?, ?)
                """, (id_os, produtos[i], qtds[i], valor_unitario))
        
        # 3. Atualiza a tabela OrdemServico com o valor total e observações
        cursor.execute("""
            UPDATE [dbo].[OrdemServico] 
            SET valor_total = ?, observacoes = ? 
            WHERE id_os = ?
        """, (valor_total_calculado, observacoes, id_os))
        
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('gestao_clientes')

    else:
        # Busca produtos para o select
        cursor.execute("SELECT id_produto, nome_produto, preco_venda FROM [dbo].[Produtos]")
        produtos_disponiveis = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return render(request, 'adicionarItens.html', {
            'id_os': id_os,
            'produtos_disponiveis': produtos_disponiveis
        })
        
    # Renderiza a tela de adição com o ID da OS em mãos
    return render(request, 'adicionarItens.html', {'id_os': id_os})   
from django.shortcuts import redirect
from django.contrib import messages # Opcional: para exibir mensagens na tela

def cancelar_os(request, id_os):
    conn = None
    try:
        # Abre a conexão com o banco
        conn = _get_db_connection()
        cursor = conn.cursor()
        
        # Realiza o UPDATE para marcar a OS como 'Cancelada'
        # Usamos parâmetros (?) para evitar SQL Injection
        cursor.execute("""
            UPDATE [dbo].[OrdemServico] 
            SET status_os = 'Cancelada' 
            WHERE id_os = ?
        """, (id_os,))
        
        conn.commit()
        
    except Exception as e:
        # Se ocorrer um erro, você pode logar ou exibir uma mensagem
        print(f"Erro ao cancelar a OS: {e}")
        # Opcional: messages.error(request, "Erro ao cancelar a OS.")
        
    finally:
        # Garante que a conexão seja fechada, independente de ter dado erro ou não
        if conn:
            cursor.close()
            conn.close()
            
    # Redireciona de volta para a listagem (certifique-se que 'gestao_clientes' 
    # é o nome da rota no seu urls.py)
    return redirect('gestao_clientes')

#Não mexer aqui, pois é uma página que será criada futuramente.
def estoque_geral(request):
    return render(request, 'estoque.html')