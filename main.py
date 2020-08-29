#可用引脚0,2,4,5,9,10,12,13,14,15,18,19,21,22,23,26,27,31,32,33
#26引脚用于dht模块，12,13用于声波接收模块,5,18,19,21,27,32用于继电器控制,22.23用于屏幕
import socket
import network
import urequests
import time
import machine
from machine import UART,RTC,Pin,I2C
import dht
i2c = I2C(scl=Pin(22), sda=Pin(23))
from ssd1306 import SSD1306_I2C
import _thread
rtc=RTC()
radar=UART(2,9600,rx=12,tx=13,timeout=10)
rad=Pin(13,Pin.OUT)
sta_if = network.WLAN(network.STA_IF)
def file_read(file_name):#读文件函数
    c_file=open(file_name,'r')
    c_line=c_file.readlines()
    c_file.close()
    return c_line
def push():#推送函数
    title = "GongShui_Yikaiqi!!!"
    content='text='+title+str(rtc.datetime())
    url="https://sc.ftqq.com/SCU90603T583ea1605085b478aa21af6d5a9a4d515e76e4ae3204a.send?%s"%content
    r=urequests.get(url)
    r.close()
def do_connect(ssid,pwd):#连接网络的函数
    sta_if.active(False)
    sta_if.active(True)
    if not sta_if.isconnected():#判断是否连接
            sta_if.connect(ssid,pwd)#ssid:WIFI名称 pwd:WIFI 密码
            while not sta_if.isconnected():
                pass
    if sta_if.isconnected():
        print('Ip Adress:'+sta_if.ifconfig()[0])
def get_net_time():#获取网络时间的函数
    url='http://apps.game.qq.com/CommArticle/app/reg/gdate.php'
    rtctime=rtc.datetime()
    nettime=urequests.get(url).text
    netdata=nettime.split("'")[1].split(' ')
    getdate=netdata[0].split('-')
    gettime=netdata[1].split(':')
    rtc.datetime((eval(getdate[0]),eval(getdate[1]),eval(getdate[2]),rtctime[3],eval(gettime[0]),eval(gettime[1]),eval(gettime[2]),0))
relay=[Pin(5,Pin.OUT),Pin(18,Pin.OUT),Pin(19,Pin.OUT),Pin(21,Pin.OUT),Pin(27,Pin.OUT)]
s = socket.socket()#创建socket对象
s.settimeout(0.5)
d = dht.DHT11(machine.Pin(26))
rad_dis=8000
log_data=file_read('logdata.txt')[0].split(',')
con_data_global=file_read('condata.txt')[0].split(',')
def out_change(con_num):
    if(len(con_num)==1):
        if(con_num=='0'):
            return '关闭'
        elif(con_num=='1'):
            return '开启'
    else:
        if(con_num[0]=='1'):
            return '定时'+con_num[1:]
        elif(con_num[0]=='2'):
            return '延时'+con_num[1:]
        elif(con_num[0]=='3'):
            return '倒计时'+con_num[1:]
        elif(con_num[0]=='4'):
            return '间歇'+con_num[1:]
        elif(con_num[0]=='5'):
            if(con_num[1]=='0'):
                return '温度触发'+con_num[1:]
            elif(con_num[1]=='1'):
                return '液位触发'+con_num[1:]
        elif(con_num[0]=='6'):
            return '双组定时器'+con_num[1:]
def html_pro(html):#处理网页中可自定义内容的函数
    html=html.replace('输出一',log_data[7]).replace('输出二',log_data[8]).replace('输出三',log_data[9]).replace('输出四',log_data[10]).replace('输出五',log_data[11])
    return html
def data_html_pro(html):
    time_now=rtc.datetime()
    html_spl=html.split('|')
    html_rep=html_spl[0]+str(time_now[0])+html_spl[1]+str(time_now[1])+html_spl[2]+str(time_now[2])+html_spl[3]+str(time_now[4])+html_spl[4]+str(time_now[5])+html_spl[5]+str(time_now[6])+html_spl[6]+str(d.temperature())+html_spl[7]+str(d.humidity())+html_spl[8]+'-'+html_spl[9]+'-'+html_spl[10]+out_change(con_data_global[0])+html_spl[11]+out_change(con_data_global[1])+html_spl[12]+out_change(con_data_global[2])+html_spl[13]+out_change(con_data_global[3])+html_spl[14]+out_change(con_data_global[4])+html_spl[15]
    return html_rep
def html_data(req_html):
    main_html= """<!DOCTYPE html>
    <html>
        <head>
            <title>农易终端</title>
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <style type="text/css">
                h2
                {
                    margin-top:4%;
                    margin-bottom:40px;
                }
            </style>
        </head>
        <body bgcolor="#C7EDCC">
        <center>
            <h1>农易设备控制终端</h1>
            <form action="/" method="get" accept-charset="utf-8">
    </table>

                <p>输出选择：
                <select name='outselect'>
                <option value ="out0">输出一</option>
                <option value ="out1">输出二</option>
                <option value ="out2">输出三</option>
                <option value ="out3">输出四</option>
                <option value ="out4">输出五</option>
                </select>
                </p>
                <p>模式选择：
                <select name='modeselect'>
                <option value ="diron">直接开启</option>
                <option value ="dirof">直接关闭</option>
                <option value ="clear">清除设置</option>
                <option value ="timer">定时模式</option>
                <option value ="count">计时模式</option>
                <option value ="delay">延时模式</option>
                <option value ="intel">间歇模式</option>
                <option value ="trige">触发模式</option>
                <option value ="doubl">双组定时器模式</option>
                </select>
                </p>
                <p>代码：<input type="text" name='concode' placeholder="输入控制代码,选填"></p>
                <p><input type="submit" name="mainsubmit" value="提交数据"  style="width:100px;height:50px;border-radius:15px;background: #06F421">&nbsp;&nbsp;&nbsp;&nbsp;<input type="submit" name="datamain" value="查看数据"style="width:100px;height:50px;border-radius:15px;background: #F2E116"></p>
        </form>
        </center>
    <h2>终端使用说明：</h2>
    <li>终端控制五组继电器，每次设置只能设置其中一组，五组输出的使用完全独立</li>
    <li>清除设置用于删除当前继电器的所有设置并将其设置为常闭</li>
    <li>当前页面显示的时间和温度是打开页面时系统中的时间和温度，由于页面是静态页面，所以数据不会刷新，可以点击刷新按钮刷新</li>
    <li>使用当前页面时，先在下拉框中选择输出，然后选择模式，在模式选择中，你可以直接开启或者关闭当前输出</li>
    <li>选择直接开启或关闭后，直接点击提交按钮即可。继电器若无设置，则切换为常开或常闭；若继电器有设置，则保留设置但切换状态</li>
    <li>提交按钮下方数字为五组继电器的控制代码，设置完成之后重新打开页面可以查看继电器设置情况</li>
    <li>设置完成之后请关闭页面清除浏览器进程，部分浏览器会自动刷新，重复提交数据可能对系统正常工作造成影响</li>
    <li>选择其他模式后，若熟知控制代码，那么可以在文本框中输入控制代码；若对代码规则较陌生，可选择不填，点击提交,将跳转至选择模式的设置页面，该页面会引导填写控制代码</li>
        </body>
    <h4>参考链接：</h4>
    <a href="https://zgny.com.cn/">中国农业网</a>&nbsp;<a href="https://www.chinabreed.com/">中国养殖网</a>&nbsp;<a href="http://www.xn121.com/">中国兴农网</a>&nbsp;<a href="http://www.chinafarming.com/">中国畜牧网</a>&nbsp;<a href="http://www.yangji.com/">养鸡网</a>
    <h5>联系作者：</h5>
    QQ：480437094 
    邮箱：480437094@qq.com 
    手机：18595752402 
    微信：Yob0402
    </html>
    """
    timer_html= """<!DOCTYPE html>
    <html>
        <head>
            <title>农易终端</title>
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <style type="text/css">
                h2
                {
                    margin-top:4%;
                    margin-bottom:40px;
                }
            </style>
        </head>
        <body bgcolor="#C7EDCC">
        <center>
            <h1>农易设备控制终端</h1>
            <h2>定时模式设置页面</h2>
            <form action="/" method="get" accept-charset="utf-8">
                <p>输出选择：
                <select name='outselect'>
                <option value ="out0">输出一</option>
                <option value ="out1">输出二</option>
                <option value ="out2">输出三</option>
                <option value ="out3">输出四</option>
                <option value ="out4">输出五</option>          
                </select>
                </p>
                <p>开始时间：<input type="time" name='statime' placeholder="开启时间"></p>
                <p>结束时间：<input type="time" name='endtime' placeholder="关闭时间"></p>
            <p><input type="submit" name='timermodesubmit' style="width:100px;height:50px;border-radius:15px;background: #06F421"/></p>
            </form>
        </center>
            <h3>定时模式设置说明</h3>
    <li>设置开始时间与结束时间即可，使用二十四小时制</li>
    <li>时间设置举例：上午八点工作到晚上十一点半，开始时间08:00，结束时间23:30</li>
    <li>当时间到达开始时间且秒数为零时，继电器接通；当时间到达结束时间且秒数为零时，继电器关闭</li>
    <li>定时模式为到时触发，开始时间可以比结束时间靠后，这样的结果是到第二天关闭</li>
    <li>在主界面输入控制代码设置定时器时，需要输入八位数：开始小时、开始分钟、结束小时和结束分钟，每项两位共八位，效果与当前页设置相同</li>
    <li>注意：系统检测到当前设置时间与系统时间一致才会开启，如果设置之后需要立刻开启，请到主界面将当前继电器打开，这个操作不会清空继电器设置</li>
        </body>
    </html>
    """
    count_html= """<!DOCTYPE html>
    <html>
        <head>
            <title>农易终端</title>
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <style type="text/css">
                h2
                {
                    margin-top:4%;
                    margin-bottom:40px;
                }
            </style>
        </head>
        <body bgcolor="#C7EDCC">
        <center>
            <h1>农易设备控制终端</h1>
            <h2>计时模式设置页面</h2>
            <form action="/" method="get" accept-charset="utf-8">
            <p>输出选择：
                <select name='outselect'>
                <option value ="out0">输出一</option>
                <option value ="out1">输出二</option>
                <option value ="out2">输出三</option>
                <option value ="out3">输出四</option>
                <option value ="out4">输出五</option>
                </select>
                </p>
                <p>计时时间：<input type="range" name='counttime' min="1" max="60"></p>
            <p><input type="submit" name='countmodesubmit'style="width:100px;height:50px;border-radius:15px;background: #06F421"/></p>
            </form>
        </center>
            <h3>定时器设置说明</h3>
    <li>滑动滑块设置计时时长即可，提交后对应继电器立刻打开，计时到设置时长后关闭</li>
    <li>计时模式精确到分钟，最短延时1分钟，最长延时60分钟，长于60分钟的请设置延时模式</li>
    <li>设置计时模式后，系统会自动计算结束时间并存储，实际上计时模式是60分钟内的延时</li>
    <li>在主界面设置计时模式，只需输入两位数分钟即可</li>
        </body>
    </html>
    """
    delay_html= """<!DOCTYPE html>
    <html>
        <head>
            <title>农易终端</title>
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <style type="text/css">
                h2
                {
                    margin-top:4%;
                    margin-bottom:40px;
                }
            </style>
        </head>
        <body bgcolor="#C7EDCC">
        <center>
            <h1>农易设备控制终端</h1>
            <h2>延时模式设置页面</h2>
            <form action="/" method="get" accept-charset="utf-8">
            <p>输出选择：
                <select name='outselect'>
                <option value ="out0">输出一</option>
                <option value ="out1">输出二</option>
                <option value ="out2">输出三</option>
                <option value ="out3">输出四</option>
                <option value ="out4">输出五</option>          
                </select>
                </p>
                <p>结束时间：<input type="time" name='endtime' placeholder="开启到该时间结束"></p>
            <p><input type="submit" name='delaymodesubmit'style="width:100px;height:50px;border-radius:15px;background: #06F421"/></p>
            </form>
        </center>
            <h3>延时模式设置说明</h3>
    <li>设置终止时间即可，使用二十四小时制</li>
    <li>设置延时模式后，对应继电器立刻开启，当到达终止时间的零秒时，系统关闭，继电器变为常闭状态</li>
    <li>延时模式举例：从现在开启到十一点结束，设置结束时间11:00</li>
    <li>如果设置的延时已经晚于当前时间，则继电器会开启到第二天对应时刻后关闭</li>
    <li>在主界面输入控制代码延时模式，只需输入终止时间即可，位数为四位数：终止小时、终止分钟各两位</li>
        </body>
    </html>
    """
    intel_html= """<!DOCTYPE html>
    <html>
        <head>
            <title>农易终端</title>
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <style type="text/css">
                h2
                {
                    margin-top:4%;
                    margin-bottom:40px;
                }
            </style>
        </head>
        <body bgcolor="#C7EDCC">
        <center>
            <h1>农易设备控制终端</h1>
            <h2>间歇模式设置页面</h2>
            <form action="/" method="get" accept-charset="utf-8">
            <p>输出选择：
                <select name='outselect'>
                <option value ="out0">输出一</option>
                <option value ="out1">输出二</option>
                <option value ="out2">输出三</option>
                <option value ="out3">输出四</option>
                <option value ="out4">输出五</option>          
                </select>
                </p>
                <p>间隔时间：<input type="number" name="looptime" placeholder="循环间隔时间"></p>
                <p>工作时间：<input type="number" name="worktime" placeholder="循环工作时间"></p>
            <p><input type="submit" name='intelmodesubmit'style="width:100px;height:50px;border-radius:15px;background: #06F421"/></p>
            </form>
        </center>
            <h3>间歇模式设置说明</h3>
    <li>设置周期时间与工作时间即可</li>
    <li>间隔时间是两次工作的间隔时间，例如每30分钟工作10分钟，则间隔时间为20分钟</li>
    <li>时间只取决于分钟，两次工作的间隔时间必须小于60，否则继电器将不会工作</li>
    <li>间歇时间的工作原理是用当前分钟数除以周期时间，将余数与间隔时间进行比较，当余数等于间隔时间时，继电器开启，余数为0，继电器关闭</li>
    <li>取模运算的好处是减小计算量，对所有周期都支持，缺点是当设置的周期不是典型值，例如周期为7分钟，每小时的最后一个周期（53--60）不足七分钟，可能会造成工作时间短缺，因此推荐设置周期时间时尽量选择能够被60整除的数</li>
    <li>在主界面输入控制代码间歇模式，输入周期时间与工作时间即可，位数为四位数：周期时间与工作时间各两位，例如0802为每间隔8分钟工作两分钟</li>
        </body>
    </html>
    """
    trige_html= """<!DOCTYPE html>
    <html>
        <head>
            <title>农易终端</title>
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <style type="text/css">
                h2
                {
                    margin-top:4%;
                    margin-bottom:40px;
                }
            </style>
        </head>
        <body bgcolor="#C7EDCC">
        <center>
            <h1>农易设备控制终端</h1>
            <h2>触发模式设置页面</h2>
            <form action="/" method="get" accept-charset="utf-8">
            <p>输出选择：
                <select name='outselect'>
                <option value ="out0">输出一</option>
                <option value ="out1">输出二</option>
                <option value ="out2">输出三</option>
                <option value ="out3">输出四</option>
                <option value ="out4">输出五</option> 
                </select>
                </p>
                <p>触发条件：<select name="trigger">
                    <option value="0">温度控制</option>
                    <option value="1">液位控制</option>
                    <option value="2">光照控制</option>
                    </select></p>
                <p>触发下限：<input type="text" name="trigsub" placeholder="大于下限开启"></p>
                <p>触发上限：<input type="number" name="trigtop" placeholder="小于上限结束"></p>
            <p><input type="submit" name='trigemodesubmit'style="width:100px;height:50px;border-radius:15px;background: #06F421"/></p>
            </form>
        </center>
            <h3>触发模式设置说明</h3>
    <li>设置触发方式与触发上下限</li>
    <li>触发模式目前只支持板子带有的温度、湿度以及液位，也可外接其他变送器进行控制，支持ADC、UART以及IIC通信的变送器</li>
    <li>当传感器数值高于触发下限时，继电器工作，当传感器数值高于出发上限时，继电器关闭，请合理设置上下限数值</li>
    <li>触发模式举例：温控设置：高于30摄氏度开，低于25摄氏度关，则上限30下限25</li>
    <li>温度传感器使用DHT11传感器，传感器温度精度为±2℃，数据可能存在误差，这是难以避免的，因此建议触发上下限之间留有一定跨度</li>
    <li>液位控制采用倒车雷达加收发模块，倒车雷达是防水的，不建议浸泡在水中，因此推荐在设置液位时与传感器保留一定距离</li>
    <li>在主界面设置触发模式，需要在上下限之前加触发方式，温度控制加数字0，液位控制加数字1；此外设置温度上下限时，精确到整数，单位为摄氏度；液位的单位为毫米，需要输入四位数字，不够的请在数字前添加零</li>
        </body>
    </html>
    """
    doubl_html= """<!DOCTYPE html>
    <html>
        <head>
            <title>农易终端</title>
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <style type="text/css">
                h2
                {
                    margin-top:4%;
                    margin-bottom:40px;
                }
            </style>
        </head>
        <body bgcolor="#C7EDCC">
        <center>
            <h1>农易设备控制终端</h1>
            <h2>双组定时模式设置页面</h2>
            <form action="/" method="get" accept-charset="utf-8">
                <p>输出选择：
                <select name='outselect'>
                <option value ="out0">输出一</option>
                <option value ="out1">输出二</option>
                <option value ="out2">输出三</option>
                <option value ="out3">输出四</option>
                <option value ="out4">输出五</option>        
                </select>
                </p>
                <p>第一组开始时间：<input type="time" name='statime1' ></p>
                <p>第一组结束时间：<input type="time" name='endtime1' ></p>
                <p>第二组开始时间：<input type="time" name='statime2' ></p>
                <p>第二组结束时间：<input type="time" name='endtime2' ></p>
            <p><input type="submit" name='doublmodesubmit'style="width:100px;height:50px;border-radius:15px;background: #06F421"/></p>
            </form>
        </center>
            <h3>双组定时模式设置说明</h3>
    <li>双组定时模式用于每天需要在两个固定时间段工作的输出</li>
    <li>两组定时器的时间重叠可能导致工作异常</li>
    <li>在主界面输入双组定时器的代码，需要输入八位数据，即两组定时的起止</li>
        </body>
    </html>
    """
    simp_html="""<!DOCTYPE html>
    <html>
        <head>
            <title>农易简端</title>
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <style type="text/css">
                h2
                {
                    margin-top:4%;
                    margin-bottom:40px;
                }
            </style>
        </head>
        <body bgcolor="#C7EDCC">
        <center>
            <h1>农易简端页面</h1>
            <form action="/" method="get" accept-charset="utf-8">
                <p><input type='submit' name="simpopenout0" value="开启输出一" style="width: 100px; height:100px; border-radius:50px;background:chartreuse"/>&nbsp;&nbsp;&nbsp;&nbsp;<input type='submit' name="simpcloseout0" value="关闭输出一" style="width: 100px; height:100px; border-radius:50px;background-color: crimson">&nbsp;&nbsp;&nbsp;&nbsp;<input type='submit' name="simpbut0" value="按钮一" style="width: 100px; height:100px; border-radius:50px;background-color:gold"/></p>
                <p><input type='submit' name="simpopenout1" value="开启输出二" style="width: 100px; height:100px; border-radius:50px;background:chartreuse"/>&nbsp;&nbsp;&nbsp;&nbsp;<input type='submit' name="simpcloseout1" value="关闭输出二" style="width: 100px; height:100px; border-radius:50px;background-color: crimson">&nbsp;&nbsp;&nbsp;&nbsp;<input type='submit' name="simpbut1" value="按钮二" style="width: 100px; height:100px; border-radius:50px;background-color:gold"/></p>
                <p><input type='submit' name="simpopenout2" value="开启输出三" style="width: 100px; height:100px; border-radius:50px;background:chartreuse"/>&nbsp;&nbsp;&nbsp;&nbsp;<input type='submit' name="simpcloseout2" value="关闭输出三" style="width: 100px; height:100px; border-radius:50px;background-color: crimson">&nbsp;&nbsp;&nbsp;&nbsp;<input type='submit' name="simpbut2" value="按钮三" style="width: 100px; height:100px; border-radius:50px;background-color:gold"/></p>
                <p><input type='submit' name="simpopenout3" value="开启输出四" style="width: 100px; height:100px; border-radius:50px;background:chartreuse"/>&nbsp;&nbsp;&nbsp;&nbsp;<input type='submit' name="simpcloseout3" value="关闭输出四" style="width: 100px; height:100px; border-radius:50px;background-color: crimson">&nbsp;&nbsp;&nbsp;&nbsp;<input type='submit' name="simpbut3" value="按钮四" style="width: 100px; height:100px; border-radius:50px;background-color:gold"/></p>
                <p><input type='submit' name="simpopenout4" value="开启输出五" style="width: 100px; height:100px; border-radius:50px;background:chartreuse"/>&nbsp;&nbsp;&nbsp;&nbsp;<input type='submit' name="simpcloseout4" value="关闭输出五" style="width: 100px; height:100px; border-radius:50px;background-color: crimson">&nbsp;&nbsp;&nbsp;&nbsp;<input type='submit' name="simpbut4" value="按钮五" style="width: 100px; height:100px; border-radius:50px;background-color:gold"/></p>
        </form>
        </center>
        </body>
    </html>
    """
    login_html = """<!DOCTYPE html>
    <html>
        <head>
            <title>农易终端控制平台</title>
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <style type="text/css">
                h2
                {
                    margin-top:4%;
                    margin-bottom:40px;
                }
            </style>
        </head>
        <body bgcolor="#C7EDCC">
            <center>
            <h2>欢迎使用农易设备！</h2>
                <form action="/" method="get" accept-charset="utf-8">
                    <p><input type="Submit" value="普通界面" name="expermain" style="width: 100px; height:100px; border-radius:50px;background-color: coral"/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="Submit" value="简单界面" name="simplemain" style="width: 100px; height:100px; border-radius:50px;background-color: chartreuse"/><p>
                    <p><input type="Submit" value="设置界面" name="initmain" style="width: 100px; height:100px; border-radius:50px;background-color:goldenrod"/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="Submit" value="帮助界面" name="helpmain" style="width: 100px; height:100px; border-radius:50px;background-color:goldenrod"/></p>
                    <p><input type="Submit" value="数据" name="datamain" style="width: 100px; height:100px; border-radius:50px;background-color:goldenrod"/></p>
                </form>
            </center>
        </body>
    </html>
    """
    data_html=""" <!DOCTYPE html>
    <html>
        <head>
            <title>农易终端</title>
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <style type="text/css">
                h2
                {
                    margin-top:4%;
                    margin-bottom:40px;
                }
            </style> 
        </head>
        <body bgcolor="#C7EDCC">
        <center>
            <h1>农易设备数据采集</h1>
			<p>|年|月|日</p>
			<p>|：|：|</p>
			<p>当前温度： | ℃</p>
			<p>当前湿度： | %</p>
			<p>当前光强：|</p>
			<p>当前液位：|</p>
			<p>输出一状态：|</p>
			<p>输出二状态：|</p>
			<p>输出三状态：|</p>
			<p>输出四状态：|</p>
			<p>输出五状态：|</p>
			<form action="/" method="get" accept-charset="utf-8">
            <p><input type="submit" value="点击按钮返回" name='datasubmit' style="height: 50px;width: 100px;border-radius: 25px;background-color: beige">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="submit" value="点击按钮刷新" name='refre' style="height: 50px;width: 100px;border-radius: 25px;background-color:aqua"></p>
            </form>
        </center>
    </html>
    """
    error_html="""<!DOCTYPE html>
    <html>
        <head>
            <title>农易终端</title>
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <style type="text/css">
                h2
                {
                    margin-top:4%;
                    margin-bottom:40px;
                }
            </style> 
        </head>
        <body bgcolor="#C7EDCC">
        <center>
            <h1>农易设备使用帮助</h1>
        <form action="/" method="get" accept-charset="utf-8">
            <p><input type="submit" value="点击按钮返回" name='errormodesubmit' style="height: 50px;width: 100px;border-radius: 25px;background-color: beige"></p>
            </form>
        </center>
        <h4>主界面说明：</h4>
        <li>打开主界面后，选择普通界面可以详细设置设备的工作方式，包含控制器的所有功能。</li>
        <li>选择简单界面可以进入简单控制，类似控制器的遥控器，可以直接开启或关闭某组输出，有五个自定义按钮绑定常用功能后可快速开启。</li>
        <li>选择设置界面，可以设置常用的WiFi名称，设置五组输出的名字，也可以设置简单页面中的自定义按钮。</li>
        <h4>以下是控制终端的详细使用说明：</h4>
    <li>在主界面选择输出以及模式后，您可以选择填入控制代码或者直接提交，填入的控制代码必须与模式相对应。注意某些模式无需填入控制代码，包含：直接开启、直接关闭以及清除设置。</li>
    <li>“直接开启”和“直接关闭”选项都会立刻调整继电器当前状态。在继电器没有设置的情况下，继电器设置会调整至对应状态。但在继电器已经有有设置的情况下，选择这些选项提交后，继电器仍会尝试调整状态，但如果已有的设置与想要转换的状态有冲突，那么继电器还是会按照先前的设置工作，例如设置温度触发模式，已经达到触发条件后选择关闭是无用的，可以使用清除设置来关闭继电器。</li>
    <li>刷新页面的作用是在您设置继电器的工作状态之后，主界面下方继电器的工作状态并不会立刻切换，这是因为页面是静态的。但是如果您选择刷新页面，您可能会将先前提交的数据重新提交一遍，这可能会产生您预期之外的结果，因此刷新页面用于刷新继电器的状态，也可以用于刷新传感器读数。</li>
    <li>定时器模式用于每天需要开关固定时长的输出，例如灯光。时间到达设定的开始时间时继电器开启，到达结束时间时继电器关闭。由于继电器只在设定时间的整分动作，因此如果您设定的时间在开始时间之后，继电器不会立刻动作，您可以通过“直接开启”选项，调整至您希望的工作状态。</li>
    <li>计时模式用于需要临时工作一段时间的情况，例如临时打开照明或者临时打开风机，请注意计时模式和延时模式在工作结束后都会清除继电器设置，这意味着您可能需要重新调整设置。如果继电器先前工作在定时模式，那么推荐您使用直接开启给或者直接关闭的方式。计时模式最长工作一小时。</li>
    <li>延时模式用于需要临时工作较长时间的情况，例如气温忽然升高时的风机工作。延时模式最长可以工作二十四小时，即如果您将时间设置到当前时刻，继电器会工作到第二天。</li>
    <li>触发模式的工作原理是用当前分钟除以周期时间，将其余数与间隔时间（间隔时间是周期时间与工作时间的差）相比较，等于间隔时间则继电器工作，等于零则继电器关闭。比如每三十分钟工作五分钟，则间隔时间是二十五分钟。如果现在是某小时的二十五分钟，二十五除以三十的余数为二十五，继电器开始工作。由于采用分钟作为标准，不考虑小时，因此工作周期最长为六十分钟。这种工作方式适用于风机通风换气，水帘间断供水等等。</li>
    <li>触发模式是高度实验性的，具有个性差别，目前拥有温度与液位控制两种模式。介于使用的从单片机功能强大，理论上支持所有IIC、UART，ADC/DAC等通信方式的传感器或变送器。</li>
    <h4>以下是终端设置参考：</h4>
    <li>在主界面输入定时模式与双组定时模式的控制代码，要注意小时不能大于23，分钟不能大于59，但是结束时间可以早于开始时间。例：上午八点到下午五点三十五分，控制代码是08001735（开始时间加终止时间）。</li>
    <li>在主界面输入计时模式的控制代码，需要注意计时的范围为1-60，并且输入必须为两位数，例：工作五分钟后关闭，控制代码为05。由于部分浏览器的“范围”输入不支持在拖动滑块的同时显示滑块当前代表的数值，因此计时模式用于模糊控制，若要精确控制分钟，推荐使用延时模式或在主界面输入倒计时时间。</li>
    <li>在主界面输入延时模式的控制代码，需要输入延时结束的时间，例：从现在起工作至下午八点四十，输入2040（终止时间加分钟）。延时模式使用后自动切换为常闭状态。</li>
    <li>在主界面输入间歇模式的控制代码，需要输入工作周期时间与每个周期的工作时间，目前支持设置的最大周期为60分钟。例：每半小时工作五分钟，需要输入控制代码2505（间隔时间加工作时间）</li>
    <li>在主界面输入触发模式的控制代码，目前支持温度触发与液位（距离触发）。温度触发模式需要在温度上下限前加数字0，例：温度大于25摄氏度开启，小于20摄氏度关闭，输入02520（触发方式加触发上限加触发下限）。液位控制需要在液位上下限前加数字1，且距离必须是四位数，单位为毫米，例如位置大于800毫米开启，小于400毫米关闭，输入108000400。</li>
    </html>
    """
    init_html="""<!DOCTYPE html>
    <html>
        <head>
            <title>农易终端</title>
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <style type="text/css">
                h2
                {
                    margin-top:4%;
                    margin-bottom:40px;
                }
            </style>
        </head>
        <body bgcolor="#C7EDCC">
        <center>
            <h1>农易设备设置界面</h1>
            <h2>请在这里设置您的设备</h2>
            <form action="/" method="get" accept-charset="utf-8">
            <p>Wifi名称:<input type="text" name="ssidname" placeholder='Wifi名称，不支持中文字符'/></p>
            <p>Wifi密码:<input type="text" name="ssidcode" placeholder='Wifi密码，开放网络可不填'/></p></p>
            <p>按钮一功能:<input type="text" name="but0code" placeholder='输入按钮一的控制代码'/></p>
            <p>按钮二功能:<input type="text" name="but1code" placeholder='输入按钮二的控制代码'/></p>
            <p>按钮三功能:<input type="text" name="but2code" placeholder='输入按钮三的控制代码'/></p>
            <p>按钮四功能:<input type="text" name="but3code" placeholder='输入按钮四的控制代码'/></p>
            <p>按钮五功能:<input type="text" name="but4code" placeholder='输入按钮五的控制代码'/></p>
            <input type="submit" name='initsubmit' style="width:100px;height:50px;border-radius: 15px;background-color: blanchedalmond" />
        </form>
        </center>
    <li>WiFi账号与密码用于设置设备默认连接的WiFi，WiFi用于设备获取时间以及控制功能，在系统对时以及设置完成后可以关闭WiFi</li>
    <li>五组输出的名称可以自定义，可以定义为输出控制的设备名称，如“风机”、“灯光”或“湿帘”等</li>
    <li>如果要使用简端功能，需要设置五个按钮的名称和功能，设置功能需要使用控制代码，如果不熟悉控制代码，可以在一般登录后了解</li>
    </body>
    </html>
    """
    if(req_html=='main'):
        return html_pro(main_html)
    elif(req_html=='intel'):
        return html_pro(intel_html)
    elif(req_html=='init'):
        return init_html
    elif(req_html=='login'):
        return login_html
    elif(req_html=='simple'):
        return html_pro(simp_html)
    elif(req_html=='count'):
        return html_pro(count_html)
    elif(req_html=='doubl'):
        return html_pro(doubl_html)
    elif(req_html=='error'):
        return error_html
    elif(req_html=='trige'):
        return html_pro(trige_html)
    elif(req_html=='delay'):
        return html_pro(delay_html)
    elif(req_html=='timer'):
        return html_pro(timer_html)
    elif(req_html=='data'):
        return data_html_pro(data_html)
def relay_on(num):#直接按钮操作的打开继电器操作函数
    global con_data_global
    if con_data_global[num]=='0':#如果当前继电器的控制方式为常闭，则设置为常开
        con_data_global[num]='1'
    else:#如果当前继电器设置不是常开，则保留继电器设置，翻转继电器状态，如果当前继电器已经是关闭状态，不执行操作
        if(relay[num].value()==0):
            relay[num].on()
def relay_off(num):#关闭继电器的操作函数
    global con_data_global
    if con_data_global[num]=='1':#如果当前继电器的控制方式为常开，则设置为常闭
        con_data_global[num]='0'
    else:#如果当前继电器设置不是常开，则保留继电器设置，但是翻转继电器状态，如果当前继电器已经是关闭状态，不执行操作
        if(relay[num].value() ==1):
            relay[num].off()
def file_write(file_name,s):#写文件函数
    c_file=open(file_name,'w')
    c_file.write(str(s))
    c_file.close()
def error_inter(typenum,data):#当输入的控制代码有错误返回0，无误返回1
    if typenum==1:
        if(len(data) != 8):
            return 0
        elif(eval(data[0:2]>23 or eval(data[4:6])>23) or eval(data[2:4])>59  or  eval(data[6:8])>59):
            return 0
        else:
            return 1
    if typenum==2:
        if(len(data) !=4):
            return 0
        elif(eval(data[0:2])>23 or eval(data[2:4])>59):
            return 0
        else:
            return 1
    if typenum==3:
        if(len(data) >2):
            return 0
        elif(eval(data[0:])>60):
            return 0
        else:
            return 1
    if typenum==4:
        if(len(data) != 4):
            return 0
        elif(eval(data[0:2])-eval(data[2:4])>60 or eval(data[2:4])>60):
            return 0
        else:
            return 1
    if typenum==5:
        if(data[0]=='0'):
            if(len(data) != 5):
                return 0
            elif(eval(data[1:3])>60 or eval(data[3:5])>60):
                return 0
            else:
                return 1
        elif(data[0]=='1'):
            if(len(data)!= 9):
                return 0
            elif(eval(data[1:5])>8000 or eval(data[5:9])>8000):
                return 0
            else:
                return 1
        if typenum==6:
            if(len(data) != 16):
                return 0
            elif(eval(data[0:2])>23 or eval(data[4:6])>23 or eval(data[8:10])>23 or eval(data[12:14])>23 or eval(data[2:4])>59 or  eval(data[6:8])>59 or  eval(data[10:12])>59 or  eval(data[16:18])>59):
                return 0
        else:
            return 1
def req_pro(req_data):#处理收到的所有有用信息并返回应该显示的页面
    global con_data_global
    if req_data.find('expermain')>-1:
        return 'main'
    elif req_data.find('simplemain')>-1:#简单页面按钮
        return 'simple'
    elif req_data.find('initmain')>-1:#设置页面提交
        return 'init'
    elif req_data.find('helpmain')>-1:#帮助页面提交
        return 'error'
    elif req_data.find('datamain')>-1:#帮助页面提交
        return 'data'
    elif(req_data.find('refre')>-1):#刷新页面
        return 'data'
    elif(req_data.find('mainsubmit')>-1):#主界面提交
        req_data_spl=req_data.split('&')
        rec_spl=req_data.split('&')
        if(rec_spl[2][-1]=='='):#判断是否输入控制代码，如果没有输入控制代码，返回相应页面
            if(rec_spl[1].find('diron')>-1):
                out_num=eval(rec_spl[0][-1])
                relay_on(out_num)
            elif(rec_spl[1].find('dirof')>-1):
                out_num=eval(rec_spl[0][-1])
                relay_off(out_num)
            elif(rec_spl[1].find('clear')>-1):
                out_num=eval(rec_spl[0][-1])
                con_data_global[out_num]='0'
            else:
                if(req_data_spl[1].find('intel')>-1):
                    return 'intel'
                elif(req_data_spl[1].find('clear')>-1):
                    return 'delay'
                elif(req_data_spl[1].find('delay')>-1):
                    return 'delay'
                elif(req_data_spl[1].find('timer')>-1):
                    return 'timer'
                elif(req_data_spl[1].find('count')>-1):
                    return 'count'
                elif(req_data_spl[1].find('trige')>-1):
                    return 'trige'
                elif(req_data_spl[1].find('doubl')>-1):
                    return 'doubl'
            return 'main'
        else:
            concode=rec_spl[2].split('=')[1]
            con_num=eval(rec_spl[0][-1])
            if(rec_spl[1].find('timer')>-1):
                if(error_inter(1,concode)):
                    con_data_global[con_num]='1'+concode
                else:
                    return 'error'
            elif(rec_spl[1].find('delay')>-1):
                if(error_inter(2,concode)):
                    con_data_global[con_num]='2'+concode
                else:
                    return 'error'
            elif(rec_spl[1].find('count')>-1):
                if(error_inter(3,concode)):
                    con_data_global[con_num]='3'+concode
                else:
                    return 'error'
            elif(rec_spl[1].find('intel')>-1):
                if(error_inter(4,concode)):    
                    con_data_global[con_num]='4'+concode
                else:
                    return 'error'
            elif(rec_spl[1].find('trige')>-1):
                if(error_inter(5,concode)):
                    con_data_global[con_num]='5'+concode
                else:
                    return 'error'
            elif(rec_spl[1].find('doubl')>-1):
                if(error_inter(6,concode)):
                    con_data_global[con_num]='6'+concode
                else:
                    return 'error'
            return 'login'
    elif(req_data.find('simpopenout')>-1):#简单界面提交开启
        con_data_global[eval(req_data[req_data.find('simpopenout')+11])]='1'
        print(req_data[req_data.find('simpopenout')+11])
        return 'simple'
    elif(req_data.find('simpcloseout')>-1):#简单界面提交关闭
        con_data_global[eval(req_data[req_data.find('simpcloseout')+12])]='0'
        return 'simple'
    elif(req_data.find('butcode')>-1):#简单界面点击按钮功能
        con_num=eval(req_data.split('butcode')[1][0])
        con_data_global[con_num]=log_data[2+con_num]
        return 'simple'
    elif(req_data.find('initsubmit')>-1):
        log_data_read=log_data
        for send_num in range(7):
            if(len(req_data.split('&')[send_num])>1 and req_data.split('&')[send_num][-1]!='='):
                log_data_read[send_num]=req_data.split('&')[send_num].split('=')[-1]
        file_write('logdata.txt',','.join(log_data_read))
        return 'login'
    else:
        rec_spl=req_data.split('&')
        get_mode=rec_spl[-1][0:5]
        out_num=eval(rec_spl[0][-1])
        print(get_mode)
        if(get_mode=='timer'):
            if(rec_spl[1][-1] !='=' and rec_spl[2][-1] !='='):
                begin_time=rec_spl[1].split('=')[1].replace('%3a','')
                end_time=rec_spl[2].split('=')[1].replace('%3a','')
                print(begin_time+end_time)
                con_data_global[out_num]='1'+begin_time+end_time
        elif(get_mode=='count'):
            count_time=rec_spl[1].split('=')[1]
            print('count'+count_time)
            fill_count=str('%02d'%eval(count_time))
            if(error_inter(2,fill_count)):
                con_data_global[out_num]=fill_count
            else:
                return 'error'
        elif(get_mode=='clear'):
            con_data_global[out_num]='0'
            return 'main'
        elif(get_mode=='delay'):
            end_time=rec_spl[1].split('=')[1].replace('%3a','')
            print('endtime:'+end_time)
            con_data_global[out_num]='2'+end_time
        elif(get_mode=='intel'):
            loop_time=rec_spl[1].split('=')[1]
            work_time=rec_spl[2].split('=')[1]
            fill_loop=str('%02d'%eval(loop_time))
            fill_work=str('%02d'%eval(work_time))
            print('trigger'+fill_loop+fill_work)
            con_data_global[out_num]='4'+fill_loop+fill_work
        elif(get_mode=='trige'):
            trigger=rec_spl[1][-1]
            print(trigger)
            if(trigger=='0'):
                top_temp=rec_spl[2].split('=')[1]
                bot_temp=rec_spl[3].split('=')[1]
                fill_top=str('%02d'%eval(top_temp))
                fill_bot=str('%02d'%eval(bot_temp))
                print('trige'+fill_top+fill_bot)
                con_data_global[out_num]='50'+fill_top+fill_bot
            elif(trigger=='1'):
                top_lev=rec_spl[2].split('=')[1]
                bot_lev=rec_spl[3].split('=')[1]
                fill_top=str('%04d'%eval(top_lev))
                fill_bot=str('%04d'%eval(bot_lev))
                print('trige'+fill_top+fill_bot)
                con_data_global[out_num]='51'+fill_top+fill_bot
        elif(get_mode=='doubl'):
            begin_time1=rec_spl[1].split('=')[1].replace('%3a','')
            end_time1=rec_spl[2].split('=')[1].replace('%3a','')
            begin_time2=rec_spl[3].split('=')[1].replace('%3a','')
            end_time2=rec_spl[4].split('=')[1].replace('%3a','')
            con_data_global[out_num]='6'+begin_time1+end_time1+begin_time2+end_time2
        return 'main'
def main_send(res):#向客户端发送网页和读取返回值的函数
    client_s = res[0]
    client_addr = res[1]
    req =client_s.readline()
    while True:
        h = client_s.readline()
        if h == b"" or h == b"\r\n":
            break
        req+=(h.decode('utf-8'))
    req=req.decode('utf-8').split('\r\n')
    req_data=req[0].lstrip().rstrip().replace(' ','')
    if req_data.find('favicon.ico')>-1:
        client_s.close()
    else:
        if len(req_data)<=12:
            if(len(log_data[0])<1):
                s_data=html_data('init')
            else:
                s_data=html_data('login')
        else:
            req_data=req_data.replace('get/?','').replace('http/1.1','')
            print(req_data)
            ret_data=req_pro(req_data)
            print(ret_data)
            s_data=html_data(ret_data)
        print('-----------')
        client_s.send(s_data)
        client_s.close()
def relay_control_single(relay_num,relay_data):# 此函数判断单个继电器是否应该动作,有动作时返回该函数的返回值：返回0关闭继电器返回1：打开继电器
    global rad_dis
    time_now=rtc.datetime()#获取当前时间
    if(len(relay_data)==1):#若果是常开常闭控制，返回控制代码
        return eval(relay_data)
    elif(relay_data[0]=='1'):#开头为1定时模式
        begin_hour=eval(relay_data[1:3])
        begin_min=eval(relay_data[3:5])
        end_hour=eval(relay_data[5:7])
        end_min=eval(relay_data[7:9])
        if(time_now[4]==begin_hour and time_now[5]==begin_min and time_now[6]==0)or(time_now[4]==begin_hour and time_now[5]==begin_min and time_now[6]==1):
            return 1
        if(time_now[4]==end_hour and time_now[5]==end_min and time_now[6]==0)or(time_now[4]==end_hour and time_now[5]==end_min and time_now[6]==1):
            return 0
    if(relay_data[0]=='2'):#开头为2延时模式
        end_hour=eval(relay_data[1:3])
        end_min=eval(relay_data[3:5])
        if(time_now[4]==end_hour and time_now[5]==end_min and time_now[6]==0)or(time_now[4]==end_hour and time_now[5]==end_min and time_now[6]==1):
            con_data_global[relay_num]='0'
            return 0
        else:
            return 1
    if(relay_data[0]=='3'):#开头为3倒计时模式
        delay_min=eval(relay_data[1:3])
        end_min=delay_min+time_now[5]
        if end_min>=60:
            min_end=end_min%60
            hour_end=time_now[4]+1
        else:
            min_end=end_min
            hour_end=time_now[4]
        con_data_global[relay_num]='2'+'%02d'%hour_end+'%02d'%min_end
    if(relay_data[0]=='4'):#开头为4，间歇模式
        inte_time=eval(relay_data[1:3])
        work_time=eval(relay_data[3:5])
        loop_time=inte_time+work_time
        if(time_now[5]%loop_time==inte_time):
            return 1
        if(time_now[5]%loop_time==0):
            return 0
    if(relay_data[0]=='5'):#开头为5条件触发模式目前板子上支持的条件比较少0：温度触发模式，精度到整数摄氏度1：距离触发模式，精度到整数毫米
        if(relay_data[1]=='0'):
            begin_temp=eval(relay_data[2:4])
            end_temp=eval(relay_data[4:6])
            if(d.temperature()>=begin_temp):
                return 1
            if(d.temperature()<=end_temp):
                return 0
        elif(relay_data[1]=='1'):
            begin_lev=eval(relay_data[2:6])
            end_lev=eval(relay_data[6:10])
            if(rad_dis !=8000):
                if(rad_dis>=begin_lev):
                    return 1
                if(rad_dis<=end_lev):
                    return 0
    if(relay_data[0]=='6'):#双组定时器模式
        begin_hour1=eval(relay_data[1:3])
        begin_min1=eval(relay_data[3:5])
        end_hour1=eval(relay_data[5:7])
        end_min1=eval(relay_data[7:9])
        begin_hour2=eval(relay_data[9:11])
        begin_min2=eval(relay_data[11:13])
        end_hour2=eval(relay_data[13:15])
        end_min2=eval(relay_data[15:17])
        if(time_now[4]==begin_hour1 and time_now[5]==begin_min1 and time_now[6]==0):
            return 1
        if(time_now[4]==end_hour1 and time_now[5]==end_min1 and time_now[6]==0):
            return 0
        if(time_now[4]==begin_hour2 and time_now[5]==begin_min2 and time_now[6]==0):
            return 1
        if(time_now[4]==end_hour2 and time_now[5]==end_min2 and time_now[6]==0):
            return 0
def all_relay_con():#所有继电器的控制函数，需要调用单个继电器控制函数
    while True:
        try:
            d.measure()
        except:
            pass
        if(con_data_global != file_read('condata.txt')[0].split(',')):
            file_write('condata.txt',','.join(con_data_global))
        all_con_data=con_data_global    
        for i in range(5):
            con=relay_control_single(i,all_con_data[i])
            if(con != None):
                relay[i].value(con)
def main_try():#网络主循环
    while True:
        if not sta_if.isconnected():
            if(len(log_data[0])<1):
                try:
                    do_connect('农易','')#默认连接名为‘农易’的热点，设置后可以连接其他热点
                except:
                    pass
            else:
                try:
                    do_connect(log_data[0],log_data[1])
                except:
                    pass
        elif sta_if.isconnected():
            try:
                get_net_time()
                print(str(rtc.datetime()))
            except:
                pass
            ai = socket.getaddrinfo(str(sta_if.ifconfig()[0]), 80)
            addr = ai[0][-1]
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(addr)
            s.listen(5)
            while sta_if.isconnected():
                try:
                    res=s.accept()
                    main_send(res)
                except:
                    pass
def measure_try():
    if(len(i2c.scan())==0):
        while True:
            timenow=rtc.datetime()
            if(relay[1].value() and timenow[5]%2==0 and timenow[6]==0):
                push()
    else:
        oled = SSD1306_I2C(128, 64, i2c)
        while True:
            timenow=rtc.datetime()
            oled.fill(0)
            if not sta_if.isconnected():
                oled.text('Notconnected',0,0)
            else:
                oled.text(str(sta_if.ifconfig()[0]),0,0)
            oled.text('Date:'+str(timenow[0])+'-'+str(timenow[1])+'-'+str(timenow[2]),0,8)
            oled.text('Time:'+str(timenow[4])+':'+str(timenow[5])+':'+str(timenow[6]),0,16)
            oled.text('Temp:'+str(d.temperature()),0,24)
            oled.text('Humi:'+str(d.humidity()),0,32)
            oled.show()
            if(relay[1].value() and timenow[5]%2==0 and timenow[6]==0):
                push()
_thread.start_new_thread(main_try,())
_thread.start_new_thread(all_relay_con,())
_thread.start_new_thread(measure_try,())