from collections import deque
from statistics import mean, pstdev
from datetime import datetime
from random import random, uniform, gauss
from time import sleep
import matplotlib.pyplot as plt

# updated by frontend, persist in backend:
frequency_profile = {
    'freq': 20 # updates/day
}

anomaly_profile = {
    'mem': 1, # days
    'breath_voc_lo_limit': None,
    'breath_voc_up_limit': None,
    'co2e_lo_limit': None,
    'co2e_up_limit': None,
    'humidity_lo_limit': None,
    'humidity_up_limit': None,
    'iaq_lo_limit': None,
    'iaq_up_limit': None,
    'pressure_lo_limit': None,
    'pressure_up_limit': None,
    'temp_lo_limit': None,
    'temp_up_limit': None
}

print('welcome to the anomaly detection tester...')
print('enter the sensor type:')
sens_dp_type = input()
print('enter the sensor unit:')
sens_dp_unit = input() # ug/m3, co2e, %, iaq, pa, °C

# updated by pipe, persist in backend:
sens_dp = {
    'type': sens_dp_type,
    'timestamp': 0,
    'value': 0,
    'unit': sens_dp_unit 
}

def update_frequency_profile(frequency_profile):
    # TODO: implement and connect to frontend event
    return

def update_anomaly_profile(anomaly_profile):
    # TODO: implement and connect to frontend event
    return

def detect_anomaly(ax, sens_dp, sens_dp_values, anomaly_profile): # connect to pipe event
    lo_limit_key = '{}_lo_limit'.format(sens_dp['type'])
    up_limit_key = '{}_up_limit'.format(sens_dp['type'])

    if anomaly_profile[lo_limit_key] == None or anomaly_profile[up_limit_key] == None: # auto mode
        if len(sens_dp_values) >= anomaly_profile['mem']*frequency_profile['freq']: # calibrating
            avg = mean(sens_dp_values)
            stddev = pstdev(sens_dp_values)
            lo_limit = avg - 3*stddev
            up_limit = avg + 3*stddev
        else:
            sens_dp_values.append(sens_dp['value'])
            return
    else: # man mode
        lo_limit = anomaly_profile[lo_limit_key]
        up_limit = anomaly_profile[up_limit_key]
        
    # connect to frontend message
    if sens_dp['value'] < lo_limit or sens_dp['value'] > up_limit:
        print('check out your property: we detected an anomalous {} of {:.3f} {} at {}'.format(
            sens_dp['type'], sens_dp['value'], sens_dp['unit'], sens_dp['timestamp'])) 

        ax.plot(sens_dp['timestamp'], sens_dp['value'], 'rx')
    else:
        print('all is well at your property: {} was {:.3f} {} just now'.format(
            sens_dp['type'], sens_dp['value'], sens_dp['unit']))
        sens_dp_values.append(sens_dp['value'])

        ax.plot(sens_dp['timestamp'], sens_dp['value'], 'bo')

    plt.pause(1) # pause to let GUI event loop run
    
sens_dp_values = deque()

plt.ion()
fig, ax = plt.subplots()
plt.title("anomaly detector test")
plt.xlabel("datetime (utc)")
plt.ylabel("{} ({})".format(sens_dp['type'], sens_dp['unit']))

try:
    while (True):
            # simulate an anomaly 10% of the time
            if random() >= 0.90 and len(sens_dp_values) >= anomaly_profile['mem']*frequency_profile['freq']:
                sens_dp['timestamp']  = datetime.utcnow()

                if sens_dp['type'] == 'breath_voc':
                    sens_dp['value'] = uniform(0.80, 0.90)
                elif sens_dp['type'] == 'co2e':
                    sens_dp['value'] = uniform(609, 611)
                elif sens_dp['type'] == 'humidity':
                    sens_dp['value'] = uniform(25, 30)
                elif sens_dp['type'] == 'iaq':
                    sens_dp['value'] = uniform(150, 200)
                elif sens_dp['type'] == 'pressure':
                    sens_dp['value'] = uniform(200, 700)
                elif sens_dp['type'] == 'temp':
                    sens_dp['value'] = uniform(-25, 25)
                else:
                    raise Exception('sensor type: {} does not exist!'.format(sens_dp['type']))
            # simulate sensing in my room
            else:
                sens_dp['timestamp'] = datetime.utcnow()

                if sens_dp['type'] == 'breath_voc':
                    sens_dp['value'] = gauss(0.70, 0.01)
                elif sens_dp['type'] == 'co2e':
                    sens_dp['value'] = gauss(590, 6)
                elif sens_dp['type'] == 'humidity':
                    sens_dp['value'] = gauss(55, 0.5)
                elif sens_dp['type'] == 'iaq':
                    sens_dp['value'] = gauss(80, 4)
                elif sens_dp['type'] == 'pressure':
                    sens_dp['value'] = gauss(1005, 2)
                elif sens_dp['type'] == 'temp':
                    sens_dp['value'] = gauss(30, 1)
                else:
                    raise Exception('sensor type: {} does not exist!'.format(sens_dp['type']))

            detect_anomaly(ax, sens_dp, sens_dp_values, anomaly_profile) # test anomaly detection

except Exception as e:
    print(e)