from umqtt.robust import MQTTClient
import ujson as json
from time import sleep


class Mqttsender:

    def __init__(self, mqtt, ip, uniqid, clean_session=False):
        self.server = mqtt['server']
        self.user = mqtt['user']
        self.password = mqtt['pass']
        self.uniqid = uniqid
        self.topic_ping = mqtt['object'] + '/globalping'
        self.topic_lastwill = mqtt['object'] + '/status/' + self.uniqid
        self.topic_management = mqtt['object'] + '/management/' + self.uniqid
        self.topic_state = mqtt['object'] + '/state/' + self.uniqid
        self.keepalive = int(mqtt['keepalive'])
        self.ip = ip
        self.clean_session = clean_session
        self.connected = False
        self.c = MQTTClient(self.uniqid, server=self.server, user=self.user, password=self.password,
                            keepalive=self.keepalive)
        if self.keepalive:
            self.c.set_last_will(topic=self.topic_lastwill, msg='offline', retain=True)
        self.message_buffer = ''

        #------- management commands ----------
        #TODO dehardcode maintenance topics and keywords!
        self.ping = 'PING'
        self.repl_on = 'ZAVULON'
        self.repl_off = 'ISAAK'
        self.reboot = 'ZARATUSTRA'
        self.get_state = 'STATE'
        self.init = 'INITIALIZE'

    def connect(self):
        while not self.connected:
            try:
                print('Connecting as ', self.uniqid, '...')
                self.connected = self.c.connect(clean_session=self.clean_session)
                print('Broker at ' + self.server + ' connected')
                self.management_subscribe()
            except Exception as e:
                print('Connecting error: ', e)
                sleep(1)

    def management_subscribe(self):
        is_error = False
        print ('Subscribing maintenance topics...')
        try:
            self.subscribe(self.topic_ping, self.manage)
            self.subscribe(self.topic_management, self.manage)
        except Exception as e:
            print ("Could not subscribe")
            print (e)
            is_error = True
        finally:
            return is_error

    def send(self, topic, message, retain=True):
        print('Sending ' + str(message) + ' in topic ' + str(topic) + '...')
        try:
            if not isinstance(topic, bytes):
                topic = topic.encode()
            if not isinstance(message, bytes):
                message = message.encode()
            self.c.publish(topic, message, retain=retain)
            print ('Data sent')
            is_error = False
        except Exception as e:
            print ("Could not send data")
            print (e)
            is_error = True
        finally:
            return (is_error)

    def subscribe(self, topic, sub_cb):
        is_error = False
        try:
            if not isinstance(topic, bytes):
                topic = topic.encode()
            self.c.set_callback(sub_cb)
            self.c.subscribe(topic)
            print ('Subscribed: '+topic.decode())
            is_error = False
        except Exception as e:
            print("Could not subscribe")
            print(e)
            is_error = True
        finally:
            return(is_error)

    def manage(self, command):
        print ('Maintenance command received')
        if command == self.ping:
            self.send(self.topic_lastwill, self.ip)
        if command == self.repl_on:
            import webrepl
            webrepl.start()
        if command == self.repl_off:
            print('Turning repl off')
            import webrepl
            webrepl.stop()
        if command == self.reboot:
            print ('Rebooting...')
            import machine as m
            m.reset()
        if command == self.init:
            conf = get_config('conf.json')
            conf['inited'] = '1'
            write_config('conf.json', conf)


def get_config(filename):
    try:
        with open(filename) as f:
            config = json.loads(f.read())
            return (config)
    except (OSError, ValueError):
        print("Couldn't load config ", filename)
        print('Starting webrepl and reboot after 2 min.')
        import webrepl
        webrepl.start()
        sleep(120)
        import machine
        machine.reset()


def write_config(filename, conf):
    try:
        with open(filename, 'w') as f:
            f.write(json.dumps(conf))
    except (OSError, ValueError):
        print("Couldn't open config ", filename)

