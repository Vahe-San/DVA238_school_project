
import os
import RPi.GPIO as GPIO
import time
import socket
import threading
import pickle

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(14, GPIO.OUT)


#counter_id = 0
on = "1"
off = "0"
systemresptime = 0
response_time = 0

HEADER = 1024
PORT = 9999
FORMAT = 'utf-8'
SERVER = "10.3.141.1"
#SERVER = "192.168.0.198"
ADDR = (SERVER, PORT)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((SERVER, PORT))




#Socket Laptop
laptop_address = "10.3.141.222"
port = 9998
laptop_addr = (laptop_address, port)
laptop_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


#Clear terminal
os.system("clear")

def send_to_laptop(on_off, time_send, system_response_time):

   send_to_laptop = (on_off, time_send, system_response_time) #Tuple signal and time
   msg_send = pickle.dumps(send_to_laptop) #Pickle dump signal and time
   laptop_socket.sendto(msg_send, laptop_addr) #Send to laptop



startTimer = 0
elapsed_time = 0
timer_start = False
GPIO.output(14, GPIO.LOW)

rec = 0
counter = 0

def my_timer_value():
	global my_timer

	my_timer = 10
	return my_timer


def countdown(timer_value):

	global stop_threads

	print("Timer value", timer_value)
	while (not stop_threads):
		timer_value = timer_value - 1
		time.sleep(1)
		print("Time:", timer_value)
		if timer_value == 0:
#			send 0 to display as string
			time_send = time.time()
			send_to_laptop(off, time_send, systemresptime)
			print("turning off LED")
			GPIO.output(14, GPIO.LOW)
			print("Listening...")
			stop_threads = True
		if stop_threads == True:
			break

try:
	global stop_threads
	print("Running diagnostics...")
	#converted_rec = 3001
	while True:
		converted_rec = "3001"

		if converted_rec > "3000":
			converted_rec = 1

		if(int(converted_rec) == 1):
			GPIO.output(14, GPIO.HIGH)
			#print(systemresptime)

			response_time = time.time() - systemresptime #System response time between RPi(DIOD-led) and Motionsensor
#			print("Response time system: {:.3f} ms" .format(response_time))
			print("Turnin on LED...")

			#send a 1 to display as string
			send_time = time.time()
			send_to_laptop(on, send_time, systemresptime)
			new_timer = my_timer_value()
			stop_threads = False
			countdown_thread = threading.Thread(target = countdown, args=(new_timer, ))
			countdown_thread.start()

			data, addr = s.recvfrom(HEADER)
			recived_data = pickle.loads(data)
			converted_rec = recived_data[2]
			systemresptime = recived_data[1]

			counter = counter + 1 #Recived Packet counter
#			print("Packet total recived:", counter)

			#Reviced time from sensor(Motion)/Packet delivery time recived from RPi 2
			total = time.time() - recived_data[0]
#			print("Packet receive time:{:.3f} ms".format(total))


			stop_threads = True
			countdown_thread.join()
			stop_threads = False
			converted_rec = 0

except KeyboardInterrupt:
	pass

finally:
	GPIO.cleanup()
	s.close()
