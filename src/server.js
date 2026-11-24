require('dotenv').config();
const express = require('express');
const logger = require('./middlewares/logger');
const veiculoRoutes = require('./routes/veiculoRoutes');
const manutencaoRoutes = require('./routes/manutencaoRoutes');

const app = express();
const PORTA = 3000;

app.use(express.json());
app.use(logger);

app.get('/status', (req, res) => {
  return res.status(200).json({ status: 'API Online' });
});

app.use(veiculoRoutes);
app.use(manutencaoRoutes);

app.listen(PORTA, () => {
  console.log(`[SERVIDOR OK] Rodando em http://localhost:${PORTA}`);
});