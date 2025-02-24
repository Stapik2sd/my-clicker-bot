const express = require('express');
const path = require('path');

const app = express();

// Раздаём WebApp
app.use(express.static(path.join(__dirname, 'webapp')));

// Запуск сервера
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`🚀 WebApp запущен на http://localhost:${PORT}`);
});
