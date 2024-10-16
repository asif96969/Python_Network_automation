from netmiko import ConnectHandler

r1 = {
	"device_type": "cisco_ios",
	"host": "192.168.44.140",
	"username": "cisco",
	"password": "cisco",
}

conn = ConnectHandler(**r1)

list_config = [
	"int lo0",
	"ip add 10.1.1.1 255.255.255.255",
	"int lo1",
	"ip add 10.1.1.2 255.255.255.255"
]

output = conn.send_config_set(list_config)
print(output)

output = conn.send_command('show ip int brief')
print(output)
