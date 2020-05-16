import requests
from time import sleep
def get_weather(city):
    appcode = 'fd258ad74ac748ecb0116d829f4a46e8'
    url = 'http://jisutqybmf.market.alicloudapi.com/weather/query'
    headers = {'Authorization': 'APPCODE ' + appcode}
    content = requests.get(url=url, params={'city': city}, headers=headers)
    # print(content.status_code )
    while (not content.status_code):
        sleep(2)
        content = requests.get(url=url, params={'city': city}, headers=headers)
    return content.json()
# print(get_weather("长春"))
# {'status': '202', 'msg': '城市不存在', 'result': ''}
# a = get_weather('长春').get('result')
# print(a)
# for i in a.get('daily'):
#     print(i)
#     # print(i.get('date').split('-')[-1],i.get('week'),i.get('night').get('templow'),i.get('day').get('weather'),
    #       i.get('day').get('temphigh'),
    #       i.get('day').get('img'),i.get('day').get('winddirect'),i.get('day').get('windpower'))




# print(a.get('city'))
# print(a.get('date').split('-')[-1])
# print(a.get('week'))
# print(":".join(a.get('updatetime').split(' ')[-1].split(':')[-3:-1]))
# print(a.get('weather'))
# print(a.get('winddirect'))
# print(a.get('windpower'))
# print(a.get('temp'))
# print(a.get('temphigh'))
# print(a.get('templow'))