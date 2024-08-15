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
#create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()   


# reflect the tables
Base.prepare(engine, reflect=True) 

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        f"Welcome to the Hawaii Climate API!<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the last 12 months of precipitation data as a JSON dictionary."""
    # Calculate the date one year ago from the last date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    end_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    start_date = end_date - dt.timedelta(days=365)

    # retrieve the data and precipitation scores
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all()

    # Convert the query results to a dictionary with date as the key and prcp as the value
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Query all stations
    station_data = session.query(Station.station).all()

    # Convert the query results to a list
    stations_list = list(np.ravel(station_data))

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations (TOBS) for the previous year."""
    # Get the most active station id
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]

    # Calculate the date one year ago from the last date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    end_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    start_date = end_date - dt.timedelta(days=365)

    # Query the temperature observations for the last year for the most active station
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all()

    # Convert the query results to a list
    temperature_list = list(np.ravel(temperature_data))

    return jsonify(temperature_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start, end=None):
    """Return a JSON list of the minimum, average, and maximum temperatures for a given date range."""
    #calculate stats from the start date to the most recent date
    if end is None:
        end = session.query(func.max(Measurement.date)).scalar()

    # Query to calculate TMIN, TAVG, and TMAX for dates between the start and end date inclusive
    temperature_stats = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Convert the query results to a list
    temperature_stats_list = list(np.ravel(temperature_stats))

    return jsonify(temperature_stats_list)

#################################################
# Run the Flask app
#################################################
if __name__ == "__main__":
    app.run(debug=True)