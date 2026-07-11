/**
 * LÓGICA DE CÁLCULO DO TOTAL
 * Percorre as linhas da tabela, multiplica qtd por valor unitário e atualiza o total geral.
 */
function calcularTotal() {
  let total = 0;
  const linhas = document.querySelectorAll('.linha-produto');

  linhas.forEach(linha => {
    let qtd = parseFloat(linha.querySelector('input[name="qtd[]"]').value) || 0;
    let valorUnit = parseFloat(linha.querySelector('input[name="valor[]"]').value) || 0;
    total += (qtd * valorUnit);
  });

  const totalOsElement = document.getElementById('total_os');
  if (totalOsElement) {
    totalOsElement.value = total.toFixed(2);
  }
}

/**
 * LÓGICA DE AUTO-PREENCHIMENTO DO VALOR
 * Busca o preço no atributo 'data-preco' e atualiza o input da linha.
 */
function atualizarValor(selectElement) {
  let linha = selectElement.closest('tr');
  let preco = selectElement.options[selectElement.selectedIndex].getAttribute('data-preco');

  let inputValor = linha.querySelector('input[name="valor[]"]');
  inputValor.value = preco ? preco : "";
  calcularTotal();
}

/**
 * LÓGICA DE ADICIONAR NOVA LINHA
 * Clona a linha de produto e reseta os valores.
 */
const btnAdicionar = document.getElementById('btn-adicionar');
if (btnAdicionar) {
  btnAdicionar.addEventListener('click', function () {
    const corpoTabela = document.getElementById('corpo-tabela');
    const primeiraLinha = document.querySelector('.linha-produto');
    const novaLinha = primeiraLinha.cloneNode(true);

    novaLinha.querySelectorAll('input').forEach(input => input.value = '');
    novaLinha.querySelector('select').selectedIndex = 0;
    corpoTabela.appendChild(novaLinha);
  });
}

/**
 * LÓGICA DE DELEGAÇÃO PARA REMOVER LINHA E INPUTS
 */
const corpoTabela = document.getElementById('corpo-tabela');
if (corpoTabela) {
  corpoTabela.addEventListener('click', function (e) {
    if (e.target.classList.contains('btn-remover')) {
      const linhas = document.querySelectorAll('.linha-produto');
      if (linhas.length > 1) {
        e.target.closest('tr').remove();
        calcularTotal();
      } else {
        alert("A OS precisa de pelo menos um item.");
      }
    }
  });

  corpoTabela.addEventListener('input', function (e) {
    if (e.target.name === 'qtd[]' || e.target.name === 'valor[]') {
      calcularTotal();
    }
  });
}

/**
 * LÓGICA DE CONTROLE DO BOTÃO VOLTAR
 * Mostra ou esconde o botão conforme preenchimento dos campos de veículo/funcionário.
 */
const selectVeiculo = document.getElementById('id_veiculo');
const selectFuncionario = document.getElementById('id_funcionario');
const btnVoltar = document.getElementById('btn-voltar');

if (selectVeiculo && selectFuncionario && btnVoltar) {
  function verificarCampos() {
    if (selectVeiculo.value !== "" || selectFuncionario.value !== "") {
      btnVoltar.style.display = 'none';
    } else {
      btnVoltar.style.display = 'inline-block';
    }
  }

  selectVeiculo.addEventListener('change', verificarCampos);
  selectFuncionario.addEventListener('change', verificarCampos);
  verificarCampos(); // Validação inicial
}