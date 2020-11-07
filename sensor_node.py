import RPi.GPIO as GPIO
import time
import socket
import pickle

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN)
GPIO.setup(24, GPIO.IN)
#GPIO.setwarnings(False)
light = 23

HEADER = 1024
PORT = 9999
FORMAT = 'utf-8'
SERVER = "10.3.141.1"
ADDR = (SERVER, PORT)
counter = 0
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def rc_time (light):
	count = 0
	
	GPIO.setup(light, GPIO.OUT)
	GPIO.output(light, GPIO.LOW)
	time.sleep(1)
	
	GPIO.setup(light, GPIO.IN)
	
	while(GPIO.input(light) == GPIO.LOW):
		count += 1
	return count

try:
	time.sleep(2)
	while True:
		print(rc_time(light))
		#light_value = str(rc_time(light))
		#client.sendto(light_value.encode(), (ADDR))
		#time.sleep(3)
		if GPIO.input(24):
			print("Motion Detected...")
			time.sleep(1)
			if(rc_time(light)) > 1000:
				
				light_value = str(rc_time(light))

				#Responsetime between when someone is activating the motionsensor and its dark outside.
				resptime = time.time()
				
				print("This is the light value: ", light_value)
				print("Dark Enough for Lamp to enable")
				
				#Deliverytime between sending packet from Light & Motion Sensor Raspberry Pi and Raspberry Acutator.
				packet_del_time = time.time()
				msg_tuple = (packet_del_time, resptime, light_value)
				msg_send = pickle.dumps(msg_tuple)

				client.sendto(msg_send, ADDR) #Send tuple packet delivery and light value 

				#Counter that counts how many packages that has been send between the two Raspberry Pies.
				counter = counter + 1
				print("Packet Number: ", counter)
				
		else:
			print("No Motion Detected...")
			time.sleep(0.3)

except KeyboardInterrupt:
	pass

finally:
	GPIO.cleanup()
