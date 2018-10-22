#!/usr/bin/python3
 
import meusip,siptrans
import selectors
import gi
gi.require_version('Gtk', '3.0')
#gi.require_version('Vte', '2.91')
from gi.repository import Gtk
from gi.repository import GLib

Timeout = 5 # 5 seg
 
# cria um UserAgent com originador "100" e IP do UAC=192.168.1.53
c = siptrans.UserAgent('100', ip='192.168.1.1')
 
# adiciona uma descrição de media do tipo audio ao UAC, incluindo
# respectivos codecs
media = meusip.SDPMedia('audio',4000)
media.add_codec(0, 'PCMU/8000')
media.add_codec(1, 'PCMA/8000')
c.add_media(media)

# cria um IOChannel associado ao UAC
chan = GLib.IOChannel(c.fileno)

# define o IOChannel como não-bloqueante
chan.set_flags(GLib.IO_FLAG_NONBLOCK)

# registra um callback no IOChannel para condição de leitura
cond = GLib.IOCondition(GLib.IOCondition.IN)
chan.add_watch(cond, c.handle)

# cria um timer para o timeout
tout = GLib.timeout_add_seconds(Timeout, c.handle_timeout)

# inicia uma chamada para o contato "200" que está no UAS 192.168.1.54
c.call('200','192.168.1.101')

# O loop de eventos do ambiente gráfico
Gtk.main()
