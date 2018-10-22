#!/usr/bin/python3

import meusip,siptrans
import selectors

# cria um UserAgent com originador "100" e IP do UAC=192.168.1.53
c = siptrans.UserAgent('100', ip='192.168.1.221')

# adiciona uma descrição de media do tipo audio ao UAC, incluindo
# respectivos codecs
media = meusip.SDPMedia('audio',4000)
media.add_codec(0, 'PCMU/8000')
media.add_codec(1, 'PCMA/8000')
c.add_media(media)

# inicia uma chamada para o contato "200" que está no UAS 192.168.1.54
c.call('200','192.168.1.101')

# Um loop de eventos simplificado:
# detecta eventos (mensagens recebidas, timeouts) e os encaminha ao UAC

sched = selectors.DefaultSelector()
sched.register(c.fileno, selectors.EVENT_READ)
while True:
    ev = sched.select(5000)
    if not ev: # se ocorreu timeout
        c.handle_timeout()
    else: # se uma mensagem foi recebida
        c.handle()
    if c.idle: break # se chamada encerrou, então termina
