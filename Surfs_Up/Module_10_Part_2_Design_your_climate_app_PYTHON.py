# Import dependences for Flask API
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from datetime import datetime, timedelta

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///C:/Users/njlan/OneDrive/Desktop/Data_Boot_Camp/Class Projects/Module_10_SQLAlchemy/Starter_Code/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route('/')
def homepage():
    return (
        "Welcome to the Flask API!<br>"
        "Available routes:<br>"
        "/api/v1.0/precipitation<br>"
        "/api/v1.0/stations<br>"
        "/api/v1.0/tobs<br>"
        "/api/v1.0/&lt;start&gt;<br>"
        "/api/v1.0/&lt;start&gt;/&lt;end&gt;<br>"
    )

# Define the precipitation route
@app.route('/api/v1.0/precipitation')
def precipitation():#
    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(func.max(Measurement.date)).scalar()
    last_date = datetime.strptime(last_date, "%Y-%m-%d")
    one_year_ago = last_date - timedelta(days=365)

    # Query precipitation data for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    session.close()

    # Convert the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

# Define the stations route
@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)

    # Query all station names
    results = session.query(Station.station).all()

    session.close()

    # Convert the query results to a list
    station_list = [station[0] for station in results]

    return jsonify(station_list)

# Define the tobs route
@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)

    # Find the most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)) \
        .group_by(Measurement.station) \
        .order_by(func.count(Measurement.station).desc()) \
        .first()[0]

    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(func.max(Measurement.date)).filter(Measurement.station == most_active_station).scalar()
    last_date = datetime.strptime(last_date, "%Y-%m-%d")
    one_year_ago = last_date - timedelta(days=365)

    # Query temperature observations for the most active station for the last 12 months
    results = session.query(Measurement.date, Measurement.tobs) \
        .filter(Measurement.station == most_active_station) \
        .filter(Measurement.date >= one_year_ago) \
        .all()

    session.close()

    # Convert the query results to a list of dictionaries
    tobs_data = [{'date': date, 'temperature': tobs} for date, tobs in results]

    return jsonify(tobs_data)

# Define the temperature statistics route for a specified start date
@app.route('/api/v1.0/<start>')
def temperature_stats_start(start):
    session = Session(engine)

    # Convert the start parameter to a datetime object
    start_date = datetime.strptime(start, "%Y-%m-%d")

    # Query temperature statistics for dates greater than or equal to the start date
    results = session.query(Measurement.date,
                            func.min(Measurement.tobs).label('min_temp'),
                            func.avg(Measurement.tobs).label('avg_temp'),
                            func.max(Measurement.tobs).label('max_temp')
                            ) \
        .filter(Measurement.date >= start) \
        .group_by(Measurement.date) \
        .all()

    session.close()

    # Convert the query results to a list of dictionaries
    temperature_stats = [{'date': date, 'min_temp': min_temp, 'avg_temp': avg_temp, 'max_temp': max_temp}
                              for date, min_temp, avg_temp, max_temp in results]

    return jsonify(temperature_stats)

# Define the temperature statistics route for a specified start and end date
@app.route('/api/v1.0/<start>/<end>')
def temperature_stats_range(start, end):
    session = Session(engine)

    # Convert the start and end parameters to datetime objects
    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")

    # Query temperature statistics for the specified date range
    results = session.query(Measurement.date,
                            func.min(Measurement.tobs).label('min_temp'),
                            func.avg(Measurement.tobs).label('avg_temp'),
                            func.max(Measurement.tobs).label('max_temp')
                            ) \
        .filter(Measurement.date >= start) \
        .filter(Measurement.date <= end) \
        .group_by(Measurement.date) \
        .all()

    session.close()

    # Convert the query results to a list of dictionaries
    temperature_stats = [{'date': date, 'min_temp': min_temp, 'avg_temp': avg_temp, 'max_temp': max_temp}
                          for date, min_temp, avg_temp, max_temp in results]

    return jsonify(temperature_stats)

if __name__ == '__main__':
    app.run(debug=True)