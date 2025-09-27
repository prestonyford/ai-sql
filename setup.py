import os
import sqlite3
import csv

def setup():
	fdir = os.path.dirname(__file__)
	def getPath(fname):
		return os.path.join(fdir, fname)
	
	# SQLITE
	sqliteDbPath = getPath("aidb.sqlite")
	setupSqlPath = getPath("setup.sql")

	# Erase previous db
	if os.path.exists(sqliteDbPath):
		os.remove(sqliteDbPath)

	sqliteCon = sqlite3.connect(sqliteDbPath) # create new db
	sqliteCursor = sqliteCon.cursor()

	with open(setupSqlPath) as setupSqlFile:
		setupSqlScript = setupSqlFile.read()
		sqliteCursor.executescript(setupSqlScript) # setup tables and keys

	# Populate the db
	def preprocess(parts):
		replacements = {
			"N/A": None,
			"": None,
			# "-": None,
			"\\N": None,
			"Y": True,
			"N": False
		}
		return [replacements.get(val, val) for val in parts]


	route_to_aircraft = {}

	# Airlines
	with open(getPath("airlines.csv"), newline="", encoding="utf-8") as f:
		reader = csv.reader(f)
		for row in reader:
			if len(row) != 8:
				continue
			row = preprocess(row)
			sqliteCursor.execute("INSERT INTO Airline VALUES (?,?,?,?,?,?,?,?)", row)

	# Routes
	with open(getPath("routes.csv"), newline="", encoding="utf-8") as f:
		reader = csv.reader(f)
		for route_id, row in enumerate(reader):
			if len(row) != 9:
				continue
			if row[6] == "":
				row[6] = False
			# remove columns 0, 2, 4, 8
			row = [x for i, x in enumerate(row) if i not in {0, 2, 4}]
			row = preprocess(row)
			row.insert(0, route_id)

			equipment = row.pop()
			if equipment:
				equipment = equipment.split(' ')
				route_to_aircraft[route_id] = [e for e in equipment if e != '']
	
			if len(row) != 6:
				continue
			sqliteCursor.execute("INSERT INTO Route VALUES (?,?,?,?,?,?)", row)

	# Airports
	with open(getPath("airports.csv"), newline="", encoding="utf-8") as f:
		reader = csv.reader(f)
		for row in reader:
			if len(row) != 14:
				continue
			row = row[:-3]
			row = preprocess(row)
			if (row[10] == False):
				row[10] = 'N'
			sqliteCursor.execute("INSERT INTO Airport VALUES (?,?,?,?,?,?,?,?,?,?,?)", row)
	
	# Aircraft
	with open(getPath("planes.csv"), newline="", encoding="utf-8") as f:
		reader = csv.reader(f)
		for aircraft_id, row in enumerate(reader):
			if len(row) != 3:
				continue
			row = preprocess(row)
			row.insert(0, aircraft_id)
			sqliteCursor.execute("INSERT INTO Aircraft VALUES (?,?,?,?)", row)

	# Build iata_code -> aircraft_id lookup
	sqliteCursor.execute("SELECT aircraft_id, iata_code FROM Aircraft")
	iata_to_id = {row[1]: row[0] for row in sqliteCursor.fetchall() if row[1]}

	# Populate RouteAircraft
	for route_id, equipment in route_to_aircraft.items():
		if equipment:
			for code in equipment:
				aircraft_id = iata_to_id.get(code)
				if aircraft_id:
					sqliteCursor.execute(
						"INSERT INTO RouteAircraft (route_id, aircraft_id) VALUES (?,?)",
						(route_id, aircraft_id)
					)

	sqliteCon.commit()
	sqliteCon.close()

if __name__ == '__main__':
    setup()
    print("Done!")
    