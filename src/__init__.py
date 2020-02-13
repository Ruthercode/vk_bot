commands_description = \
    {
        "Погода %город%": "Выдаёт информацию о текущей погоде. Можно указать страну",
        # WeatherTool and SearchTool
        "Расписание %группа%": "Расписание вашей группы на сегодняшний день",
        # ScheduleTool
        "Исходный код": "Ссылка на исходный код бота",
        # No tool command
        "Завтрашнее расписание %группа%": "Расписание вашей группы на завтрашний день"
        # TomorrowScheduleTool
    }  # TODO: Переодически обновлять

groups = {}

if groups.__len__() == 0:
    with open("src/groups.txt") as file:
        for line in file:
            pair = line.lower().split()
            groups[pair[0]] = pair[1]
