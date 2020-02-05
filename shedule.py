import requests
url = "http://165.22.28.187/schedule-api/"

def get_shedule(group,week,day):
    params = dict(group=group)
    resp = requests.get(url,params)

    if week not in resp.json()["weeks"]:
        return "Расписание на эту неделю ещё не готово"

    params = dict(group=group,week=week)
    resp = requests.get(url, params).json()["table"]

    answer_list = resp['table'][0][1:]
    answer = ""
    for i in range(answer_list.__len__()):
        answer_list[i] += ' ' +resp['table'][1][i+1] + ') '
        if resp['table'][day+1][i + 1].__len__() == 0:
            answer_list[i] += '-'
        else:
            answer_list[i] += resp['table'][day+1][i + 1]
        answer =  answer + answer_list[i] + '\n'
    return answer

get_shedule("16.htm", 2,1)