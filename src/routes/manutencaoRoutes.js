const express = require('express');
const router = express.Router();
const manutencaoController = require('../controllers/manutencaoController');
const validarId = require('../middlewares/validarId');
const { validarManutencao } = require('../middlewares/validarDados');

router.post('/manutencoes', validarManutencao, manutencaoController.criarManutencao);
router.get('/manutencoes', manutencaoController.listarManutencoes);
router.get('/manutencoes/:id', validarId, manutencaoController.buscarManutencaoPorId);
router.put('/manutencoes/:id', validarId, validarManutencao, manutencaoController.atualizarManutencao);
router.delete('/manutencoes/:id', validarId, manutencaoController.apagarManutencao);

module.exports = router;