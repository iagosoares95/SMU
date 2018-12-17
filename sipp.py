from socket import *
import time
import select
import meusip

class sipp:
    def __init__(self, ip='', port=0, ip_dest='', port_dest=5060, ramal='',chama='', ipserver=''):
        self.ip = ip
        self.port = port
        self.ip_dest = ip_dest
        self.port_dest = port_dest
        self.call_id = hash(time.time())
        self.ramal = ramal
        self.ramalgera = ramal
        self.ramalchama = chama
        self.ipserver = ipserver
        self.cid = meusip.randid(32)
        self.estado = ''

    def register(self, ramal):
        reg_str =  """REGISTER sip:""" + self.ip_dest + """ SIP/2.0
Via: SIP/2.0/UDP """ + self.ip + """:""" + str(self.port) + """;rport
From: <sip:""" + str(self.ramal) + """@""" + self.ip + """:""" + str(self.port) + """>
To: <sip:""" + str(self.ramal) + """@""" + self.ip + """:""" + str(self.port) + """>
Call-ID: """ + str(self.call_id) + """@""" + self.ip + """
CSeq: 1 REGISTER
Contact: <sip:""" + str(self.ramal) + """@""" + self.ip + """:""" + str(self.port) + """>
Max-Forwards: 70
User-Agent: SMU20182
Expires: 9999
Content-Length: 0

"""
        self.estado = "reg"
        return reg_str

    def deregister(self, ramal):
        reg_str =  """REGISTER sip:""" + self.ip_dest + """ SIP/2.0
Via: SIP/2.0/UDP """ + self.ip + """:""" + self.port + """;rport
From: <sip:""" + str(self.ramal) + """@""" + self.ip + """:""" + str(self.port) + """>
To: <sip:""" + str(self.ramal) + """@""" + self.ip + """:""" + str(self.port) + """>
Call-ID: """ + self.cid + """@""" + self.ip + """
CSeq: 2 REGISTER
Contact: <sip:""" + str(self.ramal) + """@""" + self.ip + """:""" + str(self.port) + """>
Max-Forwards: 70
User-Agent: SMU20182
Expires: 0
Content-Length: 0

"""
        return reg_str

    def invite(self, ramalgera, ramalchama, ipserver):
        invite_str = """INVITE sip:""" + str(ramalchama) + """@""" + str(ipserver) + """ SIP/2.0
Via: SIP/2.0/UDP """ + self.ip + """:""" + str(self.port) + """;rport
From: <sip:""" + str(self.ramalgera) + """@""" + str(ipserver) + """:""" + str(self.port) + """>
To: <sip:""" + str(ramalchama) + """@""" + str(ipserver) + """:""" + str(self.port) + """>
Call-ID: """ + str(self.cid) + """@""" + self.ip + """
CSeq: 2 INVITE
Contact: <sip:""" + str(self.ramalgera) + """@""" + self.ip + """:""" + str(self.port) + """>
Max-Forwards: 70
User-Agent: SMU20182
Expires: 0
Content-Length: 246

v=0
o=6032@192.168.1.229 1544548743 1544548743 IN IP4 192.168.1.231
c=IN IP4 192.168.1.229
t=1544548743 1544552343
s=VMS
m=video 4000 RTP/AVP 96
a=rtpmap:96 H264/90000
a=framerate:15.000000
m=audio 4001 RTP/AVP 0 1
a=rtpmap:0 PCMU/8000
a=rtpmap:1 PCMA/8000
"""

        self.estado = "inv"
        #print (invite_str)
        return invite_str

#    def duzentos(self):

    def ack(self, ramalgera, ramalchama, ipserver):
        print ("oi3")
        ack_str = """ACK sip:""" + str(ramalchama) + """@""" + str(ipserver) + """ SIP/2.0
Via: SIP/2.0/UDP """ + self.ip + """:""" + str(self.port) + """;rport
From: <sip:""" + str(ramalgera) + """@""" + str(ipserver) + """:""" + str(self.port) + """>
To: <sip:""" + str(ramalchama) + """@""" + str(ipserver) + """:""" + str(self.port) + """>
Call-ID: """ + str(self.cid) + """@""" + self.ip + """
CSeq: 2 ACK
Contact: <sip:""" + str(ramalgera) + """@""" + self.ip + """:""" + str(self.port) + """>
Max-Forwards: 70
User-Agent: SMU20182
Content-Length: 0

"""       
        #print (ack_str)
        return ack_str

    def bye(self, local_send_ip, cid, ramalgera, ramalchama):
        bye_str =  """BYE sip:""" + self.ip_dest + """ SIP/2.0
Via: SIP/2.0/UDP """ + self.ip + """:""" + str(self.port) + """;rport
From: <sip:""" + self.ramalgera + """@""" + self.ip + """:""" + self.port + """>
To: <sip:""" + self.ramalchama + """@""" + local_send_ip + """:""" + self.port + """>tag=1234
Call-ID: """ + self.cid + """
CSeq: 1 BYE
Max-Forwards: 70
User-Agent: SMU20182
Content-Length: 0

"""
        return bye_str

    def send(self, reg_str, local_send_ip):
        #print (reg_str)
        sockobj = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        sockobj.connect((local_send_ip, self.port_dest))
        sockobj.send(reg_str.encode('ascii'))
        ready = select.select([sockobj], [], [], 3)
        if ready[0]:
            while True:
                data, addr = sockobj.recvfrom(1024)
                data_str = data.decode('ascii').splitlines()[0]
                print (data_str[1])
                resposta = int(data_str.split()[1])
                if resposta == 100:
                    print("Tentando - 100 Trying")
                if resposta == 101:
                    print("Diálogo estabelecido - 101 Dialog establishment")
                if resposta == 180:
                    print("Tocando - 180 Ringing")
                if resposta == 183:
                    print("Sessão em progresso - 183 Session in progress")
                if resposta == 200:# and self.estado is not "reg":
                    print("oi3") 
                    print("Sucesso - 200 OK")
                    self.ack_str=self.ack(self.ramalgera, self.ramalchama, self.ip_dest)
                    self.send(self.ack_str, self.ip_dest)
                if resposta == 400:
                    print("Sintaxe errada - 400 Bad request")
                if resposta == 401:
                    print("Não autorizado - 401 Unauthorized")
                if resposta == 403:
                    print("Proibido - 403 Forbidden")
                if resposta == 404:
                    print("Ramal não encontrado - 404 Not Found")
                if resposta == 406:
                    print("Não aceito - 406 Not Acceptable")
                if resposta == 480:
                    print("Temporariamente nao acessível - 480 Temporarily Unavailable")
                if resposta == 481:
                    print("Call-ID, branch ou tag incorretos - 481 Call/Transaction Does Not Exist")
                if resposta == 486:
                    print("Lotado - 486 Busy Here")
                if resposta == 488:
                    print("Request-URI não aceitável - 488 Not Acceptable Here")
                print ("oi1")
            else:
                select.error
#        sockobj.close()
# reg_str =  """REGISTER sip:192.168.1.1 SIP/2.0
# Via: SIP/2.0/UDP 192.168.1.222:5060;rport
# From: <sip:6032@192.168.1.222:5060>
# To: <sip:6032@192.168.1.222:5060>
# Call-ID: 766827566@192.168.1.222
# CSeq: 1 REGISTER
# Contact: <sip:6032@192.168.1.222:5060>
# Max-Forwards: 70
# User-Agent: IPC/3.0
# Expires: 300
# Content-Length: 0

# """

# reg_str2 =  """REGISTER sip:192.168.1.1 SIP/2.0
# Via: SIP/2.0/UDP 192.168.1.222:5060;rport
# From: <sip:6032@192.168.1.222:5060>
# To: <sip:6032@192.168.1.222:5060>
# Call-ID: 766827566@192.168.1.222
# CSeq: 2 REGISTER
# Contact: <sip:6032@192.168.1.222:5060>
# Max-Forwards: 70
# User-Agent: IPC/3.0
# Expires: 0
# Content-Length: 0

# """

# #print(reg_str)



# sockobj.send(reg_str2.encode('ascii'))
# time.sleep(1)
