from matplotlib import pyplot as plt
import requests
import pandas as pd
import sys, getopt, math, os.path

zone = ''
groupby = 'HOUR'
output = ''

def main(argv):
	global zone
	global groupby
	global output

	try:
		opts, args = getopt.getopt(argv,"hz:g:o:",["zone=","groupby=","output="])
	except getopt.GetoptError as err:
		print(err)
		sys.exit(1)

	if not opts:
		print('Usage:')
		print('elzoneplot.py -z <SE|SE1|SE2|SE3|SE4> -g <MONTH|WEEK|DAY|HOUR(default)> -o <std|oFile>')
		sys.exit(1)
	for opt, arg in opts:
		if opt == '-h':
			print('Usage:')
			print('elzoneplot.py -z <SE|SE1|SE2|SE3|SE4> -g <MONTH|WEEK|DAY|HOUR(default)> -o <std|oFile>')
			sys.exit(1)
		elif opt in ("-z", "--zone"):
			arg=arg.upper()
			if arg == 'SE' or arg == 'SE1' or arg == 'SE2' or arg == 'SE3' or arg == 'SE4':
				zone = arg
#			elif  arg == '':
#				zone = 'SE'
			else:
				sys.exit('Not a known zone: ', arg)
		elif opt in ("-g", "--group"):
			arg=arg.upper()
			if arg == 'MONTH' or arg == 'WEEK' or arg == 'DAY' or arg == 'HOUR':
				groupby = arg
			elif arg == '':
				groupby = 'HOUR'
			else:
				sys.exit('Not a known groupby command: ', arg)
		elif opt in ("-o", "--output"):
			if arg.lower() == 'std':
				output = 'STDOUT'
			else:
				output = arg

	print('Zone=', zone, ', Groupby=', groupby, ', Output=', output, sep='')

	# Get data from file "Statistik per elområde och timme, 2022.xlsx"
	# Statistics available at https://www.svk.se/om-kraftsystemet/kraftsystemdata/elstatistik/

	fname='Statistik per elområde och timme, 2022.xlsx'
	if not os.path.isfile(fname):
		url = 'https://www.svk.se/siteassets/1.om-kraftsystemet/kraftsystemdata/statistik/elomrade-och-timme/arkiverade/timvarden-2022-01-12.xls' #Data for 2022
		r = requests.get(url)
		open(fname, 'wb').write(r.content)
	
	# Put the data in a dataframe.
	df = pd.read_excel(fname, header=0, skiprows=4)	#, nrows=10
#	df = pd.read_excel(fname, header=0, skiprows=4, nrows=100)
	pd.set_option('display.max_rows', None)

	df2 = pd.DataFrame()
	
	df2['date'] = pd.to_datetime(df.iloc[:, 0])
	df2['datetime'] = df.iloc[:, 0]
	df2['timestamp'] = pd.to_datetime(df.iloc[:, 0]).astype(int)/ 10**9
	df2['year'] = df.iloc[:, 0].dt.isocalendar().year
	df2['week'] = df.iloc[:, 0].dt.isocalendar().week
	
	df2['consumption_SE1']= df.iloc[:, [1,5,9,13,38,42]].sum(axis=1)
	df2['consumption_SE2']= df.iloc[:, [2,6,10,14,39,43]].sum(axis=1)
	df2['consumption_SE3']= df.iloc[:, [3,7,11,15,40,44]].sum(axis=1)
	df2['consumption_SE4']= df.iloc[:, [4,8,12,16,41,45]].sum(axis=1)
	df2['consumption_SE']= df2['consumption_SE1']+df2['consumption_SE2']+df2['consumption_SE3']+df2['consumption_SE4']
	
	df2['production_SE1']= df.iloc[:, [17,21,25,30,34]].sum(axis=1)
	df2['production_SE2']= df.iloc[:, [18,22,26,31,35]].sum(axis=1)
	df2['production_SE3']= df.iloc[:, [19,23,27,29,32,36]].sum(axis=1)
	df2['production_SE4']= df.iloc[:, [20,24,28,33,37]].sum(axis=1)
	df2['production_SE']= df2['production_SE1']+df2['production_SE2']+df2['production_SE3']+df2['production_SE4']
	
	df2['balance_SE']= df2['consumption_SE']+df2['production_SE']
	df2['balance_SE1']= df2['consumption_SE1']+df2['production_SE1']
	df2['balance_SE1']= df2['consumption_SE1']+df2['production_SE1']
	df2['balance_SE2']= df2['consumption_SE2']+df2['production_SE2']
	df2['balance_SE3']= df2['consumption_SE3']+df2['production_SE3']
	df2['balance_SE4']= df2['consumption_SE4']+df2['production_SE4']

	#D = calendar day
	#W = weekly frequency
	#M = month end frequency
	colDict={'datetime':'first','year':'first','week':'first','balance_SE':'sum','balance_SE1':'sum','balance_SE2':'sum','balance_SE3':'sum','balance_SE4':'sum'}
	if groupby == '' or groupby == 'HOUR':
		df3=df2[['datetime','year','week','balance_SE','balance_SE1','balance_SE2','balance_SE3','balance_SE4']].copy()
		df3['hour']=df3.index
		df3['y']=df3['hour'].apply(lambda x: int(x/120))
		df3['x']=df3['hour'].apply(lambda x: int(x%120))
	elif groupby == 'DAY':
		df3=df2.groupby([pd.Grouper(key='date', freq='D')], as_index=False).agg(colDict)
		df3['hour']=df3.index
		df3['y']=df3['hour'].apply(lambda x: int(x/20))
		df3['x']=df3['hour'].apply(lambda x: int(x%20))
	elif groupby == 'WEEK':
		df3=df2.groupby([pd.Grouper(key='date', freq='W')], as_index=False).agg(colDict)
		df3['hour']=df3.index
		df3['y']=df3['hour'].apply(lambda x: int(x/7))
		df3['x']=df3['hour'].apply(lambda x: int(x%7))
	elif groupby == 'MONTH':
		df3=df2.groupby([pd.Grouper(key='date', freq='M')], as_index=False).agg(colDict)
		df3['hour']=df3.index
		df3['y']=df3['hour'].apply(lambda x: int(x/3))
		df3['x']=df3['hour'].apply(lambda x: int(x%3))


	export_color = 'orange'
	import_color = 'grey'
	#df['color'] = df['balance'].apply(lambda x: export_color if x < 0 else import_color)
	if zone == 'SE':
		df3['color'] = df3['balance_SE'].apply(lambda x: export_color if x > 0 else import_color)
	elif zone == 'SE1':
		df3['color'] = df3['balance_SE1'].apply(lambda x: export_color if x > 0 else import_color)
	elif zone == 'SE2':
		df3['color'] = df3['balance_SE2'].apply(lambda x: export_color if x > 0 else import_color)
	elif zone == 'SE3':
		df3['color'] = df3['balance_SE3'].apply(lambda x: export_color if x > 0 else import_color)
	elif zone == 'SE4':
		df3['color'] = df3['balance_SE4'].apply(lambda x: export_color if x > 0 else import_color)
	
	# Plot the data.
	#ax = df.plot(kind='scatter', x='x', y='y', c='color')
	ax = df3.plot(kind='scatter', x='x', y='y', c='color')
	
	# Hide irrelevant names on axes.
	ax.axes.get_xaxis().set_visible(False)
	ax.axes.get_yaxis().set_visible(False)
	
	# Show plot.
	plt.show()
	
	if output == 'STDOUT':
		print(df3)
	elif output != '':
		print('Saving dataframe to: ', output, sep='')
		df.to_csv(output, sep='\t', encoding='utf-8')

if __name__ == "__main__":
	main(sys.argv[1:])