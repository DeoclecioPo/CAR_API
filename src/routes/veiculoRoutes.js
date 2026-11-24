const express = require('express');
const router = express.Router();
const veiculoController = require('../controllers/veiculoController');
const validarId = require('../middlewares/validarId');
const { validarVeiculo } = require('../middlewares/validarDados');

router.post('/veiculos', validarVeiculo, veiculoController.criarVeiculo);
router.get('/veiculos', veiculoController.listarVeiculos);
router.get('/veiculos/:id', validarId, veiculoController.buscarVeiculoPorId);
router.put('/veiculos/:id', validarId, validarVeiculo, veiculoController.atualizarVeiculo);
router.delete('/veiculos/:id', validarId, veiculoController.apagarVeiculo);

module.exports = router;