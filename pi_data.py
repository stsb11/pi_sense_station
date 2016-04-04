# Sense hat data logger v0.5
from sense_hat import SenseHat
from ISStreamer.Streamer import Streamer
import matplotlib.pyplot as plt
import time
import os

# create a Streamer instance (currently disabled)
# streamer = Streamer(bucket_name="YOUR_BUCKET_NAME", bucket_key="YOUR_KEY", access_key="YOUR_KEY")

# The sense hat temperatures are very inaccurate, as the heat from the CPU skews them.
# The program uses a heuristic to approximate what the actual ambient temperature is.
def getCPUtemperature():
     res = os.popen('vcgencmd measure_temp').readline()
     return(res.replace("temp=","").replace("'C\n",""))

# Function to pick up the number of lines in the sensor reading files.
def file_len(fname):
     i = -1
     with open(fname) as f:
         for i, l in enumerate(f):
             pass
     return i + 1

# Function to poll the sense hat.
# calctemp - The previous temperature reading. The sense hat often gives wildly erroneous values.
# humidity - previous humidity reading.
# pressure - previous pressure reading.
# returns a tuple containing new values.
def getSensorData(calctemp, humidity, pressure):
    oldtemp=calctemp
    oldhumid=humidity
    oldpressure=pressure
    # Use CPU temp and pressure sensor temperature reading to approximate actual temperature.
    # Got this from the web; not my idea. Can't remember where from. 
    cpuTemp=int(float(getCPUtemperature()))
    ambient = sense.get_temperature_from_pressure()
    calctemp = round(ambient - ((cpuTemp - ambient)/ 1.5), 1)

    humidity = round(sense.get_humidity(), 1)
    pressure = round(sense.get_pressure(), 1)

    # As alluded to above, the sensors sometimes report temperatures of -100 to +300C.
    # This serves as a basic sanity check to prevent the graphs from becoming unreadable.
    if int(calctemp) > 75 or int(calctemp) < -20:
        calctemp = oldtemp

    if int(humidity) > 110 or int(humidity) < 0:
        humidity = oldhumid
        
    if int(pressure) > 1500 or int(pressure) < 750:
        pressure = oldpressure
        
    return calctemp, humidity, pressure

def plotGraph(theFile, sensorType, sensorReading):
    with open(theFile, "a") as out_file:
        out_file.write(str(sensorReading) + "\n")

    # Sampling once a minute, there are 1440 minutes in a day.
    # Store in a variable, as we'll use this to set xlim in the graph later.
    f_len = file_len(theFile)

    # When the file has 24 hours data, remove the oldest data point.
    if f_len > 1440:
        with open(theFile, 'r') as fin:
            data = fin.read().splitlines(True)
        with open(theFile, 'w') as fout:
            fout.writelines(data[1:])

    # Put the data into a list for processing.
    dataFile = open(theFile).readlines()
    myData = list()
    
    # We'll set the y-axis scale for ourselves, based on the
    # lowest and highest readings we ever see. Use these as start points.
    lowestTemp=1500
    highestTemp=-50

    # Pass through file to find Y-axis min/max values.
    for lines in dataFile:
        nextReading = lines.replace('\n', '')
        myData.append(nextReading)

        if float(nextReading) > highestTemp:
            highestTemp = float(nextReading)

        if float(nextReading) < lowestTemp:
            lowestTemp = float(nextReading)


    # Plot the graphs
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel('Time (Past 24 hours)')

    # Set up graph labels and scale depending on data...
    if sensorType == "T":
        ax.set_title('Temperature: ' + str(sensorReading) + "C")
        ax.set_ylabel('C')
        plt.ylim(lowestTemp - 1, highestTemp + 1)
        saveName = "temp.png"
        ax.plot(myData, "r-")
    elif sensorType == "H":
        ax.set_title('Relative humidity: ' + str(sensorReading) + "%rH")
        ax.set_ylabel('%rH')
        plt.ylim(lowestTemp - 1, highestTemp + 1)
        saveName = "humidity.png"
        ax.plot(myData)
    elif sensorType == "P":
        ax.set_title('Air pressure: ' + str(sensorReading) + "mb")
        ax.set_ylabel('Millibars (mb)')
        plt.ylim(lowestTemp - 4, highestTemp + 4)
        saveName = "pressure.png"
        ax.plot(myData, "k-")

    plt.xlim(0, f_len)
    # Remove 0 - 1440 values from X-axis.
    frame = plt.gca()
    frame.axes.get_xaxis().set_ticklabels([])

    # Save PNG file for use on web page.
    plt.savefig(saveName, bbox_inches='tight')
    plt.close(fig)
     
# ---------------------
# Main program starts here
# ----------

# Take preliminary reading prior to starting loop.
sense = SenseHat()
humidity = round(sense.get_humidity(), 1)
pressure = round(sense.get_pressure(), 1)
cpuTemp=int(float(getCPUtemperature()))
ambient = sense.get_temperature_from_pressure()
calctemp = round(ambient - ((cpuTemp - ambient)/ 1.5), 1)

while True:
    # Poll sensors
    calctemp, humidity, pressure = getSensorData(calctemp, humidity, pressure)

    # Plot temperature...
    theFile = "/home/pi/mjpg-streamer/mjpg-streamer-experimental/www/t_data.txt"
    plotGraph(theFile, "T", calctemp)

    # Plot humidity...
    theFile = "/home/pi/mjpg-streamer/mjpg-streamer-experimental/www/h_data.txt"
    plotGraph(theFile, "H", humidity)

    # Plot pressure...
    theFile = "/home/pi/mjpg-streamer/mjpg-streamer-experimental/www/p_data.txt"
    plotGraph(theFile, "P", pressure)
    
    # Submit data to InitialState stream...
    #streamer.log("Temperature", temp)
    #streamer.log("Humidity", humidity)
    #streamer.log("Pressure", pressure)

    # Enable for debugging.
    # print("Temperature: %sC" % calctemp)
    # print("Humidity: %s%%rH" % humidity)
    # print("Pressure: %s Millibars" % pressure)

    time.sleep(60) # Set to 2 for debugging, 60 when live.
