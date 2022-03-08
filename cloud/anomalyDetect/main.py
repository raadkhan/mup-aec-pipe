from google.cloud import firestore
from datetime import datetime, timedelta
from statistics import mean, pstdev
from math import exp

client = firestore.Client()

frequency_profile = {
    'type': 'high',
    'value': 24 # msgs/day
}    

anomaly_profile = {
    'delta': 1, # days
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

def anomalyDetect(data, context):
    full_path = context.resource.split('/documents/')[1].split('/')
    collection_path = full_path[0]
    document_path = '/'.join(full_path[1:])

    sens_dps = client.collection(collection_path)

    sens_dp_imei = data['value']['fields']['imei']['integerValue']
    sens_dp_type = data['value']['fields']['type']['stringValue']
    sens_dp_timestamp = data['value']['fields']['timestamp']['integerValue']
    sens_dp_value = data['value']['fields']['value']['doubleValue']
    sens_dp_unit = data['value']['fields']['unit']['stringValue']

    sens_dp = {
        'imei': sens_dp_imei,
        'type': sens_dp_type,
        'timestamp': sens_dp_timestamp,
        'value': sens_dp_value,
        'unit': sens_dp_unit
    }
    
    present = datetime.fromtimestamp(int(sens_dp_timestamp)/1000)
    past = (timedelta(days=-anomaly_profile['delta']) + present).timestamp()*1000
    
    sens_dp_values = sens_dps.where(
        'imei', '==', sens_dp_imei).where(
        'type', '==', sens_dp_type).where(
        'timestamp', '>=', past).where(
        'timestamp', '!=', sens_dp_timestamp).where(
        'anomaly', '==', False).stream()

    values = []
    for sens_dp_value in sens_dp_values:
        values.append(sens_dp_value.to_dict().get('value'))
        
    if len(values) >= anomaly_profile['delta']*frequency_profile['value']: 
        avg = mean(values)
        stddev = pstdev(values)
        up_limit = avg + 3*exp(stddev/avg)
        lo_limit = avg - 3*exp(stddev/avg)
        print(f'{up_limit} {avg} {lo_limit}')
    else:
        print('calibrating...')
        return
        
    if sens_dp['value'] < lo_limit or sens_dp['value'] > up_limit:
        print(f"check out your property: detected an anomalous {sens_dp['type']} of {sens_dp['value']:.3f} {sens_dp['unit']} at {present}")
        sens_dps.document(document_path).set({'anomaly': True}, merge=True)
    else:
        print(f"all is well at your property: {sens_dp['type']} was {sens_dp['value']:.3f} {sens_dp['unit']} just now")