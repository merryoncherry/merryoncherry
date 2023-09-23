
route ADD 192.168.25.0 MASK 255.255.255.0 192.168.25.1 METRIC 1
route ADD 192.168.26.0 MASK 255.255.255.0 192.168.26.1 METRIC 1
route ADD 192.168.27.0 MASK 255.255.255.0 192.168.27.1 METRIC 1

# Syntax
# netsh interface ipv4 add neighbors "NetworkInterfaceName" "IPAddress" "MACAddress"
#
# Ethernet
# USBHub26
# USBHub27

#192.168.25.8 ???

#192.168.26.30
#192.168.26.90
#192.168.26.130
#192.168.26.154
#192.168.26.160

#192.168.27.50
#192.168.27.60
#192.168.27.70
#192.168.27.80
#192.168.27.110
#192.168.27.120 # Alphapix
#192.168.27.140 # HP5V Tree
#192.168.27.132
#192.168.27.134
#192.168.27.150
#192.168.27.156
#192.168.27.158

netsh interface ipv4 add neighbors "Ethernet" "192.168.25.5" "02-fe-00-40-00-1a"
netsh interface ipv4 add neighbors "Ethernet" "192.168.25.10" "82-a5-73-51-3c-02"
netsh interface ipv4 add neighbors "Ethernet" "192.168.25.20" "0e-62-75-59-07-bb"
netsh interface ipv4 add neighbors "Ethernet" "192.168.25.100" "36-21-75-c0-4f-e7"
netsh interface ipv4 add neighbors "Ethernet" "192.168.25.152" "98-f0-7b-5b-ae-28"
netsh interface ipv4 add neighbors "Ethernet" "192.168.25.180" "be-b4-04-12-11-67"


