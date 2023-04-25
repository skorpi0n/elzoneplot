from matplotlib import pyplot as plt
import requests
import pandas as pd
import sys, getopt, math, os.path
from datetime import datetime

year = datetime.now().year
zone = ''
groupby = 'HOUR'
output = ''

def main(argv):
	global year
	global zone
	global groupby
	global output

	try:
		opts, args = getopt.getopt(argv,"hy:z:g:o:",["year=","zone=","groupby=","output="])
	except getopt.GetoptError as err:
		print(err)
		sys.exit(1)

	if not opts:
		print('Usage:')
		print('elzoneplot.py -y <2007-> -z <SE|SE1|SE2|SE3|SE4> -g <MONTH|WEEK|DAY|HOUR(default)> -o <plot|std|oFile>')
		sys.exit(1)
	for opt, arg in opts:
		if opt == '-h':
			print('Usage:')
			print('elzoneplot.py -y <2007-> -z <SE|SE1|SE2|SE3|SE4> -g <MONTH|WEEK|DAY|HOUR(default)> -o <plot|std|oFile>')
			sys.exit(1)
		elif opt in ("-y", "--year"):
			arg = int(arg)
			if arg >= 2007 and arg <= year:
				year = arg
#			elif  arg == '':
#				zone = 'SE'
			else:
				print('Specified year ', arg, ' is not within range 2007 - ', year, sep='')
				sys.exit()

		elif opt in ("-z", "--zone"):
			arg=arg.upper()
			if arg == 'SE' or arg == 'SE1' or arg == 'SE2' or arg == 'SE3' or arg == 'SE4':
				zone = arg
#			elif  arg == '':
#				zone = 'SE'
			else:
				print('Not a known zone: ', arg)
				sys.exit()
		elif opt in ("-g", "--group"):
			arg=arg.upper()
			if arg == 'MONTH' or arg == 'WEEK' or arg == 'DAY' or arg == 'HOUR':
				groupby = arg
			elif arg == '':
				groupby = 'HOUR'
			else:
				print('Not a known groupby command: ', arg)
				sys.exit()
		elif opt in ("-o", "--output"):
			if arg.lower() == 'std':
				output = 'STDOUT'
			elif arg.lower() == 'plot':
				output = 'PLOT'
			else:
				output = arg

	print('Year=', year, ', Zone=', zone, ', Groupby=', groupby, ', Output=', output, sep='')

	# Get data from file "Statistik per elområde och timme, 2022.xlsx"
	# Statistics available at https://www.svk.se/om-kraftsystemet/kraftsystemdata/elstatistik/

	urlDict={
		2007:'https://www.svk.se/siteassets/1.om-kraftsystemet/kraftsystemdata/statistik/elomrade-och-timme/arkiverade/timvarden_2007.xls',
		2008:'https://www.svk.se/siteassets/1.om-kraftsystemet/kraftsystemdata/statistik/elomrade-och-timme/arkiverade/timvarden2008.xls',
		2009:'https://www.svk.se/siteassets/1.om-kraftsystemet/kraftsystemdata/statistik/elomrade-och-timme/arkiverade/timvarden2009.xls',
		2010:{
			0:'https://www.svk.se/siteassets/1.om-kraftsystemet/kraftsystemdata/statistik/elomrade-och-timme/arkiverade/timvarden-2010-01-till-06.xls',
			1:'https://www.svk.se/siteassets/1.om-kraftsystemet/kraftsystemdata/statistik/elomrade-och-timme/arkiverade/timvarden-2010-07-till-12.xls'
		},
		2011:'https://www.svk.se/siteassets/1.om-kraftsystemet/kraftsystemdata/statistik/elomrade-och-timme/arkiverade/timvarden-2011-01-12.xls',
		2012:'https://www.svk.se/siteassets/1.om-kraftsystemet/kraftsystemdata/statistik/elomrade-och-timme/arkiverade/timvarden-2012-01-12.xls',
		2013:'https://www.svk.se/siteassets/1.om-kraftsystemet/kraftsystemdata/statistik/elomrade-och-timme/arkiverade/timvarden-2013-01-12.xls',
		2014:'https://www.svk.se/siteassets/1.om-kraftsystemet/kraftsystemdata/statistik/elomrade-och-timme/arkiverade/timvarden-2014-01-12.xls',
		2015:'https://www.svk.se/siteassets/1.om-kraftsystemet/kraftsystemdata/statistik/elomrade-och-timme/arkiverade/statistik-per-timme-och-elomrade-2015.xls',
		2016:'https://www.svk.se/siteassets/1.om-kraftsystemet/kraftsystemdata/statistik/elomrade-och-timme/arkiverade/timvarden-2016-01-12.xls',
		2017:'https://www.svk.se/siteassets/1.om-kraftsystemet/kraftsystemdata/statistik/elomrade-och-timme/arkiverade/timvarden-2017-01-12.xls',
		2018:'https://www.svk.se/siteassets/1.om-kraftsystemet/kraftsystemdata/statistik/elomrade-och-timme/arkiverade/timvarden-2018-01-12.xls',
		2019:'https://www.svk.se/siteassets/1.om-kraftsystemet/kraftsystemdata/statistik/elomrade-och-timme/arkiverade/timvarden-2019-01-12.xls',
		2020:'https://www.svk.se/siteassets/1.om-kraftsystemet/kraftsystemdata/statistik/elomrade-och-timme/arkiverade/timvarden-2020-01-12.xls',
		2021:'https://www.svk.se/siteassets/1.om-kraftsystemet/kraftsystemdata/statistik/elomrade-och-timme/arkiverade/timvarden-2021-01-12.xls',
		2022:'https://www.svk.se/siteassets/1.om-kraftsystemet/kraftsystemdata/statistik/elomrade-och-timme/arkiverade/timvarden-2022-01-12.xls',
		2023:'https://www.svk.se/siteassets/1.om-kraftsystemet/kraftsystemdata/statistik/elomrade-och-timme/timvarden-2023-01-02.xls'
	}
	
	#This dict contains the indexes for the consumption columns by year
	consumptionDict={
		2007:{
			'SE1':[2,6,10,14,18],
			'SE2':[3,7,11,15,19],
			'SE3':[4,8,12,16,20],
			'SE4':[5,9,13,17,21]
		},
		2008:{
			'SE1':[2,6,10,14,18],
			'SE2':[3,7,11,15,19],
			'SE3':[4,8,12,16,20],
			'SE4':[5,9,13,17,21]
		},
		2009:{
			'SE1':[2,6,10,14,18],
			'SE2':[3,7,11,15,19],
			'SE3':[4,8,12,16,20],
			'SE4':[5,9,13,17,21]
		},
		2010:{
			0:{
				'SE1':[2,6,10,14,18],
				'SE2':[3,7,11,15,19],
				'SE3':[4,8,12,16,20],
				'SE4':[5,9,13,17,21]
			},
			1:{
				'SE1':[1,  8,12,35,39],	#No Ospec. förbrukning
				'SE2':[2,5,9,13,36,40],
				'SE3':[3,6,10,14,37,41],
				'SE4':[4,7,11,15,38,42]
			}
		},
		2011:{
			'SE1':[1,  8,32,36],	#No Ospec. förbrukning
			'SE2':[2,5,9,33,37],
			'SE3':[3,6,10,34,38],
			'SE4':[4,7,11,35,39]
		},
		2012:{
			'SE1':[1,5,9,34,38],
			'SE2':[2,6,10,35,39],
			'SE3':[3,7,11,36,40],
			'SE4':[4,8,12,37,41]
		},
		2013:{
			'SE1':[1,5,9,33,37],
			'SE2':[2,6,10,34,38],
			'SE3':[3,7,11,35,39],
			'SE4':[4,8,12,36,40]
		},
		2014:{
			'SE1':[1,5,9,33,37],
			'SE2':[2,6,10,34,38],
			'SE3':[3,7,11,35,39],
			'SE4':[4,8,12,36,40]
		},
		2015:{
			'SE1':[1,5,9,33,37],
			'SE2':[2,6,10,34,38],
			'SE3':[3,7,11,35,39],
			'SE4':[4,8,12,36,40]
		},
		2016:{
			'SE1':[1,5,9,34,38],
			'SE2':[2,6,10,35,39],
			'SE3':[3,7,11,36,40],
			'SE4':[4,8,12,37,41]
		},
		2017:{
			'SE1':[1,5,9,34,38],
			'SE2':[2,6,10,35,39],
			'SE3':[3,7,11,36,40],
			'SE4':[4,8,12,37,41]
		},
		2018:{
			'SE1':[1,5,30,34],
			'SE2':[2,6,31,35],
			'SE3':[3,7,32,36],
			'SE4':[4,8,33,37]
		},
		2019:{
			'SE1':[1,5,9,13,38,42],
			'SE2':[2,6,10,14,39,43],
			'SE3':[3,7,11,15,40,44],
			'SE4':[4,8,12,16,41,45]
		},
		2020:{
			'SE1':[1,5,9,13,38,42],
			'SE2':[2,6,10,14,39,43],
			'SE3':[3,7,11,15,40,44],
			'SE4':[4,8,12,16,41,45]
		},
		2021:{
			'SE1':[1,5,9,13,38,42],
			'SE2':[2,6,10,14,39,43],
			'SE3':[3,7,11,15,40,44],
			'SE4':[4,8,12,16,41,45]
		},
		2022:{
			'SE1':[1,5,9,13,38,42],
			'SE2':[2,6,10,14,39,43],
			'SE3':[3,7,11,15,40,44],
			'SE4':[4,8,12,16,41,45]
		},
		2023:{
			'SE1':[1,5,9,13,38,42],
			'SE2':[2,6,10,14,39,43],
			'SE3':[3,7,11,15,40,44],
			'SE4':[4,8,12,16,41,45]
		}
	}

	#This dict contains the indexes for the production columns by year
	productionDict={
		2007:{
			'SE1':[22,26,30,34,   38],	#No nuclear
			'SE2':[23,27,31,35,   39],	#No nuclear
			'SE3':[24,28,32,36,40,42],
			'SE4':[25,29,33,37,41,43]
		},
		2008:{
			'SE1':[22,26,30,34,   38],	#No nuclear
			'SE2':[23,27,31,35,   39],	#No nuclear
			'SE3':[24,28,32,36,40,42],
			'SE4':[25,29,33,37,41,43]
		},
		2009:{
			'SE1':[22,26,30,34,   38],	#No nuclear
			'SE2':[23,27,31,35,   39],	#No nuclear
			'SE3':[24,28,32,36,40,42],
			'SE4':[25,29,33,37,41,43]
		},
		2010:{
			0:{
				'SE1':[22,26,30,34,   38],	#No nuclear
				'SE2':[23,27,31,35,   39],	#No nuclear
				'SE3':[24,28,32,36,40,42],
				'SE4':[25,29,33,37,41,43]
			},
			1:{
				'SE1':[16,20,25,   26,30,43],	#No nuclear
				'SE2':[17,21,26,   27,32,44],	#No nuclear
				'SE3':[18,22,27,24,28,33,45],
				'SE4':[19,23,28,25,29,34,46]
			}
		},
		2011:{
			'SE1':[   15,19,   24,28,40],	#No Ospec. produktion, no nuclear
			'SE2':[12,16,20,   25,29,41],		#No nuclear
			'SE3':[13,17,21,23,26,30,42],
			'SE4':[14,18,22,   27,31,43]	#No nuclear
		},
		2012:{
			'SE1':[   16,20,   26,30,42],	#No Ospec. produktion, no nuclear
			'SE2':[13,17,21,   27,31,43],	#No nuclear
			'SE3':[14,18,22,24,28,32,44],
			'SE4':[15,19,23,25,29,33,45]
		},
		2013:{
			'SE1':[   16,20,   25,29,41],	#No Ospec. produktion, no nuclear
			'SE2':[13,17,21,   26,30,42],	#No nuclear
			'SE3':[14,18,22,24,27,31,43],
			'SE4':[15,19,23,   28,32,44]	#No nuclear
		},
		2014:{
			'SE1':[   16,20,   25,29,41],	#No Ospec. produktion, no nuclear
			'SE2':[13,17,21,   26,30,42],	#No nuclear
			'SE3':[14,18,22,24,27,31,43],
			'SE4':[15,19,23,   28,32,44]	#No nuclear
		},
		2015:{
			'SE1':[   16,20,   25,29,41],	#No Ospec. produktion, no nuclear
			'SE2':[13,17,21,   26,30,42],	#No nuclear
			'SE3':[14,18,22,24,27,31,43],
			'SE4':[15,19,23,   28,32,44]	#No nuclear
		},
		2016:{
			'SE1':[13,17,21,   26,30,42],	#No nuclear
			'SE2':[14,18,22,   27,31,43],	#No nuclear
			'SE3':[15,19,23,25,28,32,44],
			'SE4':[16,20,24,   29,33,45]	#No nuclear
		},
		2017:{
			'SE1':[13,17,21,   26,30,42],	#No nuclear
			'SE2':[14,18,22,   27,31,43],	#No nuclear
			'SE3':[15,19,23,25,28,32,44],
			'SE4':[16,20,24,   29,33,45]	#No nuclear
		},
		2018:{
			'SE1':[9, 13,17,   22,26],	#No nuclear
			'SE2':[10,14,18,   23,27],	#No nuclear
			'SE3':[11,15,19,21,24,28],
			'SE4':[12,16,20,   25,29]	#No nuclear
		},
		2019:{
			'SE1':[17,21,25,   30,34],	#No nuclear
			'SE2':[18,22,26,   31,35],	#No nuclear
			'SE3':[19,23,27,29,32,36],
			'SE4':[20,24,28,   33,37]	#No nuclear
		},
		2020:{
			'SE1':[17,21,25,   30,34],	#No nuclear
			'SE2':[18,22,26,   31,35],	#No nuclear
			'SE3':[19,23,27,29,32,36],
			'SE4':[20,24,28,   33,37]	#No nuclear
		},
		2021:{
			'SE1':[17,21,25,   30,34],	#No nuclear
			'SE2':[18,22,26,   31,35],	#No nuclear
			'SE3':[19,23,27,29,32,36],
			'SE4':[20,24,28,   33,37]	#No nuclear
		},
		2022:{
			'SE1':[17,21,25,   30,34],	#No nuclear
			'SE2':[18,22,26,   31,35],	#No nuclear
			'SE3':[19,23,27,29,32,36],
			'SE4':[20,24,28,   33,37]	#No nuclear
		},
		2023:{
			'SE1':[17,21,25,   30,34],	#No nuclear
			'SE2':[18,22,26,   31,35],	#No nuclear
			'SE3':[19,23,27,29,32,36],
			'SE4':[20,24,28,   33,37]	#No nuclear
		}
	}

	#This dict specifies a list of how many rows to skip before reaching the actual data by year
	#We start at 1, because 0 holds the header
	skipRowsDict={
		2007:[1],
		2008:[1],
		2009:[1],
		2010:{
			0:[1,2],
			1:[1,2,3,4]
		},
		2011:[1,2,3,4],
		2012:[1,2,3,4],
		2013:[1,2,3,4],
		2014:[1,2,3,4],
		2015:[1,2,3,4],
		2016:[1,2,3,4],
		2017:[1,2,3,4],
		2018:[1,2,3,4],
		2019:[1,2,3,4],
		2020:[1,2,3,4],
		2021:[1,2,3,4],
		2022:[1,2,3,4],
		2023:[1,2,3,4]
	}

	def getDataframe(fname, year, i=-1):
		if not os.path.isfile(fname):
			try:
				if i == -1:
					print('Fetching url: ',urlDict[year])
					r = requests.get(urlDict[year])
				else:
					print('Fetching url: ',urlDict[year][i])
					r = requests.get(urlDict[year][i])
				r.raise_for_status()
			except requests.exceptions.RequestException as e:
				raise SystemExit(e)
			print('Saving file to: ',fname)
			open(fname, 'wb').write(r.content)

		#Cant use skiprows at at fixed value since data starts at different indexes between different files
		#However, it looks to be consistent that the data starts at the row below first complete empty row.
		if i == -1:
			df = pd.read_excel(fname, header=0, skiprows=skipRowsDict[year])
		else:
			df = pd.read_excel(fname, header=0, skiprows=skipRowsDict[year][i])
		print('Reading excel to dataframe: ',fname)

		#Get value from first column of 1th row.
		dotCount=str(df.iloc[:, 0].iloc[0]).count('.')
		dashCount=str(df.iloc[:, 0].iloc[0]).count('-')
		colonCount=str(df.iloc[:, 0].iloc[0]).count(':')
		df2 = pd.DataFrame()
		if dotCount == 0 and dashCount == 0 and colonCount == 0:
			df2['datetime'] = pd.to_datetime(df.iloc[:, 0], format="%Y%m%d", dayfirst=True) + pd.to_timedelta((df.iloc[:, 1] / 100), unit='h')
		elif (dotCount == 2 and dashCount == 0 and colonCount == 1) or (dotCount == 0 and dashCount == 2 and colonCount == 2):
#			df2['datetime'] = pd.to_datetime(df.iloc[:, 0], format="%d.%m.%Y %H:%M")
			df2['datetime'] = pd.to_datetime(df.iloc[:, 0], dayfirst=True)
		else:
			print('Unknwon date format: ',str(df.iloc[:, 0].iloc[0]))
			sys.exit()

		df2['timestamp'] = pd.to_datetime(df2['datetime']).astype(int)/ 10**9
		df2['year'] = df2['datetime'].dt.isocalendar().year
		df2['week'] = df2['datetime'].dt.isocalendar().week

		if i == -1:
			df2['consumption_SE1']= df.iloc[:, consumptionDict[year]['SE1']].sum(axis=1,numeric_only=True)
			df2['consumption_SE2']= df.iloc[:, consumptionDict[year]['SE2']].sum(axis=1,numeric_only=True)
			df2['consumption_SE3']= df.iloc[:, consumptionDict[year]['SE3']].sum(axis=1,numeric_only=True)
			df2['consumption_SE4']= df.iloc[:, consumptionDict[year]['SE4']].sum(axis=1,numeric_only=True)
			df2['consumption_SE']= df2['consumption_SE1']+df2['consumption_SE2']+df2['consumption_SE3']+df2['consumption_SE4']
			
			df2['production_SE1']= df.iloc[:, productionDict[year]['SE1']].sum(axis=1,numeric_only=True)
			df2['production_SE2']= df.iloc[:, productionDict[year]['SE2']].sum(axis=1,numeric_only=True)
			df2['production_SE3']= df.iloc[:, productionDict[year]['SE3']].sum(axis=1,numeric_only=True)
			df2['production_SE4']= df.iloc[:, productionDict[year]['SE4']].sum(axis=1,numeric_only=True)
			df2['production_SE']= df2['production_SE1']+df2['production_SE2']+df2['production_SE3']+df2['production_SE4']
		else:
			df2['consumption_SE1']= df.iloc[:, consumptionDict[year][i]['SE1']].sum(axis=1,numeric_only=True)
			df2['consumption_SE2']= df.iloc[:, consumptionDict[year][i]['SE2']].sum(axis=1,numeric_only=True)
			df2['consumption_SE3']= df.iloc[:, consumptionDict[year][i]['SE3']].sum(axis=1,numeric_only=True)
			df2['consumption_SE4']= df.iloc[:, consumptionDict[year][i]['SE4']].sum(axis=1,numeric_only=True)
			df2['consumption_SE']= df2['consumption_SE1']+df2['consumption_SE2']+df2['consumption_SE3']+df2['consumption_SE4']
			
			df2['production_SE1']= df.iloc[:, productionDict[year][i]['SE1']].sum(axis=1,numeric_only=True)
			df2['production_SE2']= df.iloc[:, productionDict[year][i]['SE2']].sum(axis=1,numeric_only=True)
			df2['production_SE3']= df.iloc[:, productionDict[year][i]['SE3']].sum(axis=1,numeric_only=True)
			df2['production_SE4']= df.iloc[:, productionDict[year][i]['SE4']].sum(axis=1,numeric_only=True)
			df2['production_SE']= df2['production_SE1']+df2['production_SE2']+df2['production_SE3']+df2['production_SE4']
		
		df2['balance_SE']= df2['consumption_SE']+df2['production_SE']
		df2['balance_SE1']= df2['consumption_SE1']+df2['production_SE1']
		df2['balance_SE2']= df2['consumption_SE2']+df2['production_SE2']
		df2['balance_SE3']= df2['consumption_SE3']+df2['production_SE3']
		df2['balance_SE4']= df2['consumption_SE4']+df2['production_SE4']

		return df2

	if year <= 2009:
		df3 = getDataframe('Statistik per elområde och timme, ' + str(year) + '.xlsx', year, -1)
	elif year == 2010:
		#Year 2010 consists of 2 separate files which we concatenate into one
		dfa3 = getDataframe('Statistik per elområde och timme, ' + str(year) + '_01-till-06.xlsx', year, 0)
		dfb3 = getDataframe('Statistik per elområde och timme, ' + str(year) + '_07-till-12.xlsx', year, 1)
		df3 = pd.concat([dfa3, dfb3],ignore_index=True)
	elif year >= 2011 and year <= datetime.now().year:
		df3 = getDataframe('Statistik per elområde och timme, ' + str(year) + '.xlsx', year, -1)
	else:
		sys.exit('Something went wrong')

	colAggDict={
		'datetime':'first',
		'year':'first',
		'week':'first',
		'balance_SE':'sum',
		'balance_SE1':'sum',
		'balance_SE2':'sum',
		'balance_SE3':'sum',
		'balance_SE4':'sum',
		'consumption_SE':'sum',
		'consumption_SE1':'sum',
		'consumption_SE2':'sum',
		'consumption_SE3':'sum',
		'consumption_SE4':'sum',
		'production_SE':'sum',
		'production_SE1':'sum',
		'production_SE2':'sum',
		'production_SE3':'sum',
		'production_SE4':'sum'
	}
	
	groupLyDict={
		'hour':'hourly',
		'day':'daily',
		'week':'weekly',
		'month':'monthly'
	}
	
	dotSizeDict={
		'hour':20,
		'day':80,
		'week':600,
		'month':2000
	}

	#This sets the x and y position of each point
	if groupby == '' or groupby == 'HOUR':
		df4=df3[[
			'datetime','year','week',
			'balance_SE','balance_SE1','balance_SE2','balance_SE3','balance_SE4',
			'consumption_SE','consumption_SE1','consumption_SE2','consumption_SE3','consumption_SE4',
			'production_SE','production_SE1','production_SE2','production_SE3','production_SE4'
		]].copy()
		df4['hour']=df4.index
		df4['y']=df4['hour'].apply(lambda x: int(x/120))
		df4['x']=df4['hour'].apply(lambda x: int(x%120))
	elif groupby == 'DAY':
		df4=df3.groupby([pd.Grouper(key='datetime', freq='D')], as_index=False).agg(colAggDict)
		df4['hour']=df4.index
		df4['y']=df4['hour'].apply(lambda x: int(x/20))
		df4['x']=df4['hour'].apply(lambda x: int(x%20))
	elif groupby == 'WEEK':
		df4=df3.groupby([pd.Grouper(key='datetime', freq='W')], as_index=False).agg(colAggDict)
		df4['hour']=df4.index
		df4['y']=df4['hour'].apply(lambda x: int(x/7))
		df4['x']=df4['hour'].apply(lambda x: int(x%7))
	elif groupby == 'MONTH':
		df4=df3.groupby([pd.Grouper(key='datetime', freq='M')], as_index=False).agg(colAggDict)
		df4['hour']=df4.index
		df4['y']=df4['hour'].apply(lambda x: int(x/3))
		df4['x']=df4['hour'].apply(lambda x: int(x%3))

	export_color = 'orange'
	import_color = 'grey'
	#Colorize a column based on value of balance in zone
	if zone == 'SE':
		df4['color'] = df4['balance_SE'].apply(lambda x: export_color if x > 0 else import_color)
		importLabel='Import (' + str((df4['balance_SE'] < 0).sum()) + ' ' + groupby.lower() + 's)'
		exportLabel='Export (' + str((df4['balance_SE'] >= 0).sum()) + ' ' + groupby.lower() + 's)'
		selfSufficient=math.ceil(df4['production_SE'].sum()/abs(df4['consumption_SE'].sum())*1000)/10
		print('Production: ' + str(math.ceil(df4['production_SE'].sum())) + ' MWh')
		print('Consumption: ' + str(math.ceil(abs(df4['consumption_SE'].sum()))) + ' MWh')
		print('Balance: ' + str(math.ceil(df4['balance_SE'].sum())) + ' MWh')
		print('Self-sufficient: ' + str(selfSufficient) + '%')
		textStr = '\n'.join((
			r'Production: ' + str(math.ceil(df4['production_SE'].sum())) + ' MWh | Consumption: ' + str(math.ceil(abs(df4['consumption_SE'].sum()))) + ' MWh',
			r'Balance: ' + str(math.ceil(df4['balance_SE'].sum())) + ' MWh | Self-sufficiency: ' + str(selfSufficient) + '%'
		))
	elif zone == 'SE1':
		df4['color'] = df4['balance_SE1'].apply(lambda x: export_color if x > 0 else import_color)
		importLabel='Import (' + str((df4['balance_SE1'] < 0).sum()) + ' ' + groupby.lower() + 's)'
		exportLabel='Export (' + str((df4['balance_SE1'] >= 0).sum()) + ' ' + groupby.lower() + 's)'
		selfSufficient=math.ceil(df4['production_SE1'].sum()/abs(df4['consumption_SE1'].sum())*1000)/10
		print('Production: ' + str(math.ceil(df4['production_SE1'].sum())) + ' MWh')
		print('Consumption: ' + str(math.ceil(abs(df4['consumption_SE1'].sum()))) + ' MWh')
		print('Balance: ' + str(math.ceil(df4['balance_SE1'].sum())) + ' MWh')
		print('Self-sufficient: ' + str(selfSufficient) + '%')
		textStr = '\n'.join((
			r'Production: ' + str(math.ceil(df4['production_SE1'].sum())) + ' MWh | Consumption: ' + str(math.ceil(abs(df4['consumption_SE1'].sum()))) + ' MWh',
			r'Balance: ' + str(math.ceil(df4['balance_SE1'].sum())) + ' MWh | Self-sufficiency: ' + str(selfSufficient) + '%'
		))
	elif zone == 'SE2':
		df4['color'] = df4['balance_SE2'].apply(lambda x: export_color if x > 0 else import_color)
		importLabel='Import (' + str((df4['balance_SE2'] < 0).sum()) + ' ' + groupby.lower() + 's)'
		exportLabel='Export (' + str((df4['balance_SE2'] >= 0).sum()) + ' ' + groupby.lower() + 's)'
		selfSufficient=math.ceil(df4['production_SE2'].sum()/abs(df4['consumption_SE2'].sum())*1000)/10
		print('Production: ' + str(math.ceil(df4['production_SE2'].sum())) + ' MWh')
		print('Consumption: ' + str(math.ceil(abs(df4['consumption_SE2'].sum()))) + ' MWh')
		print('Balance: ' + str(math.ceil(df4['balance_SE2'].sum())) + ' MWh')
		print('Self-sufficient: ' + str(selfSufficient) + '%')
		textStr = '\n'.join((
			r'Production: ' + str(math.ceil(df4['production_SE2'].sum())) + ' MWh | Consumption: ' + str(math.ceil(abs(df4['consumption_SE2'].sum()))) + ' MWh',
			r'Balance: ' + str(math.ceil(df4['balance_SE2'].sum())) + ' MWh | Self-sufficiency: ' + str(selfSufficient) + '%'
		))
	elif zone == 'SE3':
		df4['color'] = df4['balance_SE3'].apply(lambda x: export_color if x > 0 else import_color)
		importLabel='Import (' + str((df4['balance_SE3'] < 0).sum()) + ' ' + groupby.lower() + 's)'
		exportLabel='Export (' + str((df4['balance_SE3'] >= 0).sum()) + ' ' + groupby.lower() + 's)'
		selfSufficient=math.ceil(df4['production_SE3'].sum()/abs(df4['consumption_SE3'].sum())*1000)/10
		print('Production: ' + str(math.ceil(df4['production_SE3'].sum())) + ' MWh')
		print('Consumption: ' + str(math.ceil(abs(df4['consumption_SE3'].sum()))) + ' MWh')
		print('Balance: ' + str(math.ceil(df4['balance_SE3'].sum())) + ' MWh')
		print('Self-sufficient: ' + str(selfSufficient) + '%')
		textStr = '\n'.join((
			r'Production: ' + str(math.ceil(df4['production_SE3'].sum())) + ' MWh | Consumption: ' + str(math.ceil(abs(df4['consumption_SE3'].sum()))) + ' MWh',
			r'Balance: ' + str(math.ceil(df4['balance_SE3'].sum())) + ' MWh | Self-sufficiency: ' + str(selfSufficient) + '%'
		))
	elif zone == 'SE4':
		df4['color'] = df4['balance_SE4'].apply(lambda x: export_color if x > 0 else import_color)
		importLabel='Import (' + str((df4['balance_SE4'] < 0).sum()) + ' ' + groupby.lower() + 's)'
		exportLabel='Export (' + str((df4['balance_SE4'] >= 0).sum()) + ' ' + groupby.lower() + 's)'
		selfSufficient=math.ceil(df4['production_SE4'].sum()/abs(df4['consumption_SE4'].sum())*1000)/10
		print('Production: ' + str(math.ceil(df4['production_SE4'].sum())) + ' MWh')
		print('Consumption: ' + str(math.ceil(abs(df4['consumption_SE4'].sum()))) + ' MWh')
		print('Balance: ' + str(math.ceil(df4['balance_SE4'].sum())) + ' MWh')
		print('Self-sufficient to: ' + str(selfSufficient) + '%')
		textStr = '\n'.join((
			r'Production: ' + str(math.ceil(df4['production_SE4'].sum())) + ' MWh | Consumption: ' + str(math.ceil(abs(df4['consumption_SE4'].sum()))) + ' MWh',
			r'Balance: ' + str(math.ceil(df4['balance_SE4'].sum())) + ' MWh | Self-sufficiency: ' + str(selfSufficient) + '%'
		))

	if year == datetime.now().year:
		title='NOTE! Data only to ' + str(df4['datetime'].iloc[-1]) + '\nZone ' + str(zone) + ' ' + str(year) + ' (' + groupLyDict[groupby.lower()] + ')'
	else:
		title='Zone ' + str(zone) + ' ' + str(year) + ' (' + groupLyDict[groupby.lower()] + ')'

	#These dataframes are just dummys to create labels for export/orange and import/grey
	#Another solution would have been to split the main dataframe by color-value, but that caused colors with no data to not be displayed
	importLabel_df = pd.DataFrame([[0, 0, import_color]], columns=['x', 'y', 'color'])
	exportLabel_df = pd.DataFrame([[0, 0, export_color]], columns=['a', 'b', 'color'])

	#Plot the data
	ax = importLabel_df.plot(kind='scatter', x='x', y='y', c='color', label=importLabel)
	exportLabel_df.plot(kind='scatter', x='a', y='b', c='color', label=exportLabel, ax=ax)
	df4.plot(kind='scatter', x='x', y='y', c='color', title=title, ax=ax, figsize=(7, 6), s = dotSizeDict[groupby.lower()])

	#Hide irrelevant names on axes.
	ax.axes.get_xaxis().set_visible(False)
	ax.axes.get_yaxis().set_visible(False)

	print(textStr)
	#Add text to the bottom
#	plt.text(5, -10, textStr)
	plt.text(0.13, -0.08, textStr, transform = ax.transAxes)

	sourceStr = 'Source: svk.se > Statistik per elområde och timme. Made with https://github.com/skorpi0n/elzoneplot'
	plt.text(-0.02, -0.12, sourceStr, fontsize=8, transform = ax.transAxes)

	ax.figure.savefig('elzoneplot_' + str(zone) + '_' + str(year) + '_' + groupLyDict[groupby.lower()] + '.png')
	print('Saved plot to: ' + 'elzoneplot_' + str(zone) + '_' + str(year) + '_' + groupLyDict[groupby.lower()] + '.png')

	if output == 'STDOUT':
#		pd.set_option('display.max_columns', None)
		pd.set_option('display.max_rows', None)
		print(df4)
	elif output == 'PLOT':
		#Show plot
		plt.show()
	elif output != '':
		print('Saving dataframe to: ', output, sep='')
		df4.to_csv(output, sep='\t', encoding='utf-8')

if __name__ == "__main__":
	main(sys.argv[1:])
