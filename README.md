This Python script is based on lasseedfast elplot () but with the ability so select zone (elområde)

Usage:
		elzoneplot.py -z <SE|SE1|SE2|SE3|SE4> -g <MONTH|WEEK|DAY|HOUR(default)> -o <std|oFile>
    
    -z, --zone <SE|SE1|SE2|SE3|SE4>
    
    -g, --groupby <MONTH|WEEK|DAY|HOUR(default)>
    
    -o, --output <std|oFile>
      std=direct dataframe output to stdout
      oFile=direct dataframe output to file (csv)

Data can be downloaded at https://www.svk.se/om-kraftsystemet/kraftsystemdata/elstatistik/  
The script is made for Excel-files found under "Statistik per elområde och timme".
