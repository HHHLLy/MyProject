import json
t = '2020-05-28 23:19:57'

def format_time(self,arg):


    d = {}
    htime = str(arg).split(" ")[0]
    year,mon,day = htime.split('-')
    # if mon == "01":mon = "Jan"
    # if mon == "02":mon = "Jan"
    # if mon == "03":mon = "Jan"
    # if mon == "04":mon = "Jan"
    # if mon == "05":mon = "Jan"
    # if mon == "06":mon = "Jan"
    # if mon == "07":mon = "Jan"
    # if mon == "08":mon = "Jan"
    # if mon == "09":mon = "Jan"
    # if mon == "10":mon = "Jan"
    # if mon == "11":mon = "Jan"
    # if mon == "12":mon = "Jan"
    with open("utils/mon_to_Eng","r") as f:
        mon_to_eng =f.readlines()
    for i in mon_to_eng[0].split(","):
        d[i.split(":")[0].strip('"')] = i.split(":")[-1].strip('"')

    return d[mon] + "." + day + "," + year
    # for i in list(mon_to_eng):
    #     # d[i.split(":")[0]] = i.split(":")[1]
    #     print(i)
    # print(d)
if __name__ == '__main__':
    format_time(t)