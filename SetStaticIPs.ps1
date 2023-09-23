
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

#192.168.27.120 # Alphapix
#192.168.27.140 # HP5V Tree
#192.168.27.134 # Wally Wings
#192.168.27.156 # Kulp W Fence

netsh interface ipv4 add neighbors "Ethernet" "192.168.25.5" "02-fe-00-40-00-1a"
netsh interface ipv4 add neighbors "Ethernet" "192.168.25.10" "82-a5-73-51-3c-02"
netsh interface ipv4 add neighbors "Ethernet" "192.168.25.20" "0e-62-75-59-07-bb"
netsh interface ipv4 add neighbors "Ethernet" "192.168.25.100" "36-21-75-c0-4f-e7"
netsh interface ipv4 add neighbors "Ethernet" "192.168.25.152" "98-f0-7b-5b-ae-28"
netsh interface ipv4 add neighbors "Ethernet" "192.168.25.180" "be-b4-04-12-11-67"

netsh interface ipv4 add neighbors "Ethernet" "192.168.26.30" "ee-97-d7-23-5a-da"
netsh interface ipv4 add neighbors "Ethernet" "192.168.26.90" "4e-d4-8c-7c-f7-3e"
netsh interface ipv4 add neighbors "Ethernet" "192.168.26.130" "24-76-25-f2-1f-cc"
netsh interface ipv4 add neighbors "Ethernet" "192.168.26.154" "98-f0-7b-a8-24-16"
netsh interface ipv4 add neighbors "Ethernet" "192.168.26.160" "22-fb-f2-d3-60-13"

netsh interface ipv4 add neighbors "Ethernet" "192.168.27.50" "ce-39-7e-b7-6e-f8"
netsh interface ipv4 add neighbors "Ethernet" "192.168.27.60" "ca-61-60-df-95-f6"
netsh interface ipv4 add neighbors "Ethernet" "192.168.27.70" "82-7c-2f-bb-41-d0"
netsh interface ipv4 add neighbors "Ethernet" "192.168.27.80" "32-11-b5-93-7a-cf"
netsh interface ipv4 add neighbors "Ethernet" "192.168.27.110" "ea-69-c9-b8-06-b1"
netsh interface ipv4 add neighbors "Ethernet" "192.168.27.132" "24-76-25-ef-e4-bd"
netsh interface ipv4 add neighbors "Ethernet" "192.168.27.150" "60-b6-e1-17-e6-5d"
netsh interface ipv4 add neighbors "Ethernet" "192.168.27.158" "00-02-02-04-61-8f"

