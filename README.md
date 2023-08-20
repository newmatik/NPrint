# NPrint

Raspberry Pi (single board computer) based Hardware Print Server with 
REST API to print on ZPL enabled label printers

## Hardware Requirements

### Raspberry Pi
 - Raspberry Pi 4 Model B (4GB RAM)
 - Raspberry Pi 4 Enclosure
 - Raspberry Pi 15W Power Supply (EU)
 - 16 GB MicroSD-Card (Class10)

### Label Pritner with ZPL Protocol
 - ZD411d for 5cm labels (batch label)
 - Zebra GK420d or Labelident BP41 for 10cm labels (shipping labels)

## OS SETUP OF RASPBERRY PI

Download Raspberry Pi Imager and download a fresh image of Raspberry Pi OS onto the SD Card.
We recommend using Raspberry Pi OS Lite (32-bit). Set the advanced settings like hostname
and passwords before flashing the image so you can reduce configuration efforts. This can be
done in Raspberry Pi Imager with the gear symbol, before flashing.

### Default User 
Username: nprint
Password: smart4pi

## Basic System Configuration

Connect to the device through SSH (replace with actual IP address).
Log in with user "nprint" and password "smart4pi".

```
ssh nprint@10.1.0.68 $
```

### System Update

Update Raspberry Pi OS and all packages with apt-get package manager by running this command:

```
sudo apt-get update -y && sudo apt-get upgrade -y && sudo apt-get dist-upgrade -y && sudo apt-get autoclean -y && sudo apt-get clean -y && sudo apt autoremove -y && sudo apt autoremove -y
```

### Setting Hostname

```
sudo raspi-config
```

Go to Stystem Options -> Hostname
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

Because we want to connect to the admin page through our computer we need to allowing the 
admin page remotely. We will also set that we share our printers in the network. This will
require us to restart the CUPS service after the changes have been made to take effect.

```
sudo cupsctl --remote-admin --share-printers --remote-any
sudo systemctl restart cups
```

After installing CUPS and adding a user, or set of users, to the user group lpadmin, 
the rest of the configuration can be done via the CUPS Administration page. 
You can access this page on the Raspberry Pi by opening a web browser and going to 
the address: http://10.1.0.68:631/ (replace with actual IP address).

### Share CUPS Printer via Bonjour/IPP Protocol

CUPS can announce its presence on the network via mDNS (multicast DNS) and DNS-SD 
(DNS Service Discovery) protocol, which is also known as Bonjour. In order to do that, 
you need to install and run avahi-daemon, which is a service similiar to the Apple Bonjour 
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

Connect the printers to your raspberry PI via USB connection. In our case we will connect
a Zebra ZLP 2824 Plus as a batch label printer and a Zebra GK420d as a box label printer.

Open the CUPS admin page http://10.1.0.68:631/ (replace with actual IP address) and add a new printer.
Select the local barcode printer e.g. "Zebra Technologies ZTC TLP 2824 Plus (Zebra Technologies ZTC 
TLP 2824 Plus)". Set a logical name, description and location.

### Example for Batch Label Printer:

Name: WE1-Batchlabel
Description: WE1 Batch Label Printer (ZLP2824 Plus)
Location: WE1
Select Netrowk Print share

In step 5 select the Model (e.g. "Zebra ZPL Label Printer (en)") and press Add Printer.

Under "General" configure the label size. In our case we select "custom" label size with
53x55 mm size with 203 dpi. Web Sensing and Direct Thermotransfermedia as standard settings.
Go to "Printer Settings" before saving and adjust darkness to 30 and print mode to "tear off".
Set the print rate to the highest print speed.

Now save these defaults and go to the printer page to print a test page.

### Example for Box Label Printer:

Name: WE1-Boxlabel
Description: WE1 Box Label Printer (GK420d)
Location: WE1
Select Netrowk Print share

In step 5 select the Model (e.g. "Zebra ZPL Label Printer (en)") and press Add Printer.

Under "General" configure the label size. In our case we select "custom" label size with
101x152 mm size with 203 dpi. Web Sensing and Direct Thermotransfermedia as standard settings.
Go to "Printer Settings" before saving and adjust darkness to 30 and print mode to "tear off".
Set the print rate to the highest print speed.

Now save these defaults and go to the printer page to print a test page.

### Are the labels printed inverted?

To change the orientation by 180 degrees run the following in the terminal with the correct printer name

lpadmin -p WE1-Batchlabel -o orientation-requested-default=6

## SETTING UP NPRINT

### About Flask REST API Development

For basic concepts of how this REST API is built, check out the following resources:
- https://auth0.com/blog/developing-restful-apis-with-python-and-flask/
- https://flask-restful.readthedocs.io/en/latest/

Clone the project into your home folder. This will create the project folder at "/home/nprint/NPrint":

```
clone https://github.com/elexess/NPrint.git
cd NPrint
```

Install pienv requirements through PIP:

```
pip install pipenv
pipenv --python 3.9.2
```

Install the PIP requirements (Pipfile) through pipenv:
```
pipenv install
pipenv shell
```

Copy .env_sample to .env and modify as needed:

```
cp .env_sample .env
```

We have to edit the ```$PATH``` variable to be able to run flask directly. 
To do that, let's ```touch ~/.bash_aliases``` and then ```echo "export PATH=$PATH:~/.local/bin" >> ~/.bash_aliases```. Please exit SSH and reconnect for the new path to take effect.

## START NPRINT

Make sure to enable the pipenv:

```
pipenv shell
```

To start NPrint in developer mode simply run the following in your NPrint folder:

```
flask run
```

Check if the flask app is runnign by opening the URL in your browser:

http://10.1.0.68:3000/api/ping (replace with actual IP)