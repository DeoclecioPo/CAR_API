const prisma = require('../prisma');

function camposObrigatorios({ placa, modelo, marca }) {
  return Boolean(placa && modelo && marca);
}

/**
 * Loga o erro real do Prisma para diagnóstico e devolve um status mais preciso.
 * Códigos comuns: P2002 (unique constraint), P2003 (foreign key), P2025 (não encontrado).
 */
function tratarErroPrisma(erro, res, acao) {
  console.error(`[ERRO Prisma - ${acao}]`, erro.message);
  if (erro.code === 'P2002') {
    return res.status(409).json({ erro: 'Placa já cadastrada. Informe uma placa única.' });
  }
  if (erro.code === 'P2003') {
    return res.status(409).json({ erro: 'Não foi possível completar: veículo possui manutenções vinculadas.' });
  }
  if (erro.code === 'P2025') {
    return res.status(404).json({ erro: 'Registro não encontrado.' });
  }
  return res.status(500).json({ erro: `Erro interno ao ${acao}.` });
}

async function criarVeiculo(req, res) {
  try {
    const { placa, modelo, marca } = req.body;
    if (!camposObrigatorios(req.body)) {
      return res.status(400).json({ erro: 'Placa, modelo e marca são obrigatórios.' });
    }
    const novoVeiculo = await prisma.veiculo.create({
      data: { placa, modelo, marca }
    });
    return res.status(201).json(novoVeiculo);
  } catch (erro) {
    return tratarErroPrisma(erro, res, 'cadastrar veículo');
  }
}

async function listarVeiculos(req, res) {
  try {
    const veiculos = await prisma.veiculo.findMany({
      include: { manutencoes: true }
    });
    return res.status(200).json(veiculos);
  } catch (erro) {
    console.error('[ERRO Prisma - listar veículos]', erro.message);
    return res.status(500).json({ erro: 'Erro ao listar veículos.' });
  }
}

async function buscarVeiculoPorId(req, res) {
  try {
    const { id } = req.params;
    const veiculo = await prisma.veiculo.findUnique({
      where: { id: Number(id) },
      include: { manutencoes: true }
    });
    if (!veiculo) {
      return res.status(404).json({ erro: 'Veículo não encontrado.' });
    }
    return res.status(200).json(veiculo);
  } catch (erro) {
    return tratarErroPrisma(erro, res, 'buscar veículo');
  }
}

async function atualizarVeiculo(req, res) {
  try {
    const { id } = req.params;
    const { placa, modelo, marca } = req.body;
    if (!camposObrigatorios(req.body)) {
      return res.status(400).json({ erro: 'Placa, modelo e marca são obrigatórios.' });
    }
    const veiculoAtualizado = await prisma.veiculo.update({
      where: { id: Number(id) },
      data: { placa, modelo, marca }
    });
    return res.status(200).json(veiculoAtualizado);
  } catch (erro) {
    return tratarErroPrisma(erro, res, 'atualizar veículo');
  }
}

async function apagarVeiculo(req, res) {
  try {
    const { id } = req.params;
    await prisma.veiculo.delete({ where: { id: Number(id) } });
    return res.status(204).send();
  } catch (erro) {
    return tratarErroPrisma(erro, res, 'excluir veículo');
  }
}

module.exports = {
  criarVeiculo,
  listarVeiculos,
  buscarVeiculoPorId,
  atualizarVeiculo,
  apagarVeiculo
};
