#!/usr/bin/python3
 
import meusip,siptrans
import selectors
import subprocess
 
# cria um UserAgent com originador "100" e IP do UAC=192.168.1.53
c = siptrans.UserAgent('100', ip='192.168.1.221')
 
# adiciona uma descrição de media do tipo audio ao UAC, incluindo
# respectivos codecs
media = meusip.SDPMedia('video',4000)
media.add_codec(96, 'H264/90000')
#media.add_codec(34, 'H263/90000')
#media.add_codec(35, 'H263p/90000')
media.add_attribute('framerate:15.000000')
c.add_media(media)
media = meusip.SDPMedia('audio',4001)
media.add_codec(0, 'PCMU/8000')
media.add_codec(1, 'PCMA/8000')
c.add_media(media)

sdp = c.body
open('stream.sdp','w').write(sdp)
pid = subprocess.Popen(['vlc','stream.sdp']).pid
 
# inicia uma chamada para o contato "200" que está no UAS 192.168.1.54
c.call('6002','192.168.1.211')
 
# Um loop de eventos simplificado:
# detecta eventos (mensagens recebidas, timeouts) e os encaminha ao UAC
# 
sched = selectors.DefaultSelector()
sched.register(c.fileno, selectors.EVENT_READ)
#
while True:
    try:
      ev = sched.select(5000)
      if not ev: # se ocorreu timeout
          c.handle_timeout()
      else: # se uma mensagem foi recebida
          c.handle()
      if c.idle: break # se chamada encerrou, então termina
    except Exception as e:
      print(e)
      c.hangup()
