const prisma = require('../prisma');

function tratarErroPrisma(erro, res, acao) {
  console.error(`[ERRO Prisma - ${acao}]`, erro.message);
  if (erro.code === 'P2003') {
    return res.status(409).json({ erro: 'veiculoId inválido: o veículo referenciado não existe.' });
  }
  if (erro.code === 'P2025') {
    return res.status(404).json({ erro: 'Registro não encontrado.' });
  }
  return res.status(500).json({ erro: `Erro interno ao ${acao}.` });
}

async function criarManutencao(req, res) {
  try {
    const { descricao, data, valor, veiculoId } = req.body;
    if (!descricao || !data || valor === undefined || valor === null || veiculoId === undefined) {
      return res.status(400).json({ erro: 'Descrição, data, valor e veiculoId são obrigatórios.' });
    }
    if (Number.isNaN(Number(valor)) || !Number.isInteger(Number(veiculoId))) {
      return res.status(400).json({ erro: 'Valor deve ser numérico e veiculoId um ID válido.' });
    }
    const novaManutencao = await prisma.manutencao.create({
      data: {
        descricao,
        data,
        valor: Number(valor),
        veiculoId: Number(veiculoId)
      }
    });
    return res.status(201).json(novaManutencao);
  } catch (erro) {
    return tratarErroPrisma(erro, res, 'criar manutenção');
  }
}

async function listarManutencoes(req, res) {
  try {
    const manutencoes = await prisma.manutencao.findMany({
      include: { veiculo: true }
    });
    return res.status(200).json(manutencoes);
  } catch (erro) {
    console.error('[ERRO Prisma - listar manutenções]', erro.message);
    return res.status(500).json({ erro: 'Erro ao listar manutenções.' });
  }
}

async function buscarManutencaoPorId(req, res) {
  try {
    const { id } = req.params;
    const manutencao = await prisma.manutencao.findUnique({
      where: { id: Number(id) },
      include: { veiculo: true }
    });
    if (!manutencao) {
      return res.status(404).json({ erro: 'Manutenção não encontrada.' });
    }
    return res.status(200).json(manutencao);
  } catch (erro) {
    return tratarErroPrisma(erro, res, 'buscar manutenção');
  }
}

async function atualizarManutencao(req, res) {
  try {
    const { id } = req.params;
    const { descricao, data, valor, veiculoId } = req.body;
    if (!descricao || !data || valor === undefined || valor === null) {
      return res.status(400).json({ erro: 'Descrição, data e valor são obrigatórios.' });
    }
    const dados = { descricao, data, valor: Number(valor) };
    if (veiculoId !== undefined) {
      if (!Number.isInteger(Number(veiculoId))) {
        return res.status(400).json({ erro: 'veiculoId deve ser um ID válido.' });
      }
      dados.veiculoId = Number(veiculoId);
    }
    const manutencaoAtualizada = await prisma.manutencao.update({
      where: { id: Number(id) },
      data: dados
    });
    return res.status(200).json(manutencaoAtualizada);
  } catch (erro) {
    return tratarErroPrisma(erro, res, 'atualizar manutenção');
  }
}

async function apagarManutencao(req, res) {
  try {
    const { id } = req.params;
    await prisma.manutencao.delete({
      where: { id: Number(id) }
    });
    return res.status(204).send();
  } catch (erro) {
    return tratarErroPrisma(erro, res, 'excluir manutenção');
  }
}

module.exports = {
  criarManutencao,
  listarManutencoes,
  buscarManutencaoPorId,
  atualizarManutencao,
  apagarManutencao
};
