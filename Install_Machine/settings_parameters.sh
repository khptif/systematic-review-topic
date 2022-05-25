#!/bin/sh

# We define all parameters for the file settings.py

export NUMBER_THREADS_ALLOWED=4
export NUMBER_TRIALS=300

#we define interval coordinate to display

export X_INTERVAL_LITTLE=500
export Y_INTERVAL_LITTLE=1000


export X_INTERVAL_BIG=1000
export Y_INTERVAL_BIG=4000

#we define in seconds the interval between update research
# we define 1 month
export UPDATE_INTERVAL=2700000

#is the app in one monolith block or on different module
export IS_MONOLITH=False
