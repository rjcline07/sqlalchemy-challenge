#Dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt

#creating engine
engine = create_engine("sqlite:///hawaii.sqlite")

#reflect
base = automap_base()
base.prepare(engine, reflect= True)

#Save references
measurement = base.classes.measurement
station = base.classes.station

#create session
session = Session(engine)

#flask setup
app = Flask(__name__)

@app.route("/")
def hello():
    #shows available routes
    return (
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    #shows precipitation data for last year

    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    date_split = recent_date[0].split('-')

    year = int(date_split[0])
    month = int(date_split[1])
    day = int(date_split[2])

    # using last day in database to find time 1 year prior
    date_year_ago = dt.date(year, month, day) - dt.timedelta(days = 365)
    
    
    precipitation = session.query(measurement.date, measurement.prcp).\
                            filter(measurement.date >= date_year_ago).all()
    session.close()
    
    # list of query data to shift to json 
    all_prcp =[]
    for date, prcp in precipitation:
        temp_dict ={}
        temp_dict["date"] = date
        temp_dict["precipitation"] = prcp
        all_prcp.append(temp_dict)

    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():
    #shows list of stations from dataset.

    #query for stations
    stations = session.query(Station).all()

    #list of dictionaries that is then returned jsonified
    stations_list = []
    for station in stations:
        station_dict = {}
        station_dict["id"] = station.id
        station_dict["station"] = station.station
        station_dict["name"] = station.name
        station_dict["latitude"] = station.latitude
        station_dict["longitude"] = station.longitude
        station_dict["elevation"] = station.elevation
        stations_list.append(station_dict)

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    date_split = recent_date[0].split('-')

    year = int(date_split[0])
    month = int(date_split[1])
    day = int(date_split[2])

    # using last day in database to find time 1 year prior
    date_year_ago = dt.date(year, month, day) - dt.timedelta(days = 365)
    
    # query
    list_station = session.query(measurement.station, func.count(measurement.station)).\
                    group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()

    temp_obs = session.query(measurement.tobs).\
                filter(measurement.station == list_station[0][0]).\
                filter(measurement.date >= date_year_ago).all()
    #session close
    session.close()

    tobs = list(np.ravel(temp_obs))

    return jsonify(tobs)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    #getting min,max, and average temperature

    # Summary of temp data
    summ = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]

    if end == None:
        # finding min, max, and avg for dates past start
        results = session.query(*summ).\
            filter(measurement.date >= start).all()
        # converting to list
        temp = list(np.ravel(results))
        return jsonify(temp)

    # finding min, max and avg with start date
    results = session.query(*summ).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()
    # converting to list
    temp = list(np.ravel(results))
    return jsonify(temp=temp)


if __name__ == '__main__':
    app.run()