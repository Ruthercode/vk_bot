from vkbot import VkBot

token = "5277d48df2317b0597d43fa36fb0b694bc50f6496a516cb4f62ec4e26098a4efd157a155b01230cc46635"  # Bot's token.
bot = VkBot(token=token)

bot.start_longpoll()