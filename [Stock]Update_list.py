import csv
import sys
import time
from datetime import datetime,timezone,timedelta
from io import open
import os
import pytz
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.font_manager import FontProperties
import requests
from html.parser import HTMLParser
from bs4 import BeautifulSoup
def Get_Web(url):
    resp = requests.get(
        url=url,
        cookies={'over18': '1'}
    )
    if resp.status_code != 200:
        print('Invalid url:', resp.url)
        return None
    else:
        return resp.text

def Get_Row(page,last_y,last_m,last_d):
    
    soup = BeautifulSoup(page, 'html.parser')
    table = []
    split = []
    output = []
    proc_date = []

    body = soup.find("tbody")
    for table in body.findAll("tr"):
        split=table.text.replace("\n"," ").split(" ")
        
        while '' in split:
            split.remove('')

        proc_date = split[0].split("/")
        proc_y = int(proc_date[0]) + 1911
        proc_m = int(proc_date[1])
        proc_d = int(proc_date[2])
        
        if proc_y == last_y and proc_m == last_m and proc_d <= last_d:
            continue

        if split[1] == 0: # stop trading
            continue

        output.append({
            'date': split[0],
            's_amount': split[1],
            'm_amount': split[2],
            'open': split[3],
            'high': split[4],
            'low': split[5],
            'close': split[6],
            'range': split[7],
            's_count': split[8]
        })

        print('Updated date: ',split[0])
    return output
    
def Update_Stock(St_Num):
    list_stock = []
    filename = './stock_{:04d}.csv'.format(St_Num)
    exist=os.access(filename, os.R_OK)
    title = ['date', 's_amount','m_amount','open','high','low','close','range','s_count']
    if exist:
        f = open(filename, 'r+', newline='')
        rows = csv.reader(f)
        writer = csv.DictWriter(f, fieldnames=title)
        for row in rows:
            list_stock.append(row)
        last_date = list_stock[-1][0].split('/')
        last_y,last_m,last_d  = int(last_date[0])+1911,int(last_date[1]),int(last_date[2])
        if last_y == now_y and last_m == now_m and last_d == now_d:
            return
    else:
        f = open(filename, 'w', newline='')
        writer = csv.DictWriter(f, fieldnames=title)
        writer.writeheader()
        last_y,last_m,last_d = 2011,1,1

    for y in range(2011, 2020):
        if y > now_y+1911:
            break
        for m in range(1, 13):
            if (y == now_y+1911) and (m > int(now_m)):
                break
            if (y < last_y) or (y == last_y and m < last_m):
                continue
            time.sleep(3)
            url = 'http://www.tse.com.tw/exchangeReport/STOCK_DAY?response=html&date={:04d}{:02d}01&stockNo={:04d}'.format(y,m,St_Num)
            #print(url)
            page = Get_Web(url)
            #print(page)
            output = Get_Row(page,last_y,last_m,last_d)
     
            if output:
                for post in output:
                    writer.writerow(post)               
    f.close()   

def Get_DI(list_stock):
    DI=[]
    for idx in range(0,len(list_stock)):
        if idx == 0:
            DI.append(' ')
        else:
            DI.append((float(list_stock[idx][4]) + float(list_stock[idx][5]) + float(list_stock[idx][6])*2)/4)
    return DI
        
def Get_EMA12(DI):
    EMA12=[]
    for idx in range(0,len(DI)):
        val = 0
        if idx < 12:
            EMA12.append(' ')
        elif idx == 12:
            for i in range(12):
                val = val+DI[idx-i]/12
            EMA12.append(val)
        else:
            val = ((EMA12[idx-1] * 11) + (DI[idx] * 2))/13
            EMA12.append(val)

    return EMA12

def Get_EMA26(DI):
    EMA26=[]
    for idx in range(0,len(DI)):
        val = 0
        if idx < 26:
            EMA26.append(' ')
        elif idx == 26:
            for i in range(26):
                val = val+DI[idx-i]/26
            EMA26.append(val)
        else:
            val = ((EMA26[idx-1] * 25) + (DI[idx] * 2))/27
            EMA26.append(val)

    return EMA26

def Get_DIF(EMA12,EMA26):
    DIF=[]
    for idx in range(0,len(EMA12)):
        if idx < 26:
            DIF.append(' ')
        else:
            DIF.append(EMA12[idx]-EMA26[idx])

    return DIF

def Get_MACD(DIF):
    MACD=[]
    for idx in range(0,len(DIF)):
        val = 0
        if idx < 34:
            MACD.append(' ')
        elif idx == 34:
            for i in range(9):
                val = val+DIF[idx-i]/9
            MACD.append(val)
        else:
            val = ((MACD[idx-1] * 8) + (DIF[idx] * 2))/10
            MACD.append(val)

    return MACD

def Get_OSC(DIF,MACD):
    OSC=[]
    for idx in range(0,len(DIF)):
        if idx < 34:
            OSC.append(' ')
        else:
            OSC.append(DIF[idx]-MACD[idx])
    return OSC

def Analyze_Reverse(list_stock,DIF,MACD,OSC):

    Rever_Idx=0

    for idx in range(len(list_stock)-240,len(list_stock)):
        if round(DIF[idx],2) < 0 and round(MACD[idx],2) < 0 and OSC[idx] < 0 and OSC[idx] >= OSC[idx-1] and OSC[idx-1] <= OSC[idx-2]:
            Rever_Idx = idx

    return Rever_Idx

def Analyze_Falling(list_stock,DIF,MACD,OSC):

    Fall_Idx=0

    for idx in range(len(list_stock)-240,len(list_stock)):
        if round(DIF[idx],2) < 0 and round(MACD[idx],2) < 0 and OSC[idx] < 0 and OSC[idx] <= OSC[idx-1] and OSC[idx-1] <= OSC[idx-2] and OSC[idx-2] <= OSC[idx-3]:
            Fall_Idx = idx

    return Fall_Idx

def Analyze_Rising(list_stock,DIF,MACD,OSC):

    Rise_Idx=0

    for idx in range(len(list_stock)-240,len(list_stock)):
        if round(DIF[idx],2) > 0 and round(MACD[idx],2) > 0 and OSC[idx] > 0 and OSC[idx] > OSC[idx-1] and OSC[idx-1] > OSC[idx-2] and OSC[idx-2] > OSC[idx-3]:
            Rise_Idx = idx

    return Rise_Idx
def DrawDiagram(list_stock,F_idx,DIF,MACD,OSC,St_Num):
    dates,price,dif,macd,osc,osc_dif,price=[],[],[],[],[],[],[]

    plt.clf()
    for idx in range(F_idx-20,F_idx):
        str_d = '{:s}/{:s}'.format(list_stock[idx][0].split('/')[1],list_stock[idx][0].split('/')[2])
        dates.append(str_d)
        dif.append(round(float(DIF[idx]),2))    
        macd.append(round(float(MACD[idx]),2))    
        osc.append(round(float(OSC[idx]),2))      
        osc_dif.append(round(float(OSC[idx]-OSC[idx-1]),2))     
        price.append(round(float(list_stock[idx][6]),2))   
    
    xs = dates
    plt.figure(figsize=(2.4,2.4))
    plt.subplot(211)
    font_set = FontProperties(fname=r'C:\Windows\Fonts\simsun.ttc', size=10)
    plt.title(St_Name_List['{:d}'.format(St_Num)],fontproperties=font_set)
    plt.grid(True)
    plt.xticks(fontsize=1,rotation=90)
    plt.yticks(fontsize=6)
    plt.plot(xs,dif,'y',linewidth=1, color='g')
    plt.plot(xs,macd,'y',linewidth=1, color='b')
    plt.plot(xs,osc_dif,'y',linewidth=1, color='r')
    plt.bar(xs,osc,color='y',label="OSC")

    plt.subplot(212)
    plt.grid(True)
    plt.xticks(fontsize=1,rotation=90)
    plt.yticks(fontsize=6)
    plt.plot(xs,price,'y',linewidth=1, color='g')

    plt.savefig('./img/{:d}.png'.format(St_Num))
    plt.close()

    #xs = dates
    plt.figure(figsize=(10.24,10.24))
    plt.subplot(211)
    font_set = FontProperties(fname=r'C:\Windows\Fonts\simsun.ttc', size=25)
    plt.title(St_Name_List['{:d}'.format(St_Num)],fontproperties=font_set)
    plt.grid(True)
    plt.xticks(fontsize=15,rotation=90)
    plt.yticks(fontsize=20)
    plt.plot(xs,dif,'y',linewidth=4, color='g',label="DIF")
    plt.plot(xs,macd,'y',linewidth=4, color='b',label="MACD")
    plt.plot(xs,osc_dif,'y',linewidth=4, color='r',label="OSC_DIF")
    plt.bar(xs,osc,color='y',label="OSC")
    plt.legend(loc='best')

    plt.subplot(212)
    plt.grid(True)
    plt.xticks(fontsize=15,rotation=90)
    plt.yticks(fontsize=20)
    plt.plot(xs,price,'y',linewidth=4, color='g',label="Price")
    plt.legend(loc='best')

    plt.savefig('./img/{:d}_b.png'.format(St_Num))
    plt.close()

def Parse_MACD(list_stock,St_Num):

    DI = Get_DI(list_stock)
    EMA12 = Get_EMA12(DI)
    EMA26 = Get_EMA26(DI)
    DIF = Get_DIF(EMA12,EMA26)
    MACD = Get_MACD(DIF)
    OSC = Get_OSC(DIF,MACD)
    Rever_Idx = Analyze_Reverse(list_stock,DIF,MACD,OSC)
    Falling_Idx = Analyze_Falling(list_stock,DIF,MACD,OSC)
    Rising_Idx = Analyze_Rising(list_stock,DIF,MACD,OSC)

    #############################################################################################################
    # Desktop
    print('--------------------------------------------------------')
    print(St_Name_List['{:d}'.format(St_Num)])
    print('--------------------------------------------------------')
    print('   Date   | Price |   MACD |  DIF   |  OSC   | OSC DIF')
    print('--------------------------------------------------------')
    for idx in range(len(list_stock)-12,len(list_stock)):
        print('{:s} | {:s} | {:.3f} | {:.3f} | {:.3f} | {:.3f}'.format(list_stock[idx][0], list_stock[idx][6]
            , DIF[idx], MACD[idx], OSC[idx], OSC[idx]-OSC[idx-1])
        )
    #############################################################################################################

    DrawDiagram(list_stock,len(list_stock),DIF,MACD,OSC,St_Num)
    return Rever_Idx,Falling_Idx,Rising_Idx

def Analyze_Stock(St_Num):

    list_stock = []
    Reverse = False
    Falling = False
    Rising = False

    f = open('./stock_{:04d}.csv'.format(St_Num), 'r+', newline='')
    rows = csv.reader(f)
    title = ['date', 's_amount','m_amount','open','high','low','close','range','s_count']
    writer = csv.DictWriter(f, fieldnames=title)
    for row in rows:
        list_stock.append(row)

    Rever_Idx,Falling_Idx,Rising_Idx = Parse_MACD(list_stock,St_Num)  
    if Rever_Idx == len(list_stock)-1:
        Reverse = True

    elif Falling_Idx == len(list_stock)-1:
        Falling = True

    elif Rising_Idx == len(list_stock)-1:
        Rising = True

    f.close() 
    return Reverse,Falling,Rising,list_stock

def app_stock(msg):

    text = ''
	
    if '列表' in msg:
        for St_Num in St_Num_List:
            text = text + '{:s}\n'.format(St_Name_List['{:d}'.format(St_Num)])
    
    str1,str2,str3,str4 = '<建議買進>\n','<接近買點>\n','<接近賣點>\n','<不宜買進>\n'

    for St_Num in St_Num_List:
        St_Name = St_Name_List['{:04d}'.format(St_Num)]
        if St_Name in msg:
            Update_Stock(St_Num)
            Reverse,Falling,Rising,list_stock = Analyze_Stock(St_Num)
            if Reverse == True:
                text = str1 + '  [{:s}] 價:{:s}\n'.format(St_Name,list_stock[len(list_stock)-1][6])
            elif Falling == True:
                text = str2 + '  [{:s}] 價:{:s}\n'.format(St_Name,list_stock[len(list_stock)-1][6])
            elif Rising == True:
                text = str3 + '  [{:s}] 價:{:s}\n'.format(St_Name,list_stock[len(list_stock)-1][6])
            else :
                text = str4 + '  [{:s}] 價:{:s}\n'.format(St_Name,list_stock[len(list_stock)-1][6])
            print(text)
            return

    for St_Num in St_Num_List:
        St_Name = St_Name_List['{:04d}'.format(St_Num)]
        Update_Stock(St_Num)
        Reverse,Falling,Rising,list_stock = Analyze_Stock(St_Num)
        if Reverse == True:
            str1 = str1 + '  [{:s}] 價:{:s}\n'.format(St_Name,list_stock[len(list_stock)-1][6])
        elif Falling == True:
            str2 = str2 + '  [{:s}] 價:{:s}\n'.format(St_Name,list_stock[len(list_stock)-1][6])
        elif Rising == True:
            str3 = str3 + '  [{:s}] 價:{:s}\n'.format(St_Name,list_stock[len(list_stock)-1][6])
        else :
            str4 = str4 + '  [{:s}] 價:{:s}\n'.format(St_Name,list_stock[len(list_stock)-1][6])

    if '買' in msg:
        text = str1 + str2
    elif '全' in msg:
        text = str1 + str2 + str3 + str4

    print(text)

St_Name_List = {'2317':"鴻海",'1101':"台泥",'2882':"國泰金",'1102':"亞泥",'2412':"中華電",
                '3045':"台灣大",'4904':"遠傳",'2330':"台積電",'2357':"華碩",'2354':"鴻準",
                '2382':"廣達",'2356':"英業達",'1301':"台塑",'1303':"南亞",'1326':"台化",
                '2308':"台達電",'2886':"兆豐",'4938':"和碩",'9945':"潤泰新",'2881':"富邦金",
                '1216':"統一",'9904':"寶成",'2105':"正新",'2324':"仁寶",'2002':"中鋼",
                '1210':"大成",'1310':"台苯",'2409':"友達",'2301':"光寶科"
                }
St_Num_List = [2317,1101,2882,1102,2412,3045,4904,2330,2357,2354,2382,2356,1301,1303,1326,2308,4938,2886,9945,2881,1216,9904,2105,2324,2002,1210,1310,2409,2301]

ts = time.time()
now_date = datetime.fromtimestamp(ts).strftime('%Y-%m-%d').split('-')
now_time = datetime.fromtimestamp(ts).strftime('%H:%M:%S').split(':')
print(now_date,now_time)
now_y,now_m,now_d = int(now_date[0])-1911,now_date[1],now_date[2]

if int(now_time[0]) < 14: #只能看前一天資料
    now_d = int(now_d) - 1

now_ch_date = '{:d}/{:02d}/{:02d}'.format(int(now_y),int(now_m),int(now_d))

#while True:
arg = '全'
#arg = input('please input : ')
if arg:
    app_stock(arg)
#input('Continue...')

