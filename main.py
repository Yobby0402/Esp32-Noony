#��������0,2,4,5,9,10,12,13,14,15,18,19,21,22,23,26,27,31,32,33
#26��������dhtģ�飬12,13������������ģ��,5,18,19,21,27,32���ڼ̵�������,22.23������Ļ
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
def file_read(file_name):#���ļ�����
    c_file=open(file_name,'r')
    c_line=c_file.readlines()
    c_file.close()
    return c_line
def push():#���ͺ���
    title = "GongShui_Yikaiqi!!!"
    content='text='+title+str(rtc.datetime())
    url="https://sc.ftqq.com/SCU90603T583ea1605085b478aa21af6d5a9a4d515e76e4ae3204a.send?%s"%content
    r=urequests.get(url)
    r.close()
def do_connect(ssid,pwd):#��������ĺ���
    sta_if.active(False)
    sta_if.active(True)
    if not sta_if.isconnected():#�ж��Ƿ�����
            sta_if.connect(ssid,pwd)#ssid:WIFI���� pwd:WIFI ����
            while not sta_if.isconnected():
                pass
    if sta_if.isconnected():
        print('Ip Adress:'+sta_if.ifconfig()[0])
def get_net_time():#��ȡ����ʱ��ĺ���
    url='http://apps.game.qq.com/CommArticle/app/reg/gdate.php'
    rtctime=rtc.datetime()
    nettime=urequests.get(url).text
    netdata=nettime.split("'")[1].split(' ')
    getdate=netdata[0].split('-')
    gettime=netdata[1].split(':')
    rtc.datetime((eval(getdate[0]),eval(getdate[1]),eval(getdate[2]),rtctime[3],eval(gettime[0]),eval(gettime[1]),eval(gettime[2]),0))
relay=[Pin(5,Pin.OUT),Pin(18,Pin.OUT),Pin(19,Pin.OUT),Pin(21,Pin.OUT),Pin(27,Pin.OUT)]
s = socket.socket()#����socket����
s.settimeout(0.5)
d = dht.DHT11(machine.Pin(26))
rad_dis=8000
log_data=file_read('logdata.txt')[0].split(',')
con_data_global=file_read('condata.txt')[0].split(',')
def out_change(con_num):
    if(len(con_num)==1):
        if(con_num=='0'):
            return '�ر�'
        elif(con_num=='1'):
            return '����'
    else:
        if(con_num[0]=='1'):
            return '��ʱ'+con_num[1:]
        elif(con_num[0]=='2'):
            return '��ʱ'+con_num[1:]
        elif(con_num[0]=='3'):
            return '����ʱ'+con_num[1:]
        elif(con_num[0]=='4'):
            return '��Ъ'+con_num[1:]
        elif(con_num[0]=='5'):
            if(con_num[1]=='0'):
                return '�¶ȴ���'+con_num[1:]
            elif(con_num[1]=='1'):
                return 'Һλ����'+con_num[1:]
        elif(con_num[0]=='6'):
            return '˫�鶨ʱ��'+con_num[1:]
def html_pro(html):#������ҳ�п��Զ������ݵĺ���
    html=html.replace('���һ',log_data[7]).replace('�����',log_data[8]).replace('�����',log_data[9]).replace('�����',log_data[10]).replace('�����',log_data[11])
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
            <title>ũ���ն�</title>
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
            <h1>ũ���豸�����ն�</h1>
            <form action="/" method="get" accept-charset="utf-8">
    </table>

                <p>���ѡ��
                <select name='outselect'>
                <option value ="out0">���һ</option>
                <option value ="out1">�����</option>
                <option value ="out2">�����</option>
                <option value ="out3">�����</option>
                <option value ="out4">�����</option>
                </select>
                </p>
                <p>ģʽѡ��
                <select name='modeselect'>
                <option value ="diron">ֱ�ӿ���</option>
                <option value ="dirof">ֱ�ӹر�</option>
                <option value ="clear">�������</option>
                <option value ="timer">��ʱģʽ</option>
                <option value ="count">��ʱģʽ</option>
                <option value ="delay">��ʱģʽ</option>
                <option value ="intel">��Ъģʽ</option>
                <option value ="trige">����ģʽ</option>
                <option value ="doubl">˫�鶨ʱ��ģʽ</option>
                </select>
                </p>
                <p>���룺<input type="text" name='concode' placeholder="������ƴ���,ѡ��"></p>
                <p><input type="submit" name="mainsubmit" value="�ύ����"  style="width:100px;height:50px;border-radius:15px;background: #06F421">&nbsp;&nbsp;&nbsp;&nbsp;<input type="submit" name="datamain" value="�鿴����"style="width:100px;height:50px;border-radius:15px;background: #F2E116"></p>
        </form>
        </center>
    <h2>�ն�ʹ��˵����</h2>
    <li>�ն˿�������̵�����ÿ������ֻ����������һ�飬���������ʹ����ȫ����</li>
    <li>�����������ɾ����ǰ�̵������������ò���������Ϊ����</li>
    <li>��ǰҳ����ʾ��ʱ����¶��Ǵ�ҳ��ʱϵͳ�е�ʱ����¶ȣ�����ҳ���Ǿ�̬ҳ�棬�������ݲ���ˢ�£����Ե��ˢ�°�ťˢ��</li>
    <li>ʹ�õ�ǰҳ��ʱ��������������ѡ�������Ȼ��ѡ��ģʽ����ģʽѡ���У������ֱ�ӿ������߹رյ�ǰ���</li>
    <li>ѡ��ֱ�ӿ�����رպ�ֱ�ӵ���ύ��ť���ɡ��̵����������ã����л�Ϊ�����򳣱գ����̵��������ã��������õ��л�״̬</li>
    <li>�ύ��ť�·�����Ϊ����̵����Ŀ��ƴ��룬�������֮�����´�ҳ����Բ鿴�̵����������</li>
    <li>�������֮����ر�ҳ�������������̣�������������Զ�ˢ�£��ظ��ύ���ݿ��ܶ�ϵͳ�����������Ӱ��</li>
    <li>ѡ������ģʽ������֪���ƴ��룬��ô�������ı�����������ƴ��룻���Դ�������İ������ѡ�������ύ,����ת��ѡ��ģʽ������ҳ�棬��ҳ���������д���ƴ���</li>
        </body>
    <h4>�ο����ӣ�</h4>
    <a href="https://zgny.com.cn/">�й�ũҵ��</a>&nbsp;<a href="https://www.chinabreed.com/">�й���ֳ��</a>&nbsp;<a href="http://www.xn121.com/">�й���ũ��</a>&nbsp;<a href="http://www.chinafarming.com/">�й�������</a>&nbsp;<a href="http://www.yangji.com/">������</a>
    <h5>��ϵ���ߣ�</h5>
    QQ��480437094 
    ���䣺480437094@qq.com 
    �ֻ���18595752402 
    ΢�ţ�Yob0402
    </html>
    """
    timer_html= """<!DOCTYPE html>
    <html>
        <head>
            <title>ũ���ն�</title>
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
            <h1>ũ���豸�����ն�</h1>
            <h2>��ʱģʽ����ҳ��</h2>
            <form action="/" method="get" accept-charset="utf-8">
                <p>���ѡ��
                <select name='outselect'>
                <option value ="out0">���һ</option>
                <option value ="out1">�����</option>
                <option value ="out2">�����</option>
                <option value ="out3">�����</option>
                <option value ="out4">�����</option>          
                </select>
                </p>
                <p>��ʼʱ�䣺<input type="time" name='statime' placeholder="����ʱ��"></p>
                <p>����ʱ�䣺<input type="time" name='endtime' placeholder="�ر�ʱ��"></p>
            <p><input type="submit" name='timermodesubmit' style="width:100px;height:50px;border-radius:15px;background: #06F421"/></p>
            </form>
        </center>
            <h3>��ʱģʽ����˵��</h3>
    <li>���ÿ�ʼʱ�������ʱ�伴�ɣ�ʹ�ö�ʮ��Сʱ��</li>
    <li>ʱ�����þ���������˵㹤��������ʮһ��룬��ʼʱ��08:00������ʱ��23:30</li>
    <li>��ʱ�䵽�￪ʼʱ��������Ϊ��ʱ���̵�����ͨ����ʱ�䵽�����ʱ��������Ϊ��ʱ���̵����ر�</li>
    <li>��ʱģʽΪ��ʱ��������ʼʱ����ԱȽ���ʱ�俿�������Ľ���ǵ��ڶ���ر�</li>
    <li>��������������ƴ������ö�ʱ��ʱ����Ҫ�����λ������ʼСʱ����ʼ���ӡ�����Сʱ�ͽ������ӣ�ÿ����λ����λ��Ч���뵱ǰҳ������ͬ</li>
    <li>ע�⣺ϵͳ��⵽��ǰ����ʱ����ϵͳʱ��һ�²ŻῪ�����������֮����Ҫ���̿������뵽�����潫��ǰ�̵����򿪣��������������ռ̵�������</li>
        </body>
    </html>
    """
    count_html= """<!DOCTYPE html>
    <html>
        <head>
            <title>ũ���ն�</title>
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
            <h1>ũ���豸�����ն�</h1>
            <h2>��ʱģʽ����ҳ��</h2>
            <form action="/" method="get" accept-charset="utf-8">
            <p>���ѡ��
                <select name='outselect'>
                <option value ="out0">���һ</option>
                <option value ="out1">�����</option>
                <option value ="out2">�����</option>
                <option value ="out3">�����</option>
                <option value ="out4">�����</option>
                </select>
                </p>
                <p>��ʱʱ�䣺<input type="range" name='counttime' min="1" max="60"></p>
            <p><input type="submit" name='countmodesubmit'style="width:100px;height:50px;border-radius:15px;background: #06F421"/></p>
            </form>
        </center>
            <h3>��ʱ������˵��</h3>
    <li>�����������ü�ʱʱ�����ɣ��ύ���Ӧ�̵������̴򿪣���ʱ������ʱ����ر�</li>
    <li>��ʱģʽ��ȷ�����ӣ������ʱ1���ӣ����ʱ60���ӣ�����60���ӵ���������ʱģʽ</li>
    <li>���ü�ʱģʽ��ϵͳ���Զ��������ʱ�䲢�洢��ʵ���ϼ�ʱģʽ��60�����ڵ���ʱ</li>
    <li>�����������ü�ʱģʽ��ֻ��������λ�����Ӽ���</li>
        </body>
    </html>
    """
    delay_html= """<!DOCTYPE html>
    <html>
        <head>
            <title>ũ���ն�</title>
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
            <h1>ũ���豸�����ն�</h1>
            <h2>��ʱģʽ����ҳ��</h2>
            <form action="/" method="get" accept-charset="utf-8">
            <p>���ѡ��
                <select name='outselect'>
                <option value ="out0">���һ</option>
                <option value ="out1">�����</option>
                <option value ="out2">�����</option>
                <option value ="out3">�����</option>
                <option value ="out4">�����</option>          
                </select>
                </p>
                <p>����ʱ�䣺<input type="time" name='endtime' placeholder="��������ʱ�����"></p>
            <p><input type="submit" name='delaymodesubmit'style="width:100px;height:50px;border-radius:15px;background: #06F421"/></p>
            </form>
        </center>
            <h3>��ʱģʽ����˵��</h3>
    <li>������ֹʱ�伴�ɣ�ʹ�ö�ʮ��Сʱ��</li>
    <li>������ʱģʽ�󣬶�Ӧ�̵������̿�������������ֹʱ�������ʱ��ϵͳ�رգ��̵�����Ϊ����״̬</li>
    <li>��ʱģʽ�����������ڿ�����ʮһ����������ý���ʱ��11:00</li>
    <li>������õ���ʱ�Ѿ����ڵ�ǰʱ�䣬��̵����Ὺ�����ڶ����Ӧʱ�̺�ر�</li>
    <li>��������������ƴ�����ʱģʽ��ֻ��������ֹʱ�伴�ɣ�λ��Ϊ��λ������ֹСʱ����ֹ���Ӹ���λ</li>
        </body>
    </html>
    """
    intel_html= """<!DOCTYPE html>
    <html>
        <head>
            <title>ũ���ն�</title>
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
            <h1>ũ���豸�����ն�</h1>
            <h2>��Ъģʽ����ҳ��</h2>
            <form action="/" method="get" accept-charset="utf-8">
            <p>���ѡ��
                <select name='outselect'>
                <option value ="out0">���һ</option>
                <option value ="out1">�����</option>
                <option value ="out2">�����</option>
                <option value ="out3">�����</option>
                <option value ="out4">�����</option>          
                </select>
                </p>
                <p>���ʱ�䣺<input type="number" name="looptime" placeholder="ѭ�����ʱ��"></p>
                <p>����ʱ�䣺<input type="number" name="worktime" placeholder="ѭ������ʱ��"></p>
            <p><input type="submit" name='intelmodesubmit'style="width:100px;height:50px;border-radius:15px;background: #06F421"/></p>
            </form>
        </center>
            <h3>��Ъģʽ����˵��</h3>
    <li>��������ʱ���빤��ʱ�伴��</li>
    <li>���ʱ�������ι����ļ��ʱ�䣬����ÿ30���ӹ���10���ӣ�����ʱ��Ϊ20����</li>
    <li>ʱ��ֻȡ���ڷ��ӣ����ι����ļ��ʱ�����С��60������̵��������Ṥ��</li>
    <li>��Ъʱ��Ĺ���ԭ�����õ�ǰ��������������ʱ�䣬����������ʱ����бȽϣ����������ڼ��ʱ��ʱ���̵�������������Ϊ0���̵����ر�</li>
    <li>ȡģ����ĺô��Ǽ�С�����������������ڶ�֧�֣�ȱ���ǵ����õ����ڲ��ǵ���ֵ����������Ϊ7���ӣ�ÿСʱ�����һ�����ڣ�53--60�������߷��ӣ����ܻ���ɹ���ʱ���ȱ������Ƽ���������ʱ��ʱ����ѡ���ܹ���60��������</li>
    <li>��������������ƴ����Ъģʽ����������ʱ���빤��ʱ�伴�ɣ�λ��Ϊ��λ��������ʱ���빤��ʱ�����λ������0802Ϊÿ���8���ӹ���������</li>
        </body>
    </html>
    """
    trige_html= """<!DOCTYPE html>
    <html>
        <head>
            <title>ũ���ն�</title>
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
            <h1>ũ���豸�����ն�</h1>
            <h2>����ģʽ����ҳ��</h2>
            <form action="/" method="get" accept-charset="utf-8">
            <p>���ѡ��
                <select name='outselect'>
                <option value ="out0">���һ</option>
                <option value ="out1">�����</option>
                <option value ="out2">�����</option>
                <option value ="out3">�����</option>
                <option value ="out4">�����</option> 
                </select>
                </p>
                <p>����������<select name="trigger">
                    <option value="0">�¶ȿ���</option>
                    <option value="1">Һλ����</option>
                    <option value="2">���տ���</option>
                    </select></p>
                <p>�������ޣ�<input type="text" name="trigsub" placeholder="�������޿���"></p>
                <p>�������ޣ�<input type="number" name="trigtop" placeholder="С�����޽���"></p>
            <p><input type="submit" name='trigemodesubmit'style="width:100px;height:50px;border-radius:15px;background: #06F421"/></p>
            </form>
        </center>
            <h3>����ģʽ����˵��</h3>
    <li>���ô�����ʽ�봥��������</li>
    <li>����ģʽĿǰֻ֧�ְ��Ӵ��е��¶ȡ�ʪ���Լ�Һλ��Ҳ������������������п��ƣ�֧��ADC��UART�Լ�IICͨ�ŵı�����</li>
    <li>����������ֵ���ڴ�������ʱ���̵�������������������ֵ���ڳ�������ʱ���̵����رգ������������������ֵ</li>
    <li>����ģʽ�������¿����ã�����30���϶ȿ�������25���϶ȹأ�������30����25</li>
    <li>�¶ȴ�����ʹ��DHT11���������������¶Ⱦ���Ϊ��2�棬���ݿ��ܴ������������Ա���ģ���˽��鴥��������֮������һ�����</li>
    <li>Һλ���Ʋ��õ����״���շ�ģ�飬�����״��Ƿ�ˮ�ģ������������ˮ�У�����Ƽ�������Һλʱ�봫��������һ������</li>
    <li>�����������ô���ģʽ����Ҫ��������֮ǰ�Ӵ�����ʽ���¶ȿ��Ƽ�����0��Һλ���Ƽ�����1�����������¶�������ʱ����ȷ����������λΪ���϶ȣ�Һλ�ĵ�λΪ���ף���Ҫ������λ���֣���������������ǰ�����</li>
        </body>
    </html>
    """
    doubl_html= """<!DOCTYPE html>
    <html>
        <head>
            <title>ũ���ն�</title>
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
            <h1>ũ���豸�����ն�</h1>
            <h2>˫�鶨ʱģʽ����ҳ��</h2>
            <form action="/" method="get" accept-charset="utf-8">
                <p>���ѡ��
                <select name='outselect'>
                <option value ="out0">���һ</option>
                <option value ="out1">�����</option>
                <option value ="out2">�����</option>
                <option value ="out3">�����</option>
                <option value ="out4">�����</option>        
                </select>
                </p>
                <p>��һ�鿪ʼʱ�䣺<input type="time" name='statime1' ></p>
                <p>��һ�����ʱ�䣺<input type="time" name='endtime1' ></p>
                <p>�ڶ��鿪ʼʱ�䣺<input type="time" name='statime2' ></p>
                <p>�ڶ������ʱ�䣺<input type="time" name='endtime2' ></p>
            <p><input type="submit" name='doublmodesubmit'style="width:100px;height:50px;border-radius:15px;background: #06F421"/></p>
            </form>
        </center>
            <h3>˫�鶨ʱģʽ����˵��</h3>
    <li>˫�鶨ʱģʽ����ÿ����Ҫ�������̶�ʱ��ι��������</li>
    <li>���鶨ʱ����ʱ���ص����ܵ��¹����쳣</li>
    <li>������������˫�鶨ʱ���Ĵ��룬��Ҫ�����λ���ݣ������鶨ʱ����ֹ</li>
        </body>
    </html>
    """
    simp_html="""<!DOCTYPE html>
    <html>
        <head>
            <title>ũ�׼��</title>
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
            <h1>ũ�׼��ҳ��</h1>
            <form action="/" method="get" accept-charset="utf-8">
                <p><input type='submit' name="simpopenout0" value="�������һ" style="width: 100px; height:100px; border-radius:50px;background:chartreuse"/>&nbsp;&nbsp;&nbsp;&nbsp;<input type='submit' name="simpcloseout0" value="�ر����һ" style="width: 100px; height:100px; border-radius:50px;background-color: crimson">&nbsp;&nbsp;&nbsp;&nbsp;<input type='submit' name="simpbut0" value="��ťһ" style="width: 100px; height:100px; border-radius:50px;background-color:gold"/></p>
                <p><input type='submit' name="simpopenout1" value="���������" style="width: 100px; height:100px; border-radius:50px;background:chartreuse"/>&nbsp;&nbsp;&nbsp;&nbsp;<input type='submit' name="simpcloseout1" value="�ر������" style="width: 100px; height:100px; border-radius:50px;background-color: crimson">&nbsp;&nbsp;&nbsp;&nbsp;<input type='submit' name="simpbut1" value="��ť��" style="width: 100px; height:100px; border-radius:50px;background-color:gold"/></p>
                <p><input type='submit' name="simpopenout2" value="���������" style="width: 100px; height:100px; border-radius:50px;background:chartreuse"/>&nbsp;&nbsp;&nbsp;&nbsp;<input type='submit' name="simpcloseout2" value="�ر������" style="width: 100px; height:100px; border-radius:50px;background-color: crimson">&nbsp;&nbsp;&nbsp;&nbsp;<input type='submit' name="simpbut2" value="��ť��" style="width: 100px; height:100px; border-radius:50px;background-color:gold"/></p>
                <p><input type='submit' name="simpopenout3" value="���������" style="width: 100px; height:100px; border-radius:50px;background:chartreuse"/>&nbsp;&nbsp;&nbsp;&nbsp;<input type='submit' name="simpcloseout3" value="�ر������" style="width: 100px; height:100px; border-radius:50px;background-color: crimson">&nbsp;&nbsp;&nbsp;&nbsp;<input type='submit' name="simpbut3" value="��ť��" style="width: 100px; height:100px; border-radius:50px;background-color:gold"/></p>
                <p><input type='submit' name="simpopenout4" value="���������" style="width: 100px; height:100px; border-radius:50px;background:chartreuse"/>&nbsp;&nbsp;&nbsp;&nbsp;<input type='submit' name="simpcloseout4" value="�ر������" style="width: 100px; height:100px; border-radius:50px;background-color: crimson">&nbsp;&nbsp;&nbsp;&nbsp;<input type='submit' name="simpbut4" value="��ť��" style="width: 100px; height:100px; border-radius:50px;background-color:gold"/></p>
        </form>
        </center>
        </body>
    </html>
    """
    login_html = """<!DOCTYPE html>
    <html>
        <head>
            <title>ũ���ն˿���ƽ̨</title>
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
            <h2>��ӭʹ��ũ���豸��</h2>
                <form action="/" method="get" accept-charset="utf-8">
                    <p><input type="Submit" value="��ͨ����" name="expermain" style="width: 100px; height:100px; border-radius:50px;background-color: coral"/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="Submit" value="�򵥽���" name="simplemain" style="width: 100px; height:100px; border-radius:50px;background-color: chartreuse"/><p>
                    <p><input type="Submit" value="���ý���" name="initmain" style="width: 100px; height:100px; border-radius:50px;background-color:goldenrod"/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="Submit" value="��������" name="helpmain" style="width: 100px; height:100px; border-radius:50px;background-color:goldenrod"/></p>
                    <p><input type="Submit" value="����" name="datamain" style="width: 100px; height:100px; border-radius:50px;background-color:goldenrod"/></p>
                </form>
            </center>
        </body>
    </html>
    """
    data_html=""" <!DOCTYPE html>
    <html>
        <head>
            <title>ũ���ն�</title>
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
            <h1>ũ���豸���ݲɼ�</h1>
			<p>|��|��|��</p>
			<p>|��|��|</p>
			<p>��ǰ�¶ȣ� | ��</p>
			<p>��ǰʪ�ȣ� | %</p>
			<p>��ǰ��ǿ��|</p>
			<p>��ǰҺλ��|</p>
			<p>���һ״̬��|</p>
			<p>�����״̬��|</p>
			<p>�����״̬��|</p>
			<p>�����״̬��|</p>
			<p>�����״̬��|</p>
			<form action="/" method="get" accept-charset="utf-8">
            <p><input type="submit" value="�����ť����" name='datasubmit' style="height: 50px;width: 100px;border-radius: 25px;background-color: beige">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="submit" value="�����ťˢ��" name='refre' style="height: 50px;width: 100px;border-radius: 25px;background-color:aqua"></p>
            </form>
        </center>
    </html>
    """
    error_html="""<!DOCTYPE html>
    <html>
        <head>
            <title>ũ���ն�</title>
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
            <h1>ũ���豸ʹ�ð���</h1>
        <form action="/" method="get" accept-charset="utf-8">
            <p><input type="submit" value="�����ť����" name='errormodesubmit' style="height: 50px;width: 100px;border-radius: 25px;background-color: beige"></p>
            </form>
        </center>
        <h4>������˵����</h4>
        <li>���������ѡ����ͨ���������ϸ�����豸�Ĺ�����ʽ�����������������й��ܡ�</li>
        <li>ѡ��򵥽�����Խ���򵥿��ƣ����ƿ�������ң����������ֱ�ӿ�����ر�ĳ�������������Զ��尴ť�󶨳��ù��ܺ�ɿ��ٿ�����</li>
        <li>ѡ�����ý��棬�������ó��õ�WiFi���ƣ�����������������֣�Ҳ�������ü�ҳ���е��Զ��尴ť��</li>
        <h4>�����ǿ����ն˵���ϸʹ��˵����</h4>
    <li>��������ѡ������Լ�ģʽ��������ѡ��������ƴ������ֱ���ύ������Ŀ��ƴ��������ģʽ���Ӧ��ע��ĳЩģʽ����������ƴ��룬������ֱ�ӿ�����ֱ�ӹر��Լ�������á�</li>
    <li>��ֱ�ӿ������͡�ֱ�ӹرա�ѡ������̵����̵�����ǰ״̬���ڼ̵���û�����õ�����£��̵������û��������Ӧ״̬�����ڼ̵����Ѿ��������õ�����£�ѡ����Щѡ���ύ�󣬼̵����Ի᳢�Ե���״̬����������е���������Ҫת����״̬�г�ͻ����ô�̵������ǻᰴ����ǰ�����ù��������������¶ȴ���ģʽ���Ѿ��ﵽ����������ѡ��ر������õģ�����ʹ������������رռ̵�����</li>
    <li>ˢ��ҳ����������������ü̵����Ĺ���״̬֮���������·��̵����Ĺ���״̬�����������л���������Ϊҳ���Ǿ�̬�ġ����������ѡ��ˢ��ҳ�棬�����ܻὫ��ǰ�ύ�����������ύһ�飬����ܻ������Ԥ��֮��Ľ�������ˢ��ҳ������ˢ�¼̵�����״̬��Ҳ��������ˢ�´�����������</li>
    <li>��ʱ��ģʽ����ÿ����Ҫ���ع̶�ʱ�������������ƹ⡣ʱ�䵽���趨�Ŀ�ʼʱ��ʱ�̵����������������ʱ��ʱ�̵����رա����ڼ̵���ֻ���趨ʱ������ֶ��������������趨��ʱ���ڿ�ʼʱ��֮�󣬼̵����������̶�����������ͨ����ֱ�ӿ�����ѡ���������ϣ���Ĺ���״̬��</li>
    <li>��ʱģʽ������Ҫ��ʱ����һ��ʱ��������������ʱ������������ʱ�򿪷������ע���ʱģʽ����ʱģʽ�ڹ��������󶼻�����̵������ã�����ζ����������Ҫ���µ������á�����̵�����ǰ�����ڶ�ʱģʽ����ô�Ƽ���ʹ��ֱ�ӿ���������ֱ�ӹرյķ�ʽ����ʱģʽ�����һСʱ��</li>
    <li>��ʱģʽ������Ҫ��ʱ�����ϳ�ʱ���������������º�Ȼ����ʱ�ķ����������ʱģʽ����Թ�����ʮ��Сʱ�����������ʱ�����õ���ǰʱ�̣��̵����Ṥ�����ڶ��졣</li>
    <li>����ģʽ�Ĺ���ԭ�����õ�ǰ���ӳ�������ʱ�䣬������������ʱ�䣨���ʱ��������ʱ���빤��ʱ��Ĳ��Ƚϣ����ڼ��ʱ����̵�����������������̵����رա�����ÿ��ʮ���ӹ�������ӣ�����ʱ���Ƕ�ʮ����ӡ����������ĳСʱ�Ķ�ʮ����ӣ���ʮ�������ʮ������Ϊ��ʮ�壬�̵�����ʼ���������ڲ��÷�����Ϊ��׼��������Сʱ����˹��������Ϊ��ʮ���ӡ����ֹ�����ʽ�����ڷ��ͨ�绻����ˮ����Ϲ�ˮ�ȵȡ�</li>
    <li>����ģʽ�Ǹ߶�ʵ���Եģ����и��Բ��Ŀǰӵ���¶���Һλ��������ģʽ������ʹ�õĴӵ�Ƭ������ǿ��������֧������IIC��UART��ADC/DAC��ͨ�ŷ�ʽ�Ĵ��������������</li>
    <h4>�������ն����òο���</h4>
    <li>�����������붨ʱģʽ��˫�鶨ʱģʽ�Ŀ��ƴ��룬Ҫע��Сʱ���ܴ���23�����Ӳ��ܴ���59�����ǽ���ʱ��������ڿ�ʼʱ�䡣��������˵㵽���������ʮ��֣����ƴ�����08001735����ʼʱ�����ֹʱ�䣩��</li>
    <li>�������������ʱģʽ�Ŀ��ƴ��룬��Ҫע���ʱ�ķ�ΧΪ1-60�������������Ϊ��λ����������������Ӻ�رգ����ƴ���Ϊ05�����ڲ���������ġ���Χ�����벻֧�����϶������ͬʱ��ʾ���鵱ǰ�������ֵ����˼�ʱģʽ����ģ�����ƣ���Ҫ��ȷ���Ʒ��ӣ��Ƽ�ʹ����ʱģʽ�������������뵹��ʱʱ�䡣</li>
    <li>��������������ʱģʽ�Ŀ��ƴ��룬��Ҫ������ʱ������ʱ�䣬��������������������˵���ʮ������2040����ֹʱ��ӷ��ӣ�����ʱģʽʹ�ú��Զ��л�Ϊ����״̬��</li>
    <li>�������������Ъģʽ�Ŀ��ƴ��룬��Ҫ���빤������ʱ����ÿ�����ڵĹ���ʱ�䣬Ŀǰ֧�����õ��������Ϊ60���ӡ�����ÿ��Сʱ��������ӣ���Ҫ������ƴ���2505�����ʱ��ӹ���ʱ�䣩</li>
    <li>�����������봥��ģʽ�Ŀ��ƴ��룬Ŀǰ֧���¶ȴ�����Һλ�����봥�������¶ȴ���ģʽ��Ҫ���¶�������ǰ������0�������¶ȴ���25���϶ȿ�����С��20���϶ȹرգ�����02520��������ʽ�Ӵ������޼Ӵ������ޣ���Һλ������Ҫ��Һλ������ǰ������1���Ҿ����������λ������λΪ���ף�����λ�ô���800���׿�����С��400���׹رգ�����108000400��</li>
    </html>
    """
    init_html="""<!DOCTYPE html>
    <html>
        <head>
            <title>ũ���ն�</title>
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
            <h1>ũ���豸���ý���</h1>
            <h2>�����������������豸</h2>
            <form action="/" method="get" accept-charset="utf-8">
            <p>Wifi����:<input type="text" name="ssidname" placeholder='Wifi���ƣ���֧�������ַ�'/></p>
            <p>Wifi����:<input type="text" name="ssidcode" placeholder='Wifi���룬��������ɲ���'/></p></p>
            <p>��ťһ����:<input type="text" name="but0code" placeholder='���밴ťһ�Ŀ��ƴ���'/></p>
            <p>��ť������:<input type="text" name="but1code" placeholder='���밴ť���Ŀ��ƴ���'/></p>
            <p>��ť������:<input type="text" name="but2code" placeholder='���밴ť���Ŀ��ƴ���'/></p>
            <p>��ť�Ĺ���:<input type="text" name="but3code" placeholder='���밴ť�ĵĿ��ƴ���'/></p>
            <p>��ť�幦��:<input type="text" name="but4code" placeholder='���밴ť��Ŀ��ƴ���'/></p>
            <input type="submit" name='initsubmit' style="width:100px;height:50px;border-radius: 15px;background-color: blanchedalmond" />
        </form>
        </center>
    <li>WiFi�˺����������������豸Ĭ�����ӵ�WiFi��WiFi�����豸��ȡʱ���Լ����ƹ��ܣ���ϵͳ��ʱ�Լ�������ɺ���Թر�WiFi</li>
    <li>������������ƿ����Զ��壬���Զ���Ϊ������Ƶ��豸���ƣ��硰����������ƹ⡱��ʪ������</li>
    <li>���Ҫʹ�ü�˹��ܣ���Ҫ���������ť�����ƺ͹��ܣ����ù�����Ҫʹ�ÿ��ƴ��룬�������Ϥ���ƴ��룬������һ���¼���˽�</li>
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
def relay_on(num):#ֱ�Ӱ�ť�����Ĵ򿪼̵�����������
    global con_data_global
    if con_data_global[num]=='0':#�����ǰ�̵����Ŀ��Ʒ�ʽΪ���գ�������Ϊ����
        con_data_global[num]='1'
    else:#�����ǰ�̵������ò��ǳ����������̵������ã���ת�̵���״̬�������ǰ�̵����Ѿ��ǹر�״̬����ִ�в���
        if(relay[num].value()==0):
            relay[num].on()
def relay_off(num):#�رռ̵����Ĳ�������
    global con_data_global
    if con_data_global[num]=='1':#�����ǰ�̵����Ŀ��Ʒ�ʽΪ������������Ϊ����
        con_data_global[num]='0'
    else:#�����ǰ�̵������ò��ǳ����������̵������ã����Ƿ�ת�̵���״̬�������ǰ�̵����Ѿ��ǹر�״̬����ִ�в���
        if(relay[num].value() ==1):
            relay[num].off()
def file_write(file_name,s):#д�ļ�����
    c_file=open(file_name,'w')
    c_file.write(str(s))
    c_file.close()
def error_inter(typenum,data):#������Ŀ��ƴ����д��󷵻�0�����󷵻�1
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
def req_pro(req_data):#�����յ�������������Ϣ������Ӧ����ʾ��ҳ��
    global con_data_global
    if req_data.find('expermain')>-1:
        return 'main'
    elif req_data.find('simplemain')>-1:#��ҳ�水ť
        return 'simple'
    elif req_data.find('initmain')>-1:#����ҳ���ύ
        return 'init'
    elif req_data.find('helpmain')>-1:#����ҳ���ύ
        return 'error'
    elif req_data.find('datamain')>-1:#����ҳ���ύ
        return 'data'
    elif(req_data.find('refre')>-1):#ˢ��ҳ��
        return 'data'
    elif(req_data.find('mainsubmit')>-1):#�������ύ
        req_data_spl=req_data.split('&')
        rec_spl=req_data.split('&')
        if(rec_spl[2][-1]=='='):#�ж��Ƿ�������ƴ��룬���û��������ƴ��룬������Ӧҳ��
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
    elif(req_data.find('simpopenout')>-1):#�򵥽����ύ����
        con_data_global[eval(req_data[req_data.find('simpopenout')+11])]='1'
        print(req_data[req_data.find('simpopenout')+11])
        return 'simple'
    elif(req_data.find('simpcloseout')>-1):#�򵥽����ύ�ر�
        con_data_global[eval(req_data[req_data.find('simpcloseout')+12])]='0'
        return 'simple'
    elif(req_data.find('butcode')>-1):#�򵥽�������ť����
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
def main_send(res):#��ͻ��˷�����ҳ�Ͷ�ȡ����ֵ�ĺ���
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
def relay_control_single(relay_num,relay_data):# �˺����жϵ����̵����Ƿ�Ӧ�ö���,�ж���ʱ���ظú����ķ���ֵ������0�رռ̵�������1���򿪼̵���
    global rad_dis
    time_now=rtc.datetime()#��ȡ��ǰʱ��
    if(len(relay_data)==1):#�����ǳ������տ��ƣ����ؿ��ƴ���
        return eval(relay_data)
    elif(relay_data[0]=='1'):#��ͷΪ1��ʱģʽ
        begin_hour=eval(relay_data[1:3])
        begin_min=eval(relay_data[3:5])
        end_hour=eval(relay_data[5:7])
        end_min=eval(relay_data[7:9])
        if(time_now[4]==begin_hour and time_now[5]==begin_min and time_now[6]==0)or(time_now[4]==begin_hour and time_now[5]==begin_min and time_now[6]==1):
            return 1
        if(time_now[4]==end_hour and time_now[5]==end_min and time_now[6]==0)or(time_now[4]==end_hour and time_now[5]==end_min and time_now[6]==1):
            return 0
    if(relay_data[0]=='2'):#��ͷΪ2��ʱģʽ
        end_hour=eval(relay_data[1:3])
        end_min=eval(relay_data[3:5])
        if(time_now[4]==end_hour and time_now[5]==end_min and time_now[6]==0)or(time_now[4]==end_hour and time_now[5]==end_min and time_now[6]==1):
            con_data_global[relay_num]='0'
            return 0
        else:
            return 1
    if(relay_data[0]=='3'):#��ͷΪ3����ʱģʽ
        delay_min=eval(relay_data[1:3])
        end_min=delay_min+time_now[5]
        if end_min>=60:
            min_end=end_min%60
            hour_end=time_now[4]+1
        else:
            min_end=end_min
            hour_end=time_now[4]
        con_data_global[relay_num]='2'+'%02d'%hour_end+'%02d'%min_end
    if(relay_data[0]=='4'):#��ͷΪ4����Ъģʽ
        inte_time=eval(relay_data[1:3])
        work_time=eval(relay_data[3:5])
        loop_time=inte_time+work_time
        if(time_now[5]%loop_time==inte_time):
            return 1
        if(time_now[5]%loop_time==0):
            return 0
    if(relay_data[0]=='5'):#��ͷΪ5��������ģʽĿǰ������֧�ֵ������Ƚ���0���¶ȴ���ģʽ�����ȵ��������϶�1�����봥��ģʽ�����ȵ���������
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
    if(relay_data[0]=='6'):#˫�鶨ʱ��ģʽ
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
def all_relay_con():#���м̵����Ŀ��ƺ�������Ҫ���õ����̵������ƺ���
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
def main_try():#������ѭ��
    while True:
        if not sta_if.isconnected():
            if(len(log_data[0])<1):
                try:
                    do_connect('ũ��','')#Ĭ��������Ϊ��ũ�ס����ȵ㣬���ú�������������ȵ�
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