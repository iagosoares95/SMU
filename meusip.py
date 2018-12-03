#!/usr/bin/python3

import sys,io
import re,random
import string
import time

def randid(n=8):
    'Gera uma string aleatória com n caracteres hexadecimais'
    r = ''
    while len(r) < n:
        r += random.choice(string.hexdigits)
    return r.lower()

class ContactURI:
    '''Representa um valor de cabeçalho com URI SIP, com 
atributo tag. Usado tipicamente nos cabeçalhos From e To.'''

    Expr = re.compile('<?sip:([^@]+)@([^;>]+)>?($|;tag=(.*))')
    
    def __init__(self, uri, addr, tag=''):
        '''Cria um objeto ContactURI. Argumentos:
uri: identificador do contato (ex: 100, alice, bob, ...)
addr: endereço ou domínio do contato (ex: 10.0.0.1, ifsc.edu.br)
tag: valor do atributo tag (opcional)'''
        self.uri = uri
        self.addr = addr
        self.tag = tag
            
    def __str__(self):
        'Gera o valor do cabeçalho formatado'
        r = '<sip:%s@%s>' % (self.uri, self.addr)
        if self.tag:
            r = '%s;tag=%s' % (r, self.tag)
        return r
    
    @staticmethod
    def parse(data):
        '''Método estático para gerar um objeto ContactURI a partir
de um valor de cabeçalho (str)'''
        m = ContactURI.Expr.match(data)
        if not m: raise ValueError('malformed contact uri: '+data)
        uri,addr,x,tag = m.groups()
        return ContactURI(uri, addr, tag)
              
class ViaHeader:

    '''Representa um valor de cabeçalho Via, com 
atributos branch,rport e received.'''

    Expr = re.compile(r'SIP/2.0/UDP ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}):([0-9]{1,5})(.*)')
    
    def __init__(self, addr,port, **args):
        '''Cria um objeto ViaHeader. Argumentos:
addr: endereço IP do agente SIP que gerou o cabeçalho
port: port do agente SIP que gerou o cabeçalho
args: argumentos opcionais:
.. branch: identificador do branch
.. rport: número do rport
.. received: IP visto pelo agente que recebeu a mensagem anterior
(ver RFC 3581)'''
        self.addr = addr
        self.port = port
        self.branch = args.get('branch','')
        self.rport = args.get('rport', 0)
        self.received = args.get('received','')
        
    def __str__(self):
        'Gera o valor do cabeçalho formatado'
        r = 'SIP/2.0/UDP %s:%d' % (self.addr, self.port)
        if self.branch:
            r = '%s;branch=%s' % (r, self.branch)
        if self.rport:
            r = '%s;rport=%d' % (r, self.rport)
        else:
            r = '%s;rport' % r
        if self.received:
            r = '%s;received=%s' % (r, self.received)            
        return r
    
    @staticmethod
    def parse(data):
        '''Método estático para gerar um objeto ViaHeader a partir
de um valor de cabeçalho (str)'''
        m = ViaHeader.Expr.match(data)                
        if not m: raise ValueError('malformed Via: '+data)
        addr,port,data = m.groups()
        port = int(port)
        data = data.split(';')
        args = {}
        for tok in data:
            tok = tok.split('=')
            if tok[0] == 'branch':
                args['branch']=tok[1]
            elif tok[0] == 'rport':
                if len(tok) > 1: args['rport'] = int(tok[1])
            elif tok[0] == 'received':
                args['received'] = tok[1]                
        return ViaHeader(addr, port, **args)
                       
class SIPMessage:
    
    eBranch = re.compile('branch=([a-zA-Z0-9.]+)')

    def __init__(self, body=''):
        self._headers = {}
        self._headers['Max-Forwards'] = str(70)   
        self._headers['Session-Expires'] = str(1800)
        self._headers['Allow'] = 'INVITE, ACK, BYE, OPTIONS'
        self.body = body
        self.branch = ''    
        
    @staticmethod
    def _parse(data):
        try:
            data = data.decode('ascii')
        except:
            pass
        ios = io.StringIO(data)
        l1 = ios.readline() # first line
        headers = {}
        body = ''
        while True:
            h = ios.readline() # cabeçalho
            if not h: break
            h = h.strip()
            if not h: # body
              body = ios.read()
              break
            comma = h.find(':')
            if comma < 0: raise ValueError('esperava um cabeçalho, encontrou: '+h) # erro ???
            hname = h[:comma]
            hval = h[comma+1:].strip()
            if hname in ('From','To'):
                hval = ContactURI.parse(hval)
            headers[hname] = hval
        return (l1, headers, body)

    @staticmethod
    def _parse_first_line(line):
      line = line.split()
      return line[0], line[1]

    @classmethod
    def parse(cls, data):
      l1, headers, body = SIPMessage._parse(data)
      l1 = cls._parse_first_line(l1)
      obj = cls(l1[0], l1[1], body=body)
      for h, val in headers.items():
          obj.set_header(h, val)
      try:
          via = headers['Via']
          m = SIPMessage.eBranch.search(via)
          if m:
              obj.branch = m.groups()[0]
      except:
          pass

      return obj

    @property
    def body(self):
        return self._body
    
    @body.setter
    def body(self, data):
        self._body = data
        if data:
            self._headers['Content-Length'] = str(len(data))
        
    def related_to(self, msg):
        'verifica se esta mensagem é parte da mesma chamada que a mensagem msg'
        return self.CallId == msg.CallId

    @property
    def first_line(self):
        return ''

    @property
    def Contact(self):
        return '<sip:%s>' % self._headers['Contact']
    
    @Contact.setter
    def Contact(self, uri):
        if uri[:4] == 'sip:': uri = uri[4:]
        self._headers['Contact'] = uri

    @property
    def From(self):
        return self._headers['From']
    
    @From.setter
    def From(self, uri):
        if isinstance(uri, str): uri = ContactURI.parse(uri)
        if not isinstance(uri, ContactURI): raise ValueError('uri deve ser str ou ContactURI')
        self._headers['From'] = uri
        
    @property
    def To(self):
        return self._headers['To']
    
    @To.setter
    def To(self, uri):
        print(uri)
        if isinstance(uri, str): uri = ContactURI.parse(uri)
        if not isinstance(uri, ContactURI): raise ValueError('uri deve ser str ou ContactURI')
        self._headers['To'] =uri
        
    @property
    def Via(self):
        return self._headers['Via']
    
    @Via.setter
    def Via(self, hop):
        if isinstance(hop, str): hop = ViaHeader.parse(hop)
        if not isinstance(hop, ViaHeader): raise ValueError('argumento deve ser str ou ViaHeader')
        if not hop.branch:
            hop.branch = self.branch
        self._headers['Via'] = hop
        
    @property
    def CallId(self):
        return self._headers['Call-ID']
    
    @CallId.setter
    def CallId(self, cid):
        self._headers['Call-ID'] = cid
        
    @property
    def ContentType(self):
        return self._headers['Content-Type']
    
    @ContentType.setter
    def ContentType(self, content):
        self._headers['Content-Type'] = str(content)

    def set_header(self, nome, valor):
        self._headers[nome] = valor
        
    def get_header(self, nome):
        return self._headers[nome]

    def __str__(self):
        r = '%s\r\n' % self.first_line 
        lh = list(self._headers.keys())
        lh.sort()
        for h in lh:
            #hh = h.capitalize()            
            hh = h
            try:
                val = getattr(self, hh)
            except:
                val = self._headers[h]    
            r += '%s: %s\r\n' % (hh, val)
        r += '\r\n'
        if self._body:
            r += '%s' % self._body
        return r
    
class SIPRequest(SIPMessage):
    
    Metodos = ('INVITE', 'ACK', 'OPTIONS', 'BYE')
    
    def __init__(self, metodo, uri, **args):
        SIPMessage.__init__(self, args.get('body',''))
        metodo = metodo.upper()
        if not metodo in SIPRequest.Metodos:
            raise ValueError('metodo invalido: %s' % metodo)
        self.metodo = metodo
        self.uri = uri
                
    @property
    def first_line(self):
        return '%s %s SIP/2.0' % (self.metodo, self.uri)
    
    @property
    def CSeq(self):
        return self._headers['CSeq']

    @CSeq.setter
    def CSeq(self, cseq):
        self._headers['CSeq'] = '%d %s' % (cseq, self.metodo)
    
class SIPResponse(SIPMessage):
    
    def __init__(self, status, info, **args):
        SIPMessage.__init__(self, args.get('body',''))
        self.status = status
        self.info = info
        msg = args.get('msg', None)
        if msg:
          self.From = msg.get_header('From')
          self.To = msg.get_header('To')
          self.Via = msg.get_header('Via')
          self.CallId = msg.get_header('Call-ID')
          self.CSeq = msg.get_header('CSeq')
          self.branch = msg.branch
        
    @staticmethod
    def _parse_first_line(line):
      line = line.split()
      return int(line[1]), line[2]
        
    @property
    def first_line(self):
        'Gera a primeira linha da mensagem (linha de status), e a retorna como resultado'
        return 'SIP/2.0 %d %s' % (self.status, self.info)

    @property
    def CSeq(self):
        return self._headers['CSeq']

    @CSeq.setter
    def CSeq(self, cseq):
        self._headers['CSeq'] = cseq

class SIPRequest2(SIPRequest):

    '''Representa requisições SIP ACK. Pode ser criada a partir dos atributos 
do INVITE que iniciou a sessão'''

    def __init__(self, metodo, uri, **args):
        '''Cria um Request "metodo" para a uri informada. Se o parâmetro msg for informado, copia
os atributos da mensagem SIP passada por esse parâmetro.'''
        SIPRequest.__init__(self, metodo, uri, **args)
        msg = args.get('msg', None)
        if msg:
          self.From = msg.get_header('From')
          self.To = msg.get_header('To')
          self.Via = msg.get_header('Via')
          self.CallId = msg.get_header('Call-ID')
          cseq = msg.CSeq.split()
          cseq = int(cseq[0])
          self.CSeq = cseq
          self.branch = msg.branch
          self.set_header('Content-Length', '0')

class SIPAck(SIPRequest2):

    '''Representa requisições SIP ACK. Pode ser criada a partir dos atributos 
do INVITE que iniciou a sessão'''

    def __init__(self, uri, **args):
        '''Cria um ACK para a uri informada. Se o parâmetro msg for informado, copia
os atributos da mensagem SIP passada por esse parâmetro.'''
        SIPRequest2.__init__(self, 'ack', uri, **args)
        
class SIPBye(SIPRequest2):

    '''Representa requisições SIP BYE. Pode ser criada a partir dos atributos 
do INVITE que iniciou a sessão'''

    def __init__(self, uri, **args):
        '''Cria um BYE para a uri informada. Se o parâmetro msg for informado, copia
os atributos da mensagem SIP passada por esse parâmetro.'''
        SIPRequest2.__init__(self, 'bye', uri, **args)

class SDPMedia:

    '''Representa uma descrição de media, incluindo port
UDP e codecs'''

    def __init__(self, kind, port):
        '''Cria uma descrição de media inicialmente sem codecs.
        kind: tipo de media (audio, video)
        port: número de port para recepção da stream'''
        self.kind = kind
        self.port = port
        self.codecs = {}
        self.pars = []

    def add_codec(self, num, desc):
        '''Adiciona um codec.
        num: número do codec
        desc: descrição do codec (ex: PCMU/8000)'''
        if num > 127: raise ValueError('número de codec deve estar entre 0 e 127')
        self.codecs[num] = desc

    def add_attribute(self, param):
      '''Adiciona um atributo (a=...)
         parm: valor do atributo (ex: "framerate=15.000000")'''
      self.pars.append(param)

    def __str__(self):
        '''Gera os atributos m, a da descrição de media para inclusão em uma mensagem SDP'''
        codecs = map(str, self.codecs.keys())
        codecs = ' '.join(codecs)
        r = 'm=%s %d RTP/AVP %s\r\n' % (self.kind, self.port, codecs)
        for num,desc in self.codecs.items():
            r += 'a=rtpmap:%d %s\r\n' % (num, desc)
        for parm in self.pars:
            r += 'a=%s\r\n' % parm
        return r
        
class SDP:

    '''Representa uma mensagem SDP com uma ou mais medias e
lista de codecs'''        
        
    def __init__(self, nome, orig, addr):
        ''''Cria uma mensagem SDP sem descrições de media. Essa mensagem possui
        inicialmente somente os atributos v, o, c, t, s. 
        nome: nome da sessão
        orig: contato do originador da sessão'''
        self.nome = nome
        self.orig = orig
        self.addr = addr
        self.medias = {}

    def add_media(self, media):
        '''adiciona uma descrição de media.
        media: objeto SIPMedia'''
        self.medias[media.kind] = media

    def __str__(self):
      '''Gera uma mensagem SDP pronta para ser encapsulada como corpo de uma mensagem SIP'''
      t1 = int(time.time())
      r = 'v=0\r\n'
      r += 'o=%s %d %d IN IP4 %s\r\n' % (self.orig, t1, t1, self.addr)
      r += 'c=IN IP4 %s\r\n' % self.addr
      r += 't=%d %d\r\n' % (t1, t1+3600)
      r += 's=%s\r\n' % self.nome
      for m in self.medias.values():
        r += str(m)
      return r

