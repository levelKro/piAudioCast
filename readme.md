# piAudioCast

This project is for turn a Raspberry Pi into a small Audio Player controled by Web interface. Can support local files, usb files and Internet radio.

![Screenshot](screenshot-22-7-4.png)

## Features

* Play audio file like WAV, MP3, AUD, M4A, WMA, MID, FLAC, OGG (suggest file extension if needed)
* Play Internet Radio over HTTP, like Shoutcast and Icecast
* Play all file in a folder (not sub directory, but planned)
* Web Interface with all controls
* Auto-install new Wifi configuration by USB drive
* Compatible with WM8960 hat
* Support button for volume loop
* Music folder available by Windows share (Samba)
* [planned] Random play
* [planned] Loop play
* [planned] Upload files

## Requirement

* Raspberry Pi (0/1/2/3/4)
* Raspbian OS Lite
* Local network (LAN or WLAN)
* Audio out (by HDMI or Speaker/Headphone, depend of your configuration)

## Install

 ...To Do...
```
guide for install ...
 ... hostname
 ... samba
 ... usbmount
 ... directories
 ... requirement for python
 ... piaudiocast
 
```
 
## Auto-install Wifi

Just put USB drive on your pi with the `wpa_supplicant.conf` file, configured like the Raspberry Pi requirement. The file was copied into `/boot` folder and the Raspberry will reboot.

## Boot and Poweroff

The script come with sound for help the user to known what the device do. One sound if when the system is started, another when do a power off or reboot or when the new Wifi file configuration was found.

## How to use

Juste boot the device and wait, when you ear the boot sound, you can connect to Raspberry Pi IP address on normal HTTP port, like http://192.168.0.10 or http://picast (if `picast` is the hosttname of your device).