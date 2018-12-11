import sip_register

obj_sip_reg = sip_register.sip_register('192.168.1.221', 5060, '192.168.1.1', 5060, 6031)
reg_register = obj_sip_reg.register()
try:
    obj_sip_reg.send(reg_register)
except:
    print('Não foi possível registrar no servidor')

#reg_register = obj_sip_reg.deregister()
#obj_sip_reg.send(reg_register)