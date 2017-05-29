import __init__
#
from datetime import datetime
# now = None
min_dt, max_dt = None, None
datehours = None



now = datetime(2009,1, 1, 10)
min_dt, max_dt = datetime(2009,1, 1, 10), datetime(2009,1, 1, 10)
datehours = [datetime(2009,1, 1, 10)]




def get_datehour():
    return now.year, now.month, now.day, now.hour