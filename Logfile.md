sudo apt update
sudo apt install cups printer-driver-hpcups hplip python3-flask
sudo usermod -aG lpadmin $USER

lsusb | grep -i hp
sudo lpinfo -v

sudo lpadmin -p HP_P2055dn -E -v "usb://HP/LaserJet%20P2055dn?serial=S29HJ4C" -m everywhere

sudo lpadmin -p HP_P2055dn -E \
  -v "usb://HP/LaserJet%20P2055dn?serial=S29HJ4C" \
  -m drv:///hpcups.drv/hp-laserjet_p2055dn-pcl3.ppd

  sudo lpadmin -p SRV_HP_P2055dn -E \
  -v "usb://HP/LaserJet%20P2055dn?serial=S29HJ4C" \
  -m drv:///hpcups.drv/hp-laserjet_p2055dn-pcl3.ppd


sudo lpadmin -x HP_2055dn

 lp -d SRV_HP_P2055dns

# Ext
sudo lpadmin -p HP_OPi -E \
  -v ipp://100.96.112.122:631/printers/SRV_HP_P2055dn \
  -m everywhere
lpstat -p HP_OPi