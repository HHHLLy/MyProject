from datetime import datetime
def my_time(value):
    now_time = datetime.strptime(value, '%Y-%m-%d %H:%M')

    ii = str(datetime.today().__sub__(now_time))
    if 'days' in ii:
        time = ii.split(',')[0].replace('days', '')
        days = int(int(time)/30)
        if days>0:
            years = int(days/24)
            if years>0:
                time = str(years)+'年前'
            else:
                time = str(days)+'个月前'
        else:
            time = time+'天前'
    else:
        time = ii.split(':')[:-1]
        if time[0] != '0' :
            time = time[0]+'个小时前'
        elif time[0]=='0' and time[1]=='00':
            time = '刚刚'
        else:
            if int(time[1])>9:
                time = time[1]+'分钟前'
            else:
                time = time[1].replace('0','') + '分钟前'
    return  time