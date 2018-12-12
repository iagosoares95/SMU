#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  9 15:48:31 2018

@author: msobral
"""

import meusip
import socket
from enum import Enum

import fcntl
#import struct
import time
import random
import select
# =============================================================================
# def get_ip_address(ifname='eth0'):
#     s = socket(AF_INET, SOCK_DGRAM)
#     return inet_ntoa(fcntl.ioctl(
#         s.fileno(),
#         0x8915,  # SIOCGIFADDR
#         struct.pack('256s', ifname[:15].encode('ascii'))
#     )[20:24])
# =============================================================================

class UserAgent:

    '''Representa um UAC especializado em fazer chamadas'''
    
    class Evento(Enum):
        Mensagem = 1
        Timeout = 2
        Start = 3
        Finish = 4
        
    Timeout = 3000 # 3 s
    AnswerTimeout = 10000
    MaxTX = 5
    MaxMessageSize = 2048
    
    def __init__(self, orig, **args):
        '''Cria um UAC. Parâmetros:
            orig: usuário SIP originador (sem URI)
            port=<int>: port SIP deste UAC
            ip=<str>: endereço IP deste UAC
            rtp_port=<int>: port para a stream RTP'''
        self.orig = orig
        self.dest = None
        self.port = args.get('port', 5060)
        self.rtp_port = args.get('rtp_port', 4000)
        self.ip = args.get('ip', '0.0.0.0')
        self.cid = meusip.randid(32)
        self.branch = meusip.randid(32)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.ip, 5060))
        #self.ip = get_ip_address()
        self.cseq = random.randint(1,1000)
        self.tag = meusip.randid(32)
        self._medias = []
        self._estado = self._IDLE
        self._req = None
                
    @property
    def fileno(self):
        'Retorna o descritor do socket a ser usado por algum poller'
        return self.sock.fileno()

    def call(self, dest, destip, destport=5060):
        '''Inicia uma chamada. Parâmetros:
            dest: usuário SIP a ser chamado
            destip: endereço IP do UAS do destinatário
            destport: port UDP no UAS'''
        if self._estado == self._IDLE:
            self._dest = str(meusip.ContactURI(dest, destip))
            self._destip = destip
            self._destport = destport
            self.ntx = 1
            self._estado(UserAgent.Evento.Start)
        else:
            raise Exception('chamada em andamento')

    def hangup(self):
        'Encerra uma chamada'
        self._estado(UserAgent.Evento.Finish)

    def handle(self, *args):
       'Trata uma mensagem recebida'
       self._estado(UserAgent.Evento.Mensagem)
       return True
    
    def handle_timeout(self, *args):
       'Trata um timeout'
       self._estado(UserAgent.Evento.Timeout)
       #print('timeout')
       return True
       
    def add_media(self, media):
        '''Adiciona um objeto SDPMedia, que descreve tipo de media e codecs. Mas de uma descrição de media pode ser adicionada ao UAC'''
        self._medias.append(media)
        
    @property
    def idle(self):
        'Retorna true se UAC estiver ocioso, false se houver chamada em andamento'
        return self._estado == self._IDLE
  
    @property
    def body(self):
      return self._gensdp()

    # Métodos privativos
    def _gensdp(self):
        msg = meusip.SDP('VMS', '%s@%s' % (self.orig, self.ip), self.ip)
        for media in self._medias:
            msg.add_media(media)
        return str(msg)
    
    def _gen_request(self, metodo, dest, destport, body=''):
        req = meusip.SIPRequest(metodo, dest, body=body)
        req.ContentType = 'application/sdp'
        via = meusip.ViaHeader(self.ip, self.port)
        req.Via = via
        req.From = 'sip:%s@%s;tag=%s' % (self.orig, '192.168.1.1', self.tag)
        #req.From = 'sip:%s@%s:5060;tag=%s' % (self.orig, '192.168.1.1', self.tag) 
        req.To = dest
        #req.To = dest[:-1] + ':5060>' 
        req.Contact = '%s@%s:%d' % (self.orig, self.ip, self.port)
        req.CallId = self.cid
        req.set_header('User-Agent', 'Meu SIP 1.0')
        req.branch = self.branch
        req.CSeq = self.cseq
	#if metodo == 'ACK':
            #req.Allow = 'INVITE, ACK, BYE, OPTIONS'
        return req
        
    def _rcv_message(self):
        data,addr = self.sock.recvfrom(UserAgent.MaxMessageSize)
        try:
            msg = meusip.SIPResponse.parse(data)
        except:
            msg = meusip.SIPRequest.parse(data)
        return msg
    
    def _send(self, msg=None):
        if msg == None: msg = self._req
        msg = str(msg).encode('ascii')
        #print('>>>', msg)
        #self.sock.sendto(msg,  (self._destip, self._destport))
        self.sock.connect((self._destip, self._destport))
        self.sock.send(msg)
#        ready = select.select([self.sock], [], [], 3)
#       if ready[0]:
#            data, addr = self.sock.recvfrom(1024)
#            data_str = data.decode('ascii').splitlines()[0]
#            resposta = int(data_str.split()[1])
#            assert resposta == 200
#        else:
#            select.error
        
    # Métodos da MEF
    def _START(self, ev, *args):
        print("oi")
        if ev == UserAgent.Evento.Mensagem:
            msg = self._rcv_message()
            if not self._req.related_to(msg): return
            if isinstance(msg,meusip.SIPResponse):
                if 200 <= msg.status < 300:
                    ack = meusip.SIPAck(self._dest, msg=msg)
                    self._send(ack)
                    self._estado = self._CON
                elif msg.status < 200:
                    pass
                else:
                    self._estado = self._IDLE
        elif ev == UserAgent.Evento.Timeout:
            self._send()
            
    def _CON(self, ev, *args):
        if ev == UserAgent.Evento.Mensagem:
            msg = self._rcv_message()
            if not self._req.related_to(msg): return
            if isinstance(msg,meusip.SIPResponse):
                if 200 <= msg.status < 300:
                    ack = meusip.SIPAck(self._dest, msg=msg)
                    self._send(ack)
                elif msg.status < 200:
                    pass
                else:
                    self._estado = self._FAIL
            else: # Request
                if msg.metodo == 'BYE':
                    resp = meusip.SIPResponse(200, 'OK', msg=msg)
                    self._send(resp)
                    self._estado = self._IDLE
        elif ev == UserAgent.Evento.Finish:
            msg = meusip.SIPBye(self._req.uri, msg=self._req)
            self._send(msg)
            self._estado = self._END

    def _END(self, ev, *args):
        if ev == UserAgent.Evento.Mensagem:
            msg = self._rcv_message()
            if not self._req.related_to(msg): return
            if isinstance(msg,meusip.SIPResponse):
                if 200 <= msg.status < 300:
                    self._estado = self._IDLE
                else:
                    pass
            else: # Request
                if msg.metodo == 'BYE':
                    resp = meusip.SIPResponse(200, 'OK', msg=msg)
                    self._send(resp)
        elif ev == UserAgent.Evento.Timeout:
            msg = meusip.SIPBye(self._dest, msg=self._req)
            self._send(msg)
            
    def _IDLE(self, ev, *args):
        if ev == UserAgent.Evento.Mensagem:
            msg = self._rcv_message()
            if self._req == None: return
            if not self._req.related_to(msg): return
            if isinstance(msg,meusip.SIPRequest):
                if msg.metodo == 'BYE':
                    resp = meusip.SIPResponse(200, 'OK', msg=msg)
                    self._send(resp)
        elif ev == UserAgent.Evento.Start:
            self._req = self._gen_request('invite', self._dest, self._destport, self._gensdp())
            self._send()
            self._estado = self._START
            print (self._estado)
   
