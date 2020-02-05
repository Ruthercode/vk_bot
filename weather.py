import requests

search_url = 'https://api.gismeteo.net/v2/search/cities/'
weather_url = 'https://api.gismeteo.net/v2/weather/current/'

wind_scale_8 = {0: 'Штиль',
                1: 'Северный',
                2: 'Северо-восточный',
                3: 'Восточный',
                4: 'Юго-восточный',
                5: 'Южный',
                6: 'Юго-западный',
                7: 'Западный',
                8: 'Северо-западный'}


def sity_search(sity: str):
    params = dict(query=sity)

    response = requests.get(url=search_url, params=params, headers={
        'X-Gismeteo-Token': '5c51afc32bfd12.13951840',
        'Accept-Encoding': 'deflate,gzip'
    }).json()

    if response['meta']['code'] != '200':
        return -1

    response = response['response']['items'][0]['id']
    return response


def get_weather_by_id(id: int) -> str:
    response = requests.get(url=weather_url + str(id) + '/', headers={
        'X-Gismeteo-Token': '5c51afc32bfd12.13951840',
        'Accept-Encoding': 'deflate,gzip'
    }).json()

    if response['meta']['code'] != '200':
        return "Ошибка " + response['meta']['code'] + ". Погода не определена"

    response = response['response']
    return '{description} \n' \
           'Температура: {temp}\n' \
           'Ощущается как {feels_like} \n' \
           'Ветер {wind}, cкорость {wind_speed}м/с  \n' \
           'Облачность: {clouds}% \n' \
           'Влажность: {humidity}%'.format(description=response['description']['full'],
                                           temp=response['temperature']['air']['C'],
                                           feels_like=response['temperature']['comfort']['C'],
                                           wind=wind_scale_8[response['wind']['direction']['scale_8']],
                                           wind_speed=response['wind']['speed']['m_s'],
                                           clouds=response['cloudiness']['percent'],
                                           humidity=response['humidity']['percent'])


def get_weather(message: list):
    if message.__len__() == 0:
        sity = "Таганрог"
    else:
        sity = ' '.join(message)
    id = sity_search(sity)
    return get_weather_by_id(id)
