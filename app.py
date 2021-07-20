import numpy as np

from datetime import datetime
import sqlalchemy
import pandas as pd
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../sqlalchemy-challenge/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement


#################################################
# Flask Setup
#################################################

app = Flask(__name__)

# Flask Routes

@app.route("/")
def home():
    print("Server received request for 'Home' page...") 
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>" 
        f"/api/v1.0/tobs <br/>" 
        f"/api/v1.0/<start> <br/>" 
        f"/api/v1.0/<start>/<end>")


# 1) Query precipitaiton dataset

@app.route("/api/v1.0/precipitation")
def precipitation_q():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    result = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > '2016-08-23').\
        order_by(Measurement.date).all()

    # Save the query results as a Pandas DataFrame and set the index to the date column
    precip_df = pd.DataFrame(result)
    precip_df.set_index("date", inplace = True)

    # Sort the dataframe by date
    precip_sort_df = precip_df.sort_index(ascending=True)
    precip_nonan_df = precip_sort_df.dropna(how = 'any')

    session.close()

    dict = precip_nonan_df.to_dict()

    return jsonify(dict)

# 2) Query station dataset

@app.route("/api/v1.0/stations")
def station_q():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    stations=session.query(Station.station, Station.name).all()

    session.close()

    return jsonify(stations)

# 3) Query the dates and temperature observations of the most active station for the last year of data.

@app.route("/api/v1.0/tobs")
def station_active():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    active_st_temp = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
                filter(Measurement.date > '2016-08-23').\
                filter(Measurement.station == 'USC00519281').all()

    session.close()

    return jsonify(active_st_temp)


# 4a) uery with start dates  - api/v1.0/<start> 
#    Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

@app.route("/api/v1.0/<start>")
def date_cond_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #temp_data = session.query(Measurement.station, Measurement.date, Measurement.tobs).all()
    start = datetime.strptime(start, "%Y-%m-%d").date()

    #for date in temp_data:
     #   search_term = 

    active_st_stat = session.query(Measurement.station, Station.name, func.min(Measurement.tobs),\
        func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.station == Station.station).\
        filter(Measurement.date >= start).\
        filter(Measurement.station == 'USC00519281').\
        group_by(Measurement.station).all()


    session.close()

    #return jsonify(active_st_stat)


    return (
           f'the temperature statistics for the most active station "{active_st_stat[0][1]}" is: <br/>'
           f' - lowest temperature is {active_st_stat[0][2]}; <br/>'
           f' - highest temperature is {active_st_stat[0][3]};<br/>'
           f' - average temperature is {active_st_stat[0][4]}' 
           )


# 4b) query with start and end dates -  api/v1.0/<start> and /api/v1.0/<start>/<end> 

@app.route("/api/v1.0/<start>/<end>")
def date_cond_start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #temp_data = session.query(Measurement.station, Measurement.date, Measurement.tobs).all()
    start = datetime.strptime(start, "%Y-%m-%d").date()
    end = datetime.strptime(end, "%Y-%m-%d").date()

    #for date in temp_data:
     #   search_term = 

    active_st_stat = session.query(Measurement.station, Station.name, func.min(Measurement.tobs),\
        func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.station == Station.station).\
        filter(Measurement.date >= start ).\
        filter(Measurement.date <= end).\
        filter(Measurement.station == 'USC00519281').\
        group_by(Measurement.station).all()


    session.close()

    #return jsonify(active_st_stat)

    return (
           f'the temperature statistics for the most active station "{active_st_stat[0][1]}" is: <br/>'
           f' - lowest temperature is {active_st_stat[0][2]}; <br/>'
           f' - highest temperature is {active_st_stat[0][3]};<br/>'
           f' - average temperature is {active_st_stat[0][4]}' 
           )



if __name__ == "__main__":
    app.run(debug=True)