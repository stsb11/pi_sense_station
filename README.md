# pi_sense_station

Introduction
------------
A quick-make project, to plot data (temperature, humidity, atmospheric pressure) from the Raspberry Pi sense hat onto a web page along with a live video feed from a connected USB webcam. 

Code was also pushed up to InitialState for data logging and worked well - I used up my free monthly allowance rather quickly while testing though as I initially sampled once a second! The code is still in the Python3 .py file, but is commented out; remove the hashes in the appropriate lines to re-enable it.

Ingredients
-----------
Raspberry Pi (I used a 3, but RPi2 should work nicely as well) with Raspbian installed.
Raspberry Pi sense hat,
USB webcam (I used an old Microsoft one I had in a drawer).

Method
------
STEP 1. Install mjpg-streamer. (https://github.com/jacksonliam/mjpg-streamer)
git clone https://github.com/jacksonliam/mjpg-streamer.git
cd ~/mjpg-streamer/mjpg-streamer-experimental
make
sudo make install
NOTE: Problems ensued at this point. Had to install dependencies. Can't remember which ones.

STEP 2. Test.
cd ~/mjpg-streamer/mjpg-streamer-experimental
mjpg_streamer -i input_uvc.so -o "output_http.so -w ./www"

STEP 3. Install Sense hat +  matplotlib
sudo apt-get update
sudo apt-get install sense-hat
sudo pip3 install matplotlib
sudo reboot

STEP 4. Pick up custom index.html, graphs.html and pi_data.py from this repo.
cd ~
git clone THIS REPO
cp ./pi_sense_station/index.html ~/mjpg-streamer/mjpg-streamer-experimental/www/
cp ./pi_sense_station/graphs.html ~/mjpg-streamer/mjpg-streamer-experimental/www/
cp ./pi_sense_station/pi_data.py ~/mjpg-streamer/mjpg-streamer-experimental/www/

STEP 5. Load the webcam and graph plotting services
cd ~/mjpg-streamer/mjpg-streamer-experimental
python3 ./www/pi_data.py & disown
mjpg_streamer -i input_uvc.so -o "output_http.so -w ./www" & disown

NOTE: If any error messages appear, kill the offending process by using:
ps aux    (locate the PID of the python3 pi_data.py task)
kill n    (Where n is the PID you previously located).

STEP 6. Browse to page on a different device on your network.
You can find your IP address by typing 'ip addr' from the terminal.
e.g. 192.168.1.100:8080
