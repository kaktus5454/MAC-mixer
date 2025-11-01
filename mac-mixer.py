import re
import psutil
from socket import AF_INET, AF_INET6
import subprocess
import random
import questionary
import time


if_choices = []
if_addrs = psutil.net_if_addrs()
print("\033[1m\033[32mYour interfaces:\033[0m\n")
for iface, addrs in if_addrs.items():
    if_choices.append(iface)
    
wybor = questionary.select(
    "Choose interface:",
    choices=if_choices
).ask()


def get_current_mac(iface: str) -> str | None:
    try:
        out = subprocess.run(["ip", "link", "show", iface],
                             check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        m = re.search(r"link/ether\s+([0-9a-fA-F:]{17})", out.stdout)
        return m.group(1).lower() if m else None
    except subprocess.CalledProcessError:
        print("Invalid interface name")
        return None


oldaddr = get_current_mac(wybor)
print("Your old mac address: ", oldaddr)


choices = ["Microsoft", "Dell", "IBM", "ASUS", "HP"]
producent = questionary.select(
    "Choose manufacturer:",
    choices=choices
    ).ask()


def generate_random_mac(prod):    
    newmac = [
           random.randint(0x00, 0x7f),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    if (prod=="Microsoft"):
        newmac.insert(0, 0xF2)
        newmac.insert(0, 0x50)
        newmac.insert(0, 0x00)
    elif (prod=="Dell"):
        newmac.insert(0, 0x21)
        newmac.insert(0, 0x1B)
        newmac.insert(0, 0x00)
    elif (prod=="IBM"):
        newmac.insert(0, 0xB3)
        newmac.insert(0, 0x25)
        newmac.insert(0, 0x00)
    elif (prod=="ASUS"):
        newmac.insert(0, 0x92)
        newmac.insert(0, 0x1A)
        newmac.insert(0, 0x00)
    elif (prod=="HP"):
        newmac.insert(0, 0x00)
        newmac.insert(0, 0x1C)
        newmac.insert(0, 0x42)
        
    return ':'.join(f"{x:02x}" for x in newmac)


def change_mac(iface, new_mac):
    try:
        subprocess.run(["sudo", "ip", "link", "set", "dev", iface, "down"], check=True)
        subprocess.run(["sudo", "ip", "link", "set", "dev", iface, "address", new_mac], check=True)
        subprocess.run(["sudo", "ip", "link", "set", "dev", iface, "up"], check=True)
    except subprocess.CalledProcessError:
        print("Error changeing interface mac address")



newaddr = generate_random_mac(producent)
change_mac(wybor, newaddr)
print("Your new mac address: ", newaddr, "\n")
print("Do you want the address to change constantly?")
yesno = ["yes", "no"]
yn = questionary.select("", 
    choices=yesno
    ).ask()

if (yn=="yes"):
    try:
        print("How often would you like the mac address to change?(seconds): ")
        s = input()
        s = int(s)
        while (True):
            time.sleep(s)
            newaddr = generate_random_mac(producent)
            change_mac(wybor, newaddr)
            print("Your new address is: ", newaddr)
    except KeyboardInterrupt:
            print("\033[31m   Mac mixer has been stopped\033[0m")
            print("Do you want to restore your previous mac address? ")
            bb = questionary.select("", 
            choices=yesno
            ).ask()
            if (bb=="yes"):
                with open('MACaddr.txt', 'r', encoding='utf-8') as file:
                    oldaddr = file.read()
                    change_mac(wybor, oldaddr)
                    print("Your mac address has been changed to: ", oldaddr)
            else:
                exit()
else:
    exit()