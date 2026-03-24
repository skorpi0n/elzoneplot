This Python script is based on lasseedfast elplot (https://github.com/lasseedfast/elplot) but with the ability so select zone (elområde)

Usage:
		elzoneplot.py -y <2007-2025> -z <SE|SE1|SE2|SE3|SE4> -g <MONTH|WEEK|DAY|HOUR(default)> -o <plot|std|oFile> -f -c <50-100(default)>

	-y, --year <2017-2025>
	
    -z, --zone <SE|SE1|SE2|SE3|SE4>
    
    -g, --groupby <MONTH|WEEK|DAY|HOUR(default)>
    
    -o, --output <plot|std|oFile>
      plot=open dataframe directly
      std=direct dataframe output to stdout
      oFile=direct dataframe output to file (csv)

	-f, --flows	#Undocumented Function in progress

	-c, --consumptionfraction <50-100(default)>	#Undocumented Function in progress

Data can be downloaded at https://www.svk.se/om-kraftsystemet/kraftsystemdata/elstatistik/  
The script is made for Excel-files found under "Statistik per elområde och timme".
