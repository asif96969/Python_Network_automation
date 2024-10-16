import time
import paramiko
# import netmiko
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from .models import Device, Log
from datetime import datetime
from django.contrib import messages
import psutil


def home(request):
    all_device = Device.objects.all()
    cisco_device = Device.objects.filter(vendor="cisco")
    mikrotik_device = Device.objects.filter(vendor="mikrotik")
    last_event = Log.objects.all().order_by('-id')[:10]

    contex = {
        # 'all_device1': all_device,
        'all_device': len(all_device),
        'cisco_device': len(cisco_device),
        'mikrotik_device': len(mikrotik_device),
        'last_event': last_event
    }
    return render(request, 'home.html', contex)

def devices(request):
    all_device = Device.objects.all()
    contex = {
        'all_device': all_device
    }

    return render(request, 'devices.html', contex)

def configuration(request):
    if request.method == "POST":
        selected_device_id = request.POST.getlist('device')
        mikrotik_command = request.POST['mikrotik_command'].splitlines()
        cisco_command = request.POST['cisco_command'].splitlines()
        for x in selected_device_id:
            try:
                dev = get_object_or_404(Device, pk=x)
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=dev.ip_address, username=dev.username, password=dev.password)

                if dev.vendor.lower() == 'cisco':
                    conn = ssh_client.invoke_shell()
                    conn.send("conf t \n")
                    for cmd in cisco_command:
                        conn.send(cmd + "\n")
                        time.sleep(1)
                else:
                    for cmd in mikrotik_command:
                        ssh_client.exec_command(cmd)
                log = Log(target=dev.ip_address, action="Configure", status="Success", time=datetime.now(),messages='No Error')
                log.save()
            except Exception as e:
                log = Log(target = dev.ip_address, action = "Configure", status = "Error", time = datetime.now(), messages = e)
                log.save()

        return redirect('home')
    else:
        devices = Device.objects.all()
        context = {
            'devices': devices,
            'mode': 'Configure'
        }
        return render(request, 'config.html', context)

def verify_config(request):
    if request.method == "POST":
        result = []
        selected_device_id = request.POST.getlist('device')
        mikrotik_command = request.POST['mikrotik_command'].splitlines()
        cisco_command = request.POST['cisco_command'].splitlines()
        for x in selected_device_id:
            try:
                dev = get_object_or_404(Device, pk=x)
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=dev.ip_address, username=dev.username, password=dev.password)

                if dev.vendor.lower() == 'mikrotik':
                    for cmd in mikrotik_command:
                        stdin,stdout,stderr = ssh_client.exec_command(cmd)
                        time.sleep(1)
                        result.append("Result on {}".format(dev.ip_address))
                        result.append(stdout.read().decode())
                else:
                    conn = ssh_client.invoke_shell()
                    conn.send("terminal length 0\n")
                    for cmd in cisco_command:
                        result.append("Result on {}". format(dev.ip_address))
                        conn.send(cmd + "\n")
                        time.sleep(1)
                        output = conn.recv(65535)
                        result.append(output.decode())
                log = Log(target=dev.ip_address, action="Verify Configure", status="Error", time=datetime.now(),
                          messages='No Error')
                log.save()
            except Exception as e:
                log = Log(target=dev.ip_address, action="Verify Configure", status="Error", time=datetime.now(), messages=e)
                log.save()


        result = '\n'.join(result)
        return render(request, 'verify-result.html', {'result':result})
    else:
        devices = Device.objects.all()
        context = {
            'devices': devices,
            'mode': 'verfiy config'
        }
        return render(request, 'config.html', context)

def log(request):
    logs = Log.objects.all()
    context = {
        'logs': logs
    }
    return render(request, 'log.html', context)


# def monitor_network(request):
#     source_ip = "192.168.123.162"
#     destination_ip = "202.150.221.170"
#     # Fetch current network connections using psutil
#     connections = psutil.net_connections(kind='inet')
#
#     # Clear existing connections before updating with new data
#     NetworkConnection.objects.all().delete()
#
#     # Save new connections to the database
#     for conn in connections:
#         local_addr = conn.laddr.ip if conn.laddr else ""
#         remote_addr = conn.raddr.ip if conn.raddr else ""
#         status = conn.status
#         pid = conn.pid
#
#         if local_addr == source_ip or remote_addr == destination_ip:
#             NetworkConnection.objects.create(
#                 local_address=local_addr,
#                 remote_address=remote_addr,
#                 status=status,
#                 pid=pid
#             )
#
#     # Retrieve all connections from the database
#     connections = NetworkConnection.objects.all()
#
#     return render(request, 'monitor.html', {'connections': connections})
def show(request):
    if request.method == "POST":
        interface = request.POST.getlist('Show_Int')
        # MAC = request.POST('Show_MAC')
        ARP = request.POST.getlist('Show_ARP')
        # print(interface, MAC, ARP)
        Route = request.POST.getlist('Show_Route')
        # Ping = request.POST.getlist('ping')
        Mikrotik_route = request.POST['mikrotik_route']
        Cisco_route = request.POST['cisco_route']
        Dst_Ip_Mik = request.POST['Dst_Ip_Mik']
        # Dst_Ip_Cis = request.POST['Dst_Ip_Cis']
        result = []
        selected_device_id = request.POST.getlist('device')
        if selected_device_id and interface:
            for x in selected_device_id:
                dev = get_object_or_404(Device, pk=x)
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=dev.ip_address, username=dev.username, password=dev.password)

                if dev.vendor.lower() == 'mikrotik':
                    stdin, stdout, stderr = ssh_client.exec_command("interface ethernet print\n")
                    time.sleep(1)
                    result.append("Result on {}".format(dev.ip_address))
                    result.append(stdout.read().decode())
                else:
                    conn = ssh_client.invoke_shell()
                    conn.send("show interfaces description\n")
                    time.sleep(1)
                    output = conn.recv(65535)
                    result.append(output.decode())

            result = '\n'.join(result)
            return render(request, 'show.html', {'result': result})
        elif selected_device_id and ARP:
            for x in selected_device_id:
                dev = get_object_or_404(Device, pk=x)
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=dev.ip_address, username=dev.username, password=dev.password)

                if dev.vendor.lower() == 'mikrotik':
                    stdin, stdout, stderr = ssh_client.exec_command("ip arp print\n")
                    time.sleep(1)
                    result.append("Result on {}".format(dev.ip_address))
                    result.append(stdout.read().decode())
                else:
                    conn = ssh_client.invoke_shell()
                    conn.send("show arp\n")
                    time.sleep(1)
                    output = conn.recv(65535)
                    result.append(output.decode())
            result = '\n'.join(result)
            return render(request, 'show.html', {'result': result})
        elif selected_device_id and Route:
            for x in selected_device_id:
                dev = get_object_or_404(Device, pk=x)
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=dev.ip_address, username=dev.username, password=dev.password)

                if dev.vendor.lower() == 'mikrotik':
                    command = f"ip route print where dst-address={Mikrotik_route}\n"
                    stdin, stdout, stderr = ssh_client.exec_command(command)
                    time.sleep(1)
                    result.append("Result on {}".format(dev.ip_address))
                    result.append("Result on {}".format(Mikrotik_route))
                    result.append(stdout.read().decode())
                else:
                    conn = ssh_client.invoke_shell()
                    command = f"show ip route {Cisco_route}\n"
                    conn.send(command)
                    time.sleep(1)
                    output = conn.recv(65535)
                    # result.append("Result on {}".format(Dst_Ip_Mik))
                    result.append(output.decode())

            result = '\n'.join(result)
            return render(request, 'show.html', {'result': result})
        # elif selected_device_id and Ping:
        #     for x in selected_device_id:
        #         dav = get_object_or_404(Device, pk=x)
        #         ssh_client = paramiko.SSHClient()
        #         ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #         ssh_client.connect(hostname=dev.ip_address, username=dev.username, password=dev.password)
        #         if dev.vendor.lower() == 'mikrotik':
        #             command = f"ping {Dst_Ip_Mik} interval=.2 count=10 \n"
        #             stdin, stdout, stderr = ssh_client.exec_command(command)
        #             time.sleep(1)
        #             result.append("Result on {}".format(dev.ip_address))
        #             result.append(stdout.read().decode())
        #         else:
        #             conn = ssh_client.invoke_shell()
        #             command = f"ping {Dst_Ip_Cis} repeat 10\n"
        #             conn.send(command)
        #             time.sleep(1)
        #             output = conn.recv(65535)
        #             result.append(output.decode())
        #
        #     result = '\n'.join(result)
        #     return render(request, 'show.html', {'result': result})
        else:
            devices = Device.objects.all()
            context = {
                'devices': devices,
                'mode': 'Show Interface'
            }
            return render(request, 'show-configure.html', context)
    else:
        devices = Device.objects.all()
        context = {
            'devices': devices,
            'mode': 'Show Interface'
        }
        return render(request, 'show-configure.html', context)




