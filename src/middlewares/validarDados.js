function validarVeiculo(req, res, next) {
  let { placa, modelo, marca } = req.body;

  if (typeof placa !== 'string' || typeof modelo !== 'string' || typeof marca !== 'string') {
    return res.status(400).json({
      erro: 'Placa, modelo e marca são obrigatórios e devem ser textos.'
    });
  }

  placa = placa.trim().toUpperCase();
  modelo = modelo.trim();
  marca = marca.trim();

  if (placa.length < 7 || modelo.length < 2 || marca.length < 2) {
    return res.status(400).json({
      erro: 'Preencha placa, modelo e marca com valores válidos.'
    });
  }

  req.body.placa = placa;
  req.body.modelo = modelo;
  req.body.marca = marca;
  next();
}

function validarManutencao(req, res, next) {
  let { descricao, data, valor, veiculoId } = req.body;

  if (typeof descricao !== 'string' || descricao.trim().length < 3) {
    return res.status(400).json({
      erro: 'A descrição é obrigatória e deve ter pelo menos 3 caracteres.'
    });
  }

  if (typeof data !== 'string' || data.trim() === '') {
    return res.status(400).json({
      erro: 'A data é obrigatória.'
    });
  }

  const valorNumerico = Number(valor);
  if (valor === undefined || valor === null || valor === '' || Number.isNaN(valorNumerico) || valorNumerico < 0) {
    return res.status(400).json({
      erro: 'O valor é obrigatório e deve ser um número válido maior ou igual a zero.'
    });
  }

  req.body.descricao = descricao.trim();
  req.body.data = data.trim();
  req.body.valor = valorNumerico;

  if (req.method === 'POST') {
    const idVeiculo = Number(veiculoId);
    if (veiculoId === undefined || veiculoId === null || veiculoId === '' || !Number.isInteger(idVeiculo) || idVeiculo <= 0) {
      return res.status(400).json({
        erro: 'O campo veiculoId é obrigatório e deve ser um número inteiro positivo.'
      });
    }
    req.body.veiculoId = idVeiculo;
  } else if (veiculoId !== undefined) {
    const idVeiculo = Number(veiculoId);
    if (!Number.isInteger(idVeiculo) || idVeiculo <= 0) {
      return res.status(400).json({
        erro: 'O campo veiculoId deve ser um número inteiro positivo.'
      });
    }
    req.body.veiculoId = idVeiculo;
  }

  next();
}

module.exports = {
  validarVeiculo,
  validarManutencao
};