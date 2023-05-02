import getpass
import csv
from pyats.topology import loader
from pyats.easypy import run
from genie.conf import Genie
from genie.abstract import Lookup

# Read devices from the text file
with open("devices.txt", "r") as devices_file:
    devices_list = [device.strip() for device in devices_file.readlines()]

# Read commands from the text file
with open("commands.txt", "r") as commands_file:
    commands_list = [command.strip() for command in commands_file.readlines()]

# Prompt for username and password
username = input("Enter your username: ")
password = getpass.getpass("Enter your password: ")
enable_password = getpass.getpass("Enter your enable password: ")

# Initialize the testbed
testbed = loader.Testbed()
testbed.name = "custom_testbed"

# Add devices to the testbed
for device_name in devices_list:
    device = testbed.devices.create(device_name)
    device.os = "iosxe"
    device.type = "router"
    device.connections.create("default", class_="unicon.Unicon", cli="telnet")
    device.tacacs.username = username
    device.passwords.enable = enable_password
    device.passwords.line = password

# Initialize Genie
genie_testbed = Genie.init(testbed)

# Connect to devices and execute commands
output_list = []
for device_name in devices_list:
    device = genie_testbed.devices[device_name]
    device.connect()
    device_output = {"device": device_name}

    for command in commands_list:
        device_output[command] = device.execute(command)

    output_list.append(device_output)
    device.disconnect()

# Save the output to a CSV file
with open("output.csv", "w", newline="") as csvfile:
    fieldnames = ["device"] + commands_list
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for output in output_list:
        writer.writerow(output)

print("Results saved to output.csv")
