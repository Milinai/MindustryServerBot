import asyncio
import socket
import discord #wss niet nodig

#mindustryPing.py desktop
from datetime import datetime

def ping(host, port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.settimeout(4)
	data = ""
	ms = 'ping failed'
	try:
		sent = sock.sendto(b'\xFE\x01',(host, port))
		start = datetime.now()
		data, server = sock.recvfrom(128)
		ellapsed = datetime.now()-start
		ms = '%.d ms' %(round(ellapsed.microseconds/1000,1)) #was (..., 1)		
	finally:
		response = {'ping':ms}		
		sock.close()
		if (ms!='ping failed'):
			response.update(parseResponse(data))
		return response
	

def popString(stack):
	length =	1+int.from_bytes(stack[:1],byteorder='big')
	string = stack[1:length].decode("utf-8")
	return stack[length:], string

def popInt(stack):
	integer = int.from_bytes(stack[:4],byteorder='big')
	return stack[4:],integer
	
def parseResponse(response):
	response, _ = popString(response) #msg would be server
	response, mapName = popString(response)
	response, players = popInt(response)
	response, wave    = popInt(response)
	response, version = popInt(response)
	response =	{'mapName': mapName,
				 'players': players,
				 'wave': wave,
				 'version': version,
				 'time last checked': datetime.now().strftime("%H:%M:%S %z")}
	return response

def make_msg(host, data):
	embed = discord.Embed(title=f"**{host}**")
	for key in data:
		embed.add_field(name=key, value=data[key], inline=True)
	return embed
		

#print(ping('mindustry.indielm.com', 6567))


#-----------------------------------------
'backgroundtask'
def check_online(host, port=6567, timeout=5):
	if ':' in host:
		host,port = host.split(':')[:2]
		if port.isdigit():
			port = int(port)
		else:
			return False
		
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.settimeout(timeout)
	data = "failed"
	try:
		host = socket.gethostbyname(host)
		s.sendto(b'\xFE\x01', (host, port))
		data, _ = s.recvfrom(128)
	finally:
		s.close()
		return (data != "failed")