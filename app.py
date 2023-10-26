# Import the dependencies
from flask import Flask, jsonify
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

#################################################
# Database Setup
#################################################

# Create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
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
def home():
    return (
        "Welcome to the Climate App API!<br/>"
        "Available Routes:<br/>"
        "/api/v1.0/precipitation - Precipitation data for the last 12 months<br/>"
        "/api/v1.0/stations - List of weather stations<br/>"
        "/api/v1.0/tobs - Temperature observations for the most active station in the last year<br/>"
        "/api/v1.0/&lt;start&gt; - Temperature statistics from a start date to the end of the dataset<br/>"
        "/api/v1.0/&lt;start&gt;/&lt;end&gt; - Temperature statistics for a date range"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year from the last date in data set
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date = most_recent_date[0]
    one_year_ago = (dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    # Query precipitation data for the last 12 months
    precipitation_data = session.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date >= one_year_ago)\
        .order_by(Measurement.date)\
        .all()

    # Convert the query results to a dictionary with date as the key and prcp as the value
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Query the list of stations
    station_list = session.query(Station.station).all()

    # Convert the query results to a list
    stations = [station[0] for station in station_list]

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Find the most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station))\
        .group_by(Measurement.station)\
        .order_by(func.count(Measurement.station).desc())\
        .first()[0]

    # Calculate the date one year from the last date in data set
    most_recent_date_active_station = session.query(Measurement.date)\
        .filter(Measurement.station == most_active_station)\
        .order_by(Measurement.date.desc())\
        .first()[0]

    one_year_ago_active_station = (dt.datetime.strptime(most_recent_date_active_station, '%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    # Query temperature observations for the most active station in the last 12 months
    temperature_data_active_station = session.query(Measurement.tobs)\
        .filter(Measurement.station == most_active_station, Measurement.date >= one_year_ago_active_station)\
        .all()

    # Convert the query results to a list of temperature observations
    temperature_list = [temp[0] for temp in temperature_data_active_station]

    return jsonify(temperature_list)

@app.route("/api/v1.0/<start>")
def temp_stats_start(start):
    # Calculate temperature statistics for a start date
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs))\
        .filter(Measurement.date >= start)\
        .all()

    # Create a dictionary for the statistics
    temp_stats = {
        "Minimum Temperature": results[0][0],
        "Maximum Temperature": results[0][1],
        "Average Temperature": results[0][2]
    }

    return jsonify(temp_stats)

@app.route("/api/v1.0/<start>/<end>")
def temp_stats_start_end(start, end):
    # Calculate temperature statistics for a date range
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs))\
        .filter(Measurement.date >= start, Measurement.date <= end)\
        .all()

    # Create a dictionary for the statistics
    temp_stats = {
        "Minimum Temperature": results[0][0],
        "Maximum Temperature": results[0][1],
        "Average Temperature": results[0][2]
    }

    return jsonify(temp_stats)

if __name__ == "__main__":
    app.run(debug=True)
