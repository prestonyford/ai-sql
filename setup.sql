CREATE TABLE Airline (
	airline_id INTEGER PRIMARY KEY,
	name TEXT NOT NULL,
	alias TEXT,
	iata_code TEXT,
	icao_code TEXT,
	callsign TEXT,
	country TEXT,
	active INTEGER
);

CREATE TABLE Route (
	route_id INTEGER PRIMARY KEY,
	airline_id INTEGER,
	src_airport_id INTEGER,
	dst_airport_id INTEGER,
    codeshare BOOLEAN,
	stops INTEGER,
	FOREIGN KEY (airline_id) REFERENCES Airline(airline_id),
	FOREIGN KEY (src_airport_id) REFERENCES Airport(airport_id),
	FOREIGN KEY (dst_airport_id) REFERENCES Airport(airport_id)
);

CREATE TABLE Airport (
	airport_id INTEGER PRIMARY KEY,
	name TEXT NOT NULL,
	city TEXT,
	country TEXT,
	iata_code TEXT,
	icao_code TEXT,
	latitude REAL,
	longitude REAL,
	altitude_feet INTEGER,
	timezone_offset REAL,
	dst TEXT CHECK(dst IN ('E','A','S','O','Z','N','U'))
);

-- CREATE TABLE Country (
-- 	country_id INTEGER PRIMARY KEY,
-- 	name TEXT NOT NULL,
-- 	iso_code TEXT NOT NULL
-- );

CREATE TABLE Aircraft (
	aircraft_id INTEGER PRIMARY KEY,
	name TEXT NOT NULL,
	iata_code TEXT,
	icao_code TEXT
);

CREATE TABLE RouteAircraft (
	route_id INTEGER NOT NULL,
	aircraft_id INTEGER NOT NULL,
	PRIMARY KEY(route_id, aircraft_id),
	FOREIGN KEY (route_id) REFERENCES Route(route_id),
	FOREIGN KEY (aircraft_id) REFERENCES Aircraft(aircraft_id)
);
