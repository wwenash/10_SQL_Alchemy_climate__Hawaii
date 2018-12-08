# HW_10_SQL_Alchemy_wen_WASHSTL201809DATA3
# Dependencies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt
from datetime import datetime
from datetime import timedelta
from datetime import date

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    # List all available api routes.
    return (
        f"Welcome to the Hawaii Climate Data Analysis API!<br/><br/>"
        f"Avalable Routes:<br/><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/> When selecting dates, use dates before 2017-08-23" 
         " and in YYYY-MM-DD format, please. <br/><br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

#precipition route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Return the precipitation data for the last 2 years from today
    # Calulate the date 2 year ago from today
    today = datetime.now()
    last_yearobj = today.replace(year=today.year-2)
    last_year = last_yearobj.strftime("%Y-%m-%d")

    # Query for the date and precipitation for the last year
    precip_results = (session.query(Measurement.date, Measurement.prcp).
        filter(Measurement.date >= last_year).all())

    # Dict with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in precip_results}

    # return to user
    return jsonify(precip)

# station route
@app.route("/api/v1.0/stations")
def stations():
    # List for station data
    stations_list = []

    # Station Query
    stations = (session.query(Station.station, Station.name, Station.latitude, 
        Station.longitude, Station.elevation).all())

    #create a dictionary for each station's info and append to list
    for station in stations:
        station_dict = {"station_id": station[0], "name": station[1], 
        "latitude": station[2], "longitude": station[3], 
        "elevation": station[4]}

        stations_list.append(station_dict)

    # Return to user
    return jsonify(stations_list)

# tobs temps route
@app.route("/api/v1.0/tobs")
def temperatures():
    # Get dates...Calculate the date 1 year ago from the last data point in the database
    most_current = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = most_current[0]
    
    #convert last_date to a datetime object
    last_dateobj = datetime.strptime(last_date, "%Y-%m-%d")
    year_before = last_dateobj.replace(year = last_dateobj.year - 1)
    year_before = year_before.strftime("%Y-%m-%d")
    
    # Perform a query to retrieve the most active station
    station_results = (session.query(Measurement.station, func.count(Measurement.station)).
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all())

    has_station = station_results[0]
    h_station = has_station[0]

    # Perform query to retrieve the temp data from most active station for last year 
    # from the last data point
    temp_results = (session.query(Measurement.tobs).
                    filter(Measurement.station == h_station).
                    filter(Measurement.date >= year_before).all())

    # Return to user
    return jsonify(temp_results)

# start date route
# start/end date route
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):
    #R eturn TMIN, TAVG, TMAX

    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = (session.query(*sel).
            filter(Measurement.date >= start).all())
        
        # Retuen return to user
        starttemps = list(np.ravel(results))
        return jsonify(starttemps)

    # calculate TMIN, TAVG, TMAX with start and stop
    results = (session.query(*sel).
        filter(Measurement.date >= start).
        filter(Measurement.date <= end).all())
    
    # Retuen return to user
    startendtemps = list(np.ravel(results))
    return jsonify(startendtemps)




if __name__ == '__main__':
    app.run(debug=True)