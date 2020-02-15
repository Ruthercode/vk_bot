from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def delault_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Расписание", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Погода", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line
    return keyboard
