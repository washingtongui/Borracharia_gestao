# busca_cliente/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # O prefixo 'clientes/' já foi definido no arquivo raiz, então aqui vai só o resto:
    path('gestaoClientes/', views.gestaoClientes, name='gestao_clientes'),
    path('estoque/', views.estoque_geral, name='estoque_geral'), # Adicione esta linha
    path('cadastrar-cliente/', views.cadastrar_usuario, name='cadastrar_cliente'),
    path('cadastrar-veiculo/<int:id_cliente>/', views.cadastrar_veiculo, name='cadastrar_veiculo'),
    path('criar-os/<int:id_cliente>/', views.criar_nova_os, name='criar_nova_os'),
    path('adicionar-itens/<int:id_os>/', views.adicionar_itens_os, name='adicionar_itens_os'),
    path('cancelar-os/<int:id_os>/', views.cancelar_os, name='cancelar_os'),
]