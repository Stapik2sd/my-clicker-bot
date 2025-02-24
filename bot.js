const { Telegraf, Markup } = require('telegraf');

const bot = new Telegraf('7588402465:AAE0n9hgqx99ZqihhSNy-Ze2VNMZfb1UUVw');

let players = {}; // Данные игроков (клики, уровень, монеты)

// Получение данных игрока
function getPlayer(userId) {
    if (!players[userId]) {
        players[userId] = { clicks: 0, level: 1, coins: 0 };
    }
    return players[userId];
}

// Главное меню
function mainMenu() {
    return Markup.inlineKeyboard([
        [Markup.button.callback(`🔘 Кликнуть!`, 'click')],
        [Markup.button.callback('📊 Посмотреть счётчик', 'counter')],
        [Markup.button.callback('🏪 Магазин', 'shop')]
    ]);
}

// Старт
bot.start((ctx) => {
    const userId = ctx.from.id;
    getPlayer(userId); // Создаём игрока
    ctx.reply('Привет! Добро пожаловать в кликер-бота.', mainMenu());
});

// Обработка клика (реакция без задержек)
bot.action('click', async (ctx) => {
    const userId = ctx.from.id;
    const player = getPlayer(userId);
    player.clicks += 1;
    player.coins += 1; // Начисляем монеты

    // Повышение уровня каждые 10 кликов
    if (player.clicks % 10 === 0) {
        player.level += 1;
    }

    // **Мгновенный отклик без редактирования**
    await ctx.answerCbQuery(`+1 клик! 🔘 (Всего: ${player.clicks})`, { show_alert: false });
});

// Счётчик кликов
bot.action('counter', async (ctx) => {
    const userId = ctx.from.id;
    const player = getPlayer(userId);

    await ctx.reply(
        `📊 Твой счётчик:\n👤 Уровень: ${player.level}\n💰 Монеты: ${player.coins}\n🔘 Кликов: ${player.clicks}`,
        mainMenu()
    );
});

// Магазин
bot.action('shop', async (ctx) => {
    const userId = ctx.from.id;
    const player = getPlayer(userId);
    
    await ctx.reply(
        `🏪 Магазин:\n💰 Твои монеты: ${player.coins}\n\nВыбери покупку:`,
        Markup.inlineKeyboard([
            [Markup.button.callback('⚡ Ускорить клики (10 монет)', 'buy_boost')],
            [Markup.button.callback('⬅️ Назад', 'start')]
        ])
    );
});

// Покупка улучшения
bot.action('buy_boost', async (ctx) => {
    const userId = ctx.from.id;
    const player = getPlayer(userId);

    if (player.coins >= 10) {
        player.coins -= 10;
        player.clicks += 5; // Бонусные клики
        await ctx.answerCbQuery('✅ Покупка успешна! +5 кликов.');
    } else {
        await ctx.answerCbQuery('❌ Недостаточно монет!', { show_alert: true });
    }
});

// Возвращение в главное меню
bot.action('start', async (ctx) => {
    await ctx.reply('🔙 Возвращаемся в главное меню...', mainMenu());
});

bot.launch();
console.log('Бот запущен! ✅');
