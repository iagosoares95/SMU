#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 22 14:57:16 2018

@author: pedrohames
"""

import meusip, siptrans

class contiudo:

    def __init__(self, my_IP, my_number, video_port, audio_port, cam_IP, cam_number):

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

        c.call(cam_number,'192.168.1.1')

        self.sdp = c.body

    def getSDP(self):
        return self.sdp
