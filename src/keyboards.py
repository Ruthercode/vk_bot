from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from src import tools


class Node:
    def __init__(self, obj, children, is_tool: bool):
        self.obj = obj
        self.children = children
        self.is_tool = is_tool


class Tree:
    def __init__(self):
        self.root = Node(obj=Keyboard(),
                         children=("Погода", "Расписание"),
                         is_tool=False)
        self.root.obj.set_default_keyboard()

        weather = Node(obj=Keyboard(),
                       children=("Город",),
                       is_tool=False)
        weather.obj.set_weather_keyboard()

        schedule = Node(obj=Keyboard(),
                        children=("Сегодня", "Завтра"),
                        is_tool=False)
        schedule.obj.set_schedule_keyboard()

        today_schedule = Node(obj=tools.ScheduleTool,
                              children=(),
                              is_tool=True)

        tomorrow_schedule = Node(obj=tools.TomorrowScheduleTool,
                                 children=(),
                                 is_tool=True)

        sity_weather = Node(obj=tools.WeatherTool,
                            children=(),
                            is_tool=True)

        self.nodes = {"Эрнест": self.root,
                      "Погода": weather,
                      "Расписание": schedule,
                      "Сегодня": today_schedule,
                      "Завтра": tomorrow_schedule,
                      "Город": sity_weather}


class Keyboard:
    def __init__(self):
        self.keyboard_buttons = None
        self.response = ""
        self.set_default_keyboard()

    def return_buttons(self):
        return self.keyboard_buttons

    def return_response(self):
        return self.response;

    def set_default_keyboard(self):
        self.keyboard_buttons = VkKeyboard(one_time=True)
        self.keyboard_buttons.add_button("Расписание", color=VkKeyboardColor.PRIMARY)
        self.keyboard_buttons.add_button("Погода", color=VkKeyboardColor.PRIMARY)
        self.keyboard_buttons.add_line

        self.response = "Да-да я"

    def set_schedule_keyboard(self):
        self.keyboard_buttons = VkKeyboard(one_time=True)
        self.keyboard_buttons.add_button("Сегодня", color=VkKeyboardColor.POSITIVE)
        self.keyboard_buttons.add_button("Завтра", color=VkKeyboardColor.NEGATIVE)
        self.keyboard_buttons.add_line

        self.response = "На какой день?"

    def set_weather_keyboard(self):
        self.keyboard_buttons = None

        self.response = "Укажите название вашего города"


class Handler:
    def __init__(self):
        self.tree = Tree()
        self.current_node = self.tree.root
        self.command = ""
        self.answer = "Да-да я"

    def take_command(self, message):
        self.command = message

    def compute_next_step(self):
        answer = ""
        if self.current_node.is_tool:
            self.command = self.command.lower()
            tool = self.current_node.obj(self.command)
            tool.set_response_handler()
            answer = tool.get_response()

            self.current_node = self.tree.root
        else:
            if self.command not in self.current_node.children:
                self.current_node = self.tree.root
                answer = "Не понял"
            else:
                idx = self.current_node.children.index(self.command)
                self.current_node = self.tree.nodes[self.current_node.children[idx]]
                if self.current_node.is_tool:
                    answer = self.current_node.obj.greeting
                else:
                    answer = self.current_node.obj.return_response()
        return answer
