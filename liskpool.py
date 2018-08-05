import requests
import json
import sys
import time

if len (sys.argv) > 2 and sys.argv [1] == '-c':
	cfile = sys.argv [2]
else:
	cfile = 'config.json'
	
try:
	conf = json.load (open (cfile, 'r'))
except:
	print ('Unable to load config file.')
	sys.exit ()
	
if 'logfile' in conf:
	LOGFILE = conf['logfile']
else:
	LOGFILE = 'poollogs.json'


def loadLog ():
	try:
		data = json.load (open (LOGFILE, 'r'))
	except:
		data = {
			"lastpayout": 0, 
			"accounts": {},
			"skip": []
		}
	return data
	
	
def saveLog (log):
	json.dump (log, open (LOGFILE, 'w'), indent=4, separators=(',', ': '))
	


def estimatePayouts (log):
	if conf['coin'].lower () == 'xpx':
		uri = conf['node'] + '/api/delegates/forging/getForgedByAccount?generatorPublicKey=' + conf['pubkey']
		d = requests.get (uri)
		lf = log['lastforged']
		rew = int (d.json ()['rewards']) 
		log['lastforged'] = rew 
		rew = rew - lf
	elif conf['coin'].lower () == 'kapu':
		uri = conf['node'] + '/api/delegates/forging/getForgedByAccount?generatorPublicKey=' + conf['pubkey']
		d = requests.get (uri)
		lf = log['lastforged']
		rew = int (d.json ()['rewards']) 
		log['lastforged'] = rew 
		rew = rew - lf
	else:
		uri = conf['node'] + '/api/delegates/forging/getForgedByAccount?generatorPublicKey=' + conf['pubkey'] + '&start=' + str (log['lastpayout']) + '&end=' + str (int (time.time ()))
		d = requests.get (uri)
		rew = d.json ()['rewards']

	forged = (int (rew) / 100000000) * conf['percentage'] / 100
	print ('To distribute: %f %s' % (forged, conf['coin']))
	
	if forged < 0.1:
		return ([], log)
		
	d = requests.get (conf['node'] + '/api/delegates/voters?publicKey=' + conf['pubkey']).json ()
	
	weight = 0.0
	payouts = []
	
	for x in d['accounts']:
		if x['balance'] == '0' or x['address'] in conf['skip']:
			continue
			
		weight += float (x['balance']) / 100000000
		
	print ('Total weight is: %f' % weight)
	
	for x in d['accounts']:
		if int (x['balance']) == 0 or x['address'] in conf['skip']:
			continue
			
		payouts.append ({ "address": x['address'], "balance": (float (x['balance']) / 100000000 * forged) / weight})
		#print (float (x['balance']) / 100000000, payouts [x['address']], x['address'])
		
	return (payouts, log, forged)
	
	
def pool ():
	log = loadLog ()
	
	(topay, log, forged) = estimatePayouts (log)
	
	if len (topay) == 0:
		print ('Nothing to distribute, exiting...')
		return
		
	f = open ('payments.json', 'w')
	f.write('{\"transactions\": [\n')
	index = 0
	for x in topay:
		if not (x['address'] in log['accounts']) and x['balance'] != 0.0:
			log['accounts'][x['address']] = { 'pending': 0.0, 'received': 0.0 }
			
		if x['balance'] < conf['minpayout'] and x['balance'] > 0.0:
			log['accounts'][x['address']]['pending'] += x['balance']
			continue
		if index > 0: 
			f.write (',\n')
		log['accounts'][x['address']]['received'] += x['balance']	
		data = { "secret": conf['secret'], "amount": int (x['balance'] * 100000000), "recipientId": x['address'] }
		if conf['secondsecret'] != None:
			data['secondSecret'] = conf['secondsecret']		
		f.write (json.dumps (data))
		index += 1
	index = 0
	f.write('],\n \"transactionsPending\": [\n')
	for y in log['accounts']:
		if log['accounts'][y]['pending'] > conf['minpayout']:
			data = { "secret": conf['secret'], "amount": int (log['accounts'][y]['pending'] * 100000000), "recipientId": y }
			if conf['secondsecret'] != None:
				data['secondSecret'] = conf['secondsecret']			
			f.write (json.dumps (data))
			if index < (len (log['accounts']) - 1):
				f.write (',\n')
			index += 1
			log['accounts'][y]['received'] += log['accounts'][y]['pending']
			log['accounts'][y]['pending'] = 0.0
	f.write('],\n \"donations\": [\n');		
	# Donations
	index = 0
	if 'donations' in conf:
		for y in conf['donations']:
			data = { "secret": conf['secret'], "amount": int (conf['donations'][y] * 100000000), "recipientId": y }
			if conf['secondsecret'] != None:
				data['secondSecret'] = conf['secondsecret']			
			f.write (json.dumps (data))
			if index < (len (conf['donations']) - 1):
				f.write (',\n')
			index += 1
	f.write('],\n \"donationsPercentage\": [\n');		
	# Donation percentage
	index = 0
	if 'donationspercentage' in conf:
		for y in conf['donationspercentage']:
			am = (forged * conf['donationspercentage'][y]) / 100
			data = { "secret": conf['secret'], "amount": int (am * 100000000), "recipientId": y }
			if conf['secondsecret'] != None:
				data['secondSecret'] = conf['secondsecret']			
			f.write (json.dumps (data))
			if index < (len (conf['donationspercentage']) - 1):
				f.write (',\n')
			index += 1
	f.write(']\n}\n')
	f.close ()
	
	log['lastpayout'] = int (time.time ())
	
	print (json.dumps (log, indent=4, separators=(',', ': ')))
	
	if len (sys.argv) > 1 and sys.argv[1] == '-y':
		print ('Saving...')
		saveLog (log)
	else:
		yes = input ('save? y/n: ')
		if yes == 'y':
			saveLog (log)
			
			

if __name__ == "__main__":
	pool ()
