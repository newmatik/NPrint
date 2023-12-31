# NPrint

Raspberry Pi (single board computer) based Hardware Print Server with 
REST API to print on ZPL enabled label printers.

## Hardware Requirements

### Raspberry Pi
 - Raspberry Pi 4 Model B 4 GB RAM (Conrad: 2138865)
 - Kühllörper Raspberry Pi (Conrad: 2247647)
 - Raspberry Pi 4 Enclosure (Conrad: 2140254)
 - Raspberry Pi 15W Power Supply EU (Conrad: 2140238 - VQ)
 - 16 GB Micro-SD-Card Class10 (Conrad: 1421772 - VQ)

### Label Printer with ZPL Protocol
 - ZD411d for 5 cm labels (batch label)
 - Zebra GK420d or Labelident BP41 for 10 cm labels (shipping labels)

## OS Setup of Raspberry

Download Raspberry Pi Imager and download a fresh image of Raspberry Pi OS onto the SD Card.
We recommend using Raspberry Pi OS Lite (32-bit). Set the advanced settings like hostname
and passwords before flashing the image, so you can reduce configuration efforts. This can be
done in Raspberry Pi Imager with the gear symbol, before flashing.

### Default User 
 - Username: "nprint"
 - Password: "smart4pi"

## Basic System Configuration

Connect to the device through SSH (replace with actual IP address).
Log in with user "nprint" and password "smart4pi".

```
ssh nprint@10.1.1.128 $
```

### System Update

Update Raspberry Pi OS and all packages with apt-get package manager by running this command:
```
sudo apt-get update -y && sudo apt-get upgrade -y && sudo apt-get dist-upgrade -y &&
sudo apt-get autoclean -y && sudo apt-get clean -y && sudo apt autoremove -y &&
sudo apt autoremove -y
```

### Setting Hostname

```
sudo raspi-config
```

Go to System Options → Hostname
example: nprint-we1.de.newmatik.com

After setting the hostname, reboot once.

### Installing the basics

```
sudo apt-get install -y vim git python3-pip 
```

### Installing CUPS

The system uses CUPS as the print server. Install:

```
sudo apt-get install -y cups cups-client lpr libcups2-dev
```

CUPS uses the user group “lpadmin” to know who is authorized to administer the printers.
After installing CUPS, add our user "nprint" to the user group “lpadmin”:

```
sudo usermod -a -G lpadmin nprint
```

Because we want to connect to the admin page through our computer we need to allow the 
admin page remotely. We will also set that we share our printers in the network. This will
require us to restart the CUPS service after the changes have been made to take effect.

```
sudo cupsctl --remote-admin --share-printers --remote-any
sudo systemctl restart cups
```

After installing CUPS and adding a user, or set of users, to the user group lpadmin, 
the rest of the configuration can be done via the CUPS Administration page. 
You can access this page on the Raspberry Pi by opening a web browser and going to 
the address: http://10.1.1.128:631/ (replace with actual IP address).

### Securing with UFW Firewall

```
sudo apt-get install -y ufw

# SSH and DNS
sudo ufw allow ssh
sudo ufw allow dns

# Flask Development Port
sudo ufw allow 3000

# CUPS IPP Printer Sharing
sudo ufw allow 631/tcp
sudo ufw allow 5353/udp

# CUPS IPP Printer Sharing
sudo ufw allow 137/udp
sudo ufw allow 139/tcp
sudo ufw allow 445/tcp

# Enable UFW
sudo ufw enable
```

### Share CUPS Printer via Bonjour/IPP Protocol

CUPS can announce its presence on the network via mDNS (multicast DNS) and DNS-SD 
(DNS Service Discovery) protocol, which is also known as Bonjour. In order to do that, 
you need to install and run avahi-daemon, which is a service similar to the Apple Bonjour 
service that allows computers to automatically discover shared devices and services on the local network.

```
sudo apt install avahi-daemon -y
sudo systemctl start avahi-daemon -y
sudo systemctl enable avahi-daemon -y
sudo ufw allow 5353/udp
```

Because macOS and most Linux desktop distributions have CUPS installed as the default printing system, 
once you have enabled printer sharing via Bonjour/IPP on the Ubuntu box, macOS and Linux users in the 
same network can automatically use the printer. When they click the print option in applications 
(word processors, email readers, photo editors, and web browsers), the printer will be automatically available. They don’t have to explicitly add the printer.

```
sudo apt install cups-ipp-utils -y
sudo systemctl restart cups
```

## Printer Setup

Connect the printers to your Raspberry Pi via USB connection. In our case we will connect
a Zebra ZLP 2824 Plus as a batch label printer and a Zebra GK420d as a box label printer.

Open the CUPS admin page http://10.1.1.128:631/ (replace with actual IP address) and add a new printer.
Select the local barcode printer e.g. "Zebra Technologies ZTC TLP 2824 Plus (Zebra Technologies ZTC 
TLP 2824 Plus)". Set a logical name, description and location.

### Example for Batch Label Printer:

Name: WE1-Batchlabel
Description: WE1 Batch Label Printer (ZLP2824 Plus)
Location: WE1
Select Network Print share

In step 5 select the Model (e.g. "Zebra ZPL Label Printer (en)") and press Add Printer.

Under "General" configure the label size. In our case we select "custom" label size with
53x55 mm size with 203 dpi. Web Sensing and "Direct Thermo Transfer Media" as standard settings.
Go to "Printer Settings" before saving and adjust darkness to 30 and print mode to "tear off".
Set the print rate to the highest print speed.

Now save these defaults and go to the printer page to print a test page.

### Example for Box Label Printer:

Name: WE1-Boxlabel
Description: WE1 Box Label Printer (GK420d)
Location: WE1
Select Network Print share

In step 5 select the Model (e.g. "Zebra ZPL Label Printer (en)") and press Add Printer.

Under "General" configure the label size. In our case we select "custom" label size with
101x152 mm size with 203 dpi. Web Sensing and "Direct Thermo Transfer Media" as standard settings.
Go to "Printer Settings" before saving and adjust darkness to 30 and print mode to "tear off".
Set the print rate to the highest print speed.

Now save these defaults and go to the printer page to print a test page.

### Are the labels printed inverted?

To change the orientation by 180 degrees run the following in the terminal with the correct printer name

```
lpadmin -p WE1-Batchlabel -o orientation-requested-default=6
```

## Setting up NPrint

### About Flask REST API Development

For basic concepts of how this REST API is built, check out the following resources:
- https://auth0.com/blog/developing-restful-apis-with-python-and-flask/
- https://flask-restful.readthedocs.io/en/latest/

Clone the project into your home folder. This will create the project folder at "/home/nprint/NPrint":

```
clone https://github.com/elexess/NPrint.git
cd NPrint
```

#### On MacOS

```
brew install pipenv

```

#### On Raspberry Pi

Install pipenv requirements through PIP:

```
pip install pipenv
pipenv --python 3.9.2
```

Install the PIP requirements (Pipfile) through pipenv:
```
pipenv install
```

Copy .env_sample to .env and modify as needed:

```
cp .env_sample .env
```

Modify the API-KEY in .env or keep the default API-KEY "g897hdfsgo987oh9gbinuhjvc".
Make sure to change the API-KEY on a production system.

We have to edit the ```$PATH``` variable to be able to run flask directly. 
To do that, create the file with ```touch ~/.bash_aliases``` and then ```echo "export PATH=$PATH:~/.local/bin" >> ~/.bash_aliases```. Please exit SSH and reconnect for the new path to take effect.

## Start NPrint

Make sure to enable the pipenv:

```
pipenv shell
```

To start NPrint in developer mode simply run the following in your NPrint folder:

```
flask run
```

Check if the flask app is running by opening the URL in your browser:

http://10.1.1.128:3000/api/ping (replace with actual IP)

# Testing the application

Open demo.html to test basic functionality, use Postman or the following CURL examples.

Ping:
```
curl http://localhost:3000/api/ping
```

Get Printers installed in CUPS:
```
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"api_key": "g897hdfsgo987oh9gbinuhjvc"}' \
  http://localhost:3000/api/printers
```

Update the API-KEY:
```
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"api_key": "OLD API KEY", "new_api_key": "NEW API KEY"}' \
  http://localhost:3000/api/update/api_key
```

For a full list of API Endpoints check nprint.py