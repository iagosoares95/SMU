from socket import *
import time
import select

class sip_register:
    def __init__(self, ip='', port=0, ip_dest='', port_dest=5060, ramal =0):
        self.ip = ip
        self.port = port
        self.ip_dest = ip_dest
        self.port_dest = port_dest
        self.call_id = hash(time.time())
        self.ramal = ramal
    def register(self, ramal):
        reg_str =  """REGISTER sip:""" + self.ip_dest + """ SIP/2.0
Via: SIP/2.0/UDP """ + self.ip + """:""" + str(self.port) + """;rport
<<<<<<< HEAD
From: <sip:""" + str(self.ramal) + """@""" + self.ip + """:""" + str(self.port) + """>
To: <sip:""" + str(self.ramal) + """@""" + self.ip + """:""" + str(self.port) + """>
Call-ID: """ + str(self.call_id) + """@""" + self.ip + """
CSeq: 1 REGISTER
Contact: <sip:""" + str(self.ramal) + """@""" + self.ip + """:""" + str(self.port) + """>
=======
From: <sip:6031@""" + self.ip + """:""" + str(self.port) + """>
To: <sip:6031@""" + self.ip + """:""" + str(self.port) + """>
Call-ID: """ + str(self.call_id) + """@""" + self.ip + """
CSeq: 1 REGISTER
Contact: <sip:6031@""" + self.ip + """:""" + str(self.port) + """>
>>>>>>> 01a13d01aeb3b12fdd4080c5747368c8ae4373e9
Max-Forwards: 70
User-Agent: SMU20182
Expires: 9999
Content-Length: 0

"""
        return reg_str

    def deregister(self):
        reg_str =  """REGISTER sip:""" + self.ip_dest + """ SIP/2.0
Via: SIP/2.0/UDP """ + self.ip + """:""" + str(self.port) + """;rport
From: <sip:6031@""" + self.ip + """:""" + str(self.port) + """>
To: <sip:6031@""" + self.ip + """:""" + str(self.port) + """>
Call-ID: """ + str(self.call_id) + """@""" + self.ip + """
CSeq: 2 REGISTER
Contact: <sip:6031@""" + self.ip + """:""" + str(self.port) + """>
Max-Forwards: 70
User-Agent: SMU20182
Expires: 0
Content-Length: 0

"""
        return reg_str

    def send(self, reg_str, local_send_ip):
        sockobj = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        sockobj.connect((local_send_ip, self.port_dest))
        sockobj.send(reg_str.encode('ascii'))
        ready = select.select([sockobj], [], [], 3)
        if ready[0]:
            data, addr = sockobj.recvfrom(1024)
            data_str = data.decode('ascii').splitlines()[0]
            resposta = int(data_str.split()[1])
            assert resposta == 200
        else:
            select.error

        return reg_str
#        sockobj.close()
    def bye(self, local_send_ip, cid):
        bye_str =  """BYE sip:""" + self.ip_dest + """ SIP/2.0
Via: SIP/2.0/UDP """ + self.ip + """:""" + str(self.port) + """;rport
From: <sip:6032@""" + self.ip + """:""" + str(self.port) + """>
To: <sip:6002@""" + local_send_ip + """:""" + str(self.port) + """>
Call-ID: """ + str(cid) + """
CSeq: 1 BYE
Max-Forwards: 70
User-Agent: SMU20182
Content-Length: 0

"""
        return bye_str
# reg_str =  """REGISTER sip:192.168.1.1 SIP/2.0
# Via: SIP/2.0/UDP 192.168.1.222:5060;rport
# From: <sip:6031@192.168.1.222:5060>
# To: <sip:6031@192.168.1.222:5060>
# Call-ID: 766827566@192.168.1.222
# CSeq: 1 REGISTER
# Contact: <sip:6031@192.168.1.222:5060>
# Max-Forwards: 70
# User-Agent: IPC/3.0
# Expires: 300
# Content-Length: 0

# """

# reg_str2 =  """REGISTER sip:192.168.1.1 SIP/2.0
# Via: SIP/2.0/UDP 192.168.1.222:5060;rport
# From: <sip:6031@192.168.1.222:5060>
# To: <sip:6031@192.168.1.222:5060>
# Call-ID: 766827566@192.168.1.222
# CSeq: 2 REGISTER
# Contact: <sip:6031@192.168.1.222:5060>
# Max-Forwards: 70
# User-Agent: IPC/3.0
# Expires: 0
# Content-Length: 0

# """

# #print(reg_str)



# sockobj.send(reg_str2.encode('ascii'))
# time.sleep(1)
