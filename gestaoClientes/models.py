from django.db import models

class Clientes(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    cpf_cnpj = models.CharField(max_length=19, unique=True)
    telefone = models.CharField(max_length=15)
    email = models.CharField(max_length=100, blank=True, null=True)
    data_cadastro = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Clientes'

class Fornecedores(models.Model):
    id_fornecedor = models.AutoField(primary_key=True)
    razao_social = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=19, unique=True)
    representante = models.CharField(max_length=50, blank=True, null=True)
    telefone_comercial = models.CharField(max_length=15)

    class Meta:
        managed = False
        db_table = 'Fornecedores'

class Funcionarios(models.Model):
    id_funcionario = models.AutoField(primary_key=True)
    nome_completo = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    cargo = models.CharField(max_length=50)
    email = models.CharField(max_length=150, unique=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Funcionarios'

class Produtos(models.Model):
    id_produto = models.AutoField(primary_key=True)
    id_fornecedor = models.ForeignKey(Fornecedores, models.DO_NOTHING, db_column='id_fornecedor')
    nome_produto = models.CharField(max_length=100)
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'Produtos'

class Veiculos(models.Model):
    id_veiculo = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Clientes, models.DO_NOTHING, db_column='id_cliente')
    placa = models.CharField(max_length=8, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    ano = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'Veiculos'

class OrdemServico(models.Model):
    id_os = models.AutoField(primary_key=True)
    id_veiculo = models.ForeignKey(Veiculos, models.DO_NOTHING, db_column='id_veiculo')
    id_funcionario = models.ForeignKey(Funcionarios, models.DO_NOTHING, db_column='id_funcionario')
    data_abertura = models.DateTimeField()
    data_fechamento = models.DateTimeField(blank=True, null=True)
    status_os = models.CharField(max_length=20)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    observacoes = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'OrdemServico'

class ItensOrdemServico(models.Model):
    id_item_os = models.AutoField(primary_key=True)
    id_os = models.ForeignKey(OrdemServico, models.DO_NOTHING, db_column='id_os')
    id_produto = models.ForeignKey(Produtos, models.DO_NOTHING, db_column='id_produto', blank=True, null=True)
    descricao_servico_ou_produto = models.CharField(max_length=150)
    quantidade = models.IntegerField()
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'ItensOrdemServico'

class Estoque(models.Model):
    id_estoque = models.AutoField(primary_key=True)
    id_produto = models.ForeignKey(Produtos, models.DO_NOTHING, db_column='id_produto')
    tipo_movimentacao = models.CharField(max_length=10)
    quantidade = models.IntegerField()
    data_movimento = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Estoque'

class Financeiro(models.Model):
    id_financeiro = models.AutoField(primary_key=True)
    id_os = models.ForeignKey(OrdemServico, models.DO_NOTHING, db_column='id_os')
    forma_pagamento = models.CharField(max_length=30)
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2)
    data_pagamento = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Financeiro'