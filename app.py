# Import Flask/dependencies 
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

import datetime as dt

# Setup database 
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"All Available Routes:<br/>"       
        f"/api/v1.0/precipitation<br/>"   
        f"/api/v1.0/stations<br/>"  
        f"/api/v1.0/tobs<br/>"     
        f"/api/v1.0/yyyy-mm-dd<br/>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    #Create session/link from python to DB 
    session = Session(engine) 

    #Query for date and prcp  
    results = session.query(Measurement.date, Measurement.prcp).all()

    #Convert query results to dictionary using date as key and prcp as value
    all_measurements = [ ] 
    for date, prcp in results:
        measurement_dict = {date : prcp}
        all_measurements.append(measurement_dict)

    #close session
    session.close()

    #Reutrn JSON representation of dictionary 
    return jsonify(all_measurements)


@app.route("/api/v1.0/stations")
def stations():
    #Create session/link from python to DB 
    session = Session(engine) 

    #return JSON list of stations from dataset
    stations = session.query(Station.station).all()

    session.close()
    
    all_stations = list(np.ravel(stations))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    #Create session/link from python to DB 
    session = Session(engine) 

    # Query the dates and temperature observations of the most active station for the last year of data.
    station_id = 'USC00519281'
    
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    year_date = dt.datetime.strptime(last_date,'%Y-%m-%d')-dt.timedelta(days=366)

    # Return a JSON list of temperature observations (TOBS) for the previous year.
    all_temps = []
    most_active = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
        filter(Measurement.date >=year_date).filter(Measurement.station == station_id).all()

    for station, date, tobs in most_active:
        temp_obs={}
        temp_obs['Date'] = date
        temp_obs['Station ID'] = station
        temp_obs['tobs'] = tobs
        all_temps.append(temp_obs)

    session.close()

    return jsonify(all_temps)


@app.route("/api/v1.0/<start>")
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates 
# greater than and equal to the start date.

def start_only(start):
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    session.close()
    all_results = [ ]
    for min, avg, max in results:
        result_qry={ }
        result_qry['Tmin'] = min
        result_qry['Tavg'] = avg
        result_qry['Tmax'] = max
        all_results.append(result_qry)

    return jsonify(all_results)


@app.route("/api/v1.0/<start>/<end>")
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for 
# dates between the start and end date inclusive.

def start_end(start, end):
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()
    all_results = [ ]
    for min, avg, max in results:
        result_qry={ }
        result_qry['Tmin'] = min
        result_qry['Tavg'] = avg
        result_qry['Tmax'] = max
        all_results.append(result_qry)

    return jsonify(all_results)


if __name__ == "__main__":
    app.run(debug=True)