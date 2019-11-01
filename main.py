#!/usr/bin/python3
import syrabond
from time import sleep


sh = syrabond.API('sh', listen=True)
i = 20
while i > 0:
    sh.facility.listener.check_for_messages()
    sleep(0.1)
    i -= 1
sh.facility.message_handler()
sh.facility.listener.disconnect()
print('Датчики:')
for r in sh.facility.resources:
    res = sh.facility.resources[r]
    if res.type == 'sensor':
        print('{} ({}): {}'.format(res.hrn, res.uid, res.get_state()))
print('Переключатели:')
i = 0
switches = {}
for r in sh.facility.resources:
    res = sh.facility.resources[r]
    if res.type == 'switch':
        i += 1
        print('{}) {} ({}): {}'.format(i, res.hrn, res.uid, res.get_state()))
        switches.update({i: res})
while True:
    choice = input('Индекс (#) или API (A)? ')
    if choice.isdigit() and int(choice) in switches:
        com = input('on (1) | off (0) | reboot (r) | webrepl (w)')
        r = switches[int(choice)]
        if com == '1':
            r.on()
        elif com == '0':
            r.off()
        elif com == 'r':
            r.device_reboot()
        elif com == 'w':
            r.webrepl('on')
        else:
            break
        sleep(0.5)
    elif choice == 'A':
        base = input('Укажите API-строку')
        if not sh.direct(base):
            print('Wrong API usage.')
    else:
        break

    print('Список переключателей:')
    i = 0
    switches = {}
    for r in sh.facility.resources:
        res = sh.facility.resources[r]
        if res.type == 'switch':
            i += 1
            print('{}) {} ({}): {}'.format(i, res.hrn, res.uid, res.get_state()))
            switches.update({i: res})
