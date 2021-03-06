#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 22 14:57:16 2018

@author: pedrohames
"""

import meusip, siptrans
import selectors
# import subprocess

class contiudo:

    def __init__(self, my_IP, my_number, video_port, audio_port, cam_IP, cam_number, ip_server):

        # cria um UserAgent com originador "100" e IP do UAC=192.168.1.53
        c = siptrans.UserAgent(my_number, ip=my_IP)

        # adiciona uma descrição de media do tipo audio ao UAC, incluindo
        # respectivos codecs
        media = meusip.SDPMedia('video',video_port)
        media.add_codec(96, 'H264/90000')
        #media.add_codec(34, 'H263/90000')
        #media.add_codec(35, 'H263p/90000')
        media.add_attribute('framerate:15.000000')
        c.add_media(media)
        media = meusip.SDPMedia('audio',audio_port)
        media.add_codec(0, 'PCMU/8000')
        media.add_codec(1, 'PCMA/8000')
        c.add_media(media)

        # open('stream.sdp','w').write(self.sdp)
        # pid = subprocess.Popen(['vlc','stream.sdp']).pid
        
        self.sdp = c.body
        c.call(cam_number, cam_IP)
        self.cid = c.call_id()
        # Um loop de eventos simplificado:
# detecta eventos (mensagens recebidas, timeouts) e os encaminha ao UAC
         
        # sched = selectors.DefaultSelector()
        # sched.register(c.fileno, selectors.EVENT_READ)
        # while True:
        #     ev = sched.select(5000)
        #     if not ev: # se ocorreu timeout
        #         c.handle_timeout()
        #     else: # se uma mensagem foi recebida
        #         c.handle()
        #     if c.idle: break # se chamada encerrou, então termina

    def call_id(self):
        return self.cid
        c.call(cam_number, ip_server)
        sched = selectors.DefaultSelector()
        sched.register(c.fileno, selectors.EVENT_READ)
        while True:
            ev = sched.select(5000)
            if not ev: # se ocorreu timeout
                c.handle_timeout()
            else: # se uma mensagem foi recebida
                c.handle()
                self.sdp = c.body
            if c.idle: break # se chamada encerrou, então termina

    def getSDP(self):
        return self.sdp
