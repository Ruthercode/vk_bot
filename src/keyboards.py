from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from abc import ABC, abstractmethod
from src import tools
import re


class Keyboard(ABC):
    keyboard_buttons = None
    have_tools = False
    response = ""

    @abstractmethod
    def return_buttons(self):
        return self.keyboard_buttons

    @abstractmethod
    def return_response(self):
        return self.response;

    @abstractmethod
    def set_next(self, command):
        pass


class DefaultKeyboard(Keyboard):
    def __init__(self):
        self.keyboard_buttons = VkKeyboard(one_time=True)
        self.keyboard_buttons.add_button("Расписание", color=VkKeyboardColor.PRIMARY)
        self.keyboard_buttons.add_button("Погода", color=VkKeyboardColor.PRIMARY)
        self.keyboard_buttons.add_line

        self.have_tools = False

        self.response = "Что вы ищете?"

    def return_buttons(self):
        return super().return_buttons()

    def return_response(self):
        return super().return_response()

    def set_next(self, command):
        if command == "Расписание":
            return ScheduleKeyboard()

        return self


class ScheduleKeyboard(Keyboard):
    def __init__(self):
        self.keyboard_buttons = VkKeyboard(one_time=True)
        self.keyboard_buttons.add_button("Сегодня", color=VkKeyboardColor.POSITIVE)
        self.keyboard_buttons.add_button("Завтра", color=VkKeyboardColor.NEGATIVE)
        self.keyboard_buttons.add_line

        self.have_tools = True

        self.response = "На какой день?"

    def return_buttons(self):
        return super().return_buttons()

    def return_response(self):
        return super().return_response()

    def set_next(self, command):
        tool = None
        if command == "Сегодня":
            tool = tools.ScheduleTool

        if command == "Завтра":
            tool = tools.TomorrowScheduleTool

        return tool


class Handler:
    def __init__(self):
        self.keyboard = DefaultKeyboard()
        self.command = ""
        self.tool = None
        self.answer = self.keyboard.return_response()

    def return_keyboard(self):
        return self.keyboard.return_buttons()

    def set_command(self, message):
        self.command = message

    def return_answer(self):
        if self.tool != None:
            self.command = self.command.lower()
            self.command = re.sub(',+', ' ', self.command)
            self.tool = self.tool(self.command)
            self.tool.set_response_handler()

            answer = self.tool.get_response()

            self.keyboard = DefaultKeyboard()
            self.command = ""
            self.tool = None
            self.answer = self.keyboard.return_response()

            return answer

        if self.keyboard.have_tools:
            self.tool = self.keyboard.set_next(self.command)
            self.answer = self.tool().greeting
        else:
            self.keyboard = self.keyboard.set_next(self.command)
            self.answer = self.keyboard.return_response()
            print(self.keyboard.__class__)

        return self.answer
