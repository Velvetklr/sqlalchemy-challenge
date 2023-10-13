# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
M = Base.classes.measurement
S = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)
last_date = session.query(M.date)[-1]
#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Available routes: <br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/[start] <br/>"
        f"/api/v1.0/[start]/[end] <br/>"
    )

#Date and Precipitation for the past 12 months
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    last_date = session.query(M.date)[-1]
    prev_year = dt.datetime.strptime(last_date[0], '%Y-%m-%d').date()-dt.timedelta(365)
    precipitation = session.query(M.date, M.prcp).\
        filter(M.date >= prev_year).all()

    precip = {date: prcp for date, prcp in precipitation}

    return jsonify(precip)

#List of all Stations
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station = session.query(S.station).all()
    
    session.close()
    stations = list(np.ravel(station))

    return jsonify(stations)

#Temp for most active station in past 12M
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    last_date = session.query(M.date)[-1]
    prev_year = dt.datetime.strptime(last_date[0], '%Y-%m-%d').date()-dt.timedelta(365)

    results = session.query(M.tobs).\
        filter(M.station == 'USC00519281').\
        filter(M.date >= prev_year).all()
    
    session.close()

    temps = list(np.ravel(results))

    return jsonify(temps)


# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def range(start,end="2017-08-23"):
    session = Session(engine)

    results = session.query(func.min(M.tobs), func.avg(M.tobs), func.max(M.tobs)).filter((M.date>=start)&(M.date<=end)).first()
 
    return {"min":results[0], "avg":results[1], "max":results[2]}


if __name__ == "__main__":
    app.run(debug=True)