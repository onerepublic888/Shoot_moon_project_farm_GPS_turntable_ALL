
# ComputingPyMultiThreaded.py
# D. Thiebaut
#
# Computes an approximation of Pi by summing up
# a series of terms.  The more terms, the closer
# the approximation.
#
#from __future__ import print_function
import threading
import subprocess
import paho.mqtt.publish as publish

host = "192.168.88.250"
topic = "Client/Datarate"
client_id = "Datarate"
class Datarate_show(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.Datarate = 0
        self._running = False # flag: gps threading running 
        self._stop = False # flag: main threading running
        self.daemon = True
        
    def run(self):
        while not self._stop:
            while (self._running):
                try:
                    proc = subprocess.Popen("iperf3 -c 192.168.88.250 -t 1 -R",shell = True,stdout=subprocess.PIPE)
                    out, err=proc.communicate()
#                    print(out)
                    payload = out.decode().split('\n')[4][38:43] # t=1 [3]  t=2 [4]
#                    print(payload)
                    publish.single(topic, payload, qos=1, hostname=host)
                    self.Datarate = float(payload)
#                    print('Data rate: %s'%(payload))
                except Exception as e:
#                    print('Datarate_show:')
                    print(e)
                    publish.single(topic, '0', qos=1, hostname=host)
                    self.Datarate = 0
                    break
        print('exit Datarate_show loop')
            
    # method: resume main thread
    def resume(self):
        self._running = True
    # method: suspend main thread
    def suspend(self):
        self._running = False

    # method: stop main thread    
    def stop(self):
        self._stop = True
        self._running = False
