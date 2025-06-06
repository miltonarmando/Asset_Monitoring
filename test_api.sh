#!/bin/bash
set -e
API_URL="http://localhost:8000/api/v1/devices/"
set -x
echo "[1] Create device"
CREATE=$(curl -s -X POST -H "Content-Type: application/json" --data '{
  "hostname": "test-device-2",
  "ip_address": "192.168.100.102",
  "vendor": "cisco",
  "model": "3750",
  "os_version": "15.2(4)E10",
  "snmp_community": "public",
  "snmp_port": 161,
  "ssh_username": "admin",
  "ssh_password": "password"
}' $API_URL)
echo "$CREATE"
DEVICE_ID=$(echo "$CREATE" | grep -o '"id":[0-9]*' | grep -o '[0-9]*')

if [ -z "$DEVICE_ID" ]; then echo "[FAIL] Device creation failed"; exit 1; fi

# [2] List devices
echo "[2] List devices"
curl -s $API_URL | jq

# [3] Get device by ID
echo "[3] Get device by ID $DEVICE_ID"
curl -s $API_URL/$DEVICE_ID | jq

# [4] Update device
echo "[4] Update device"
UPDATE=$(curl -s -X PUT -H "Content-Type: application/json" --data '{
  "hostname": "test-device-2-updated",
  "ip_address": "192.168.100.102",
  "vendor": "cisco",
  "model": "3850",
  "os_version": "16.3.6",
  "snmp_community": "private",
  "snmp_port": 162,
  "ssh_username": "admin2",
  "ssh_password": "newpass"
}' $API_URL/$DEVICE_ID)
echo "$UPDATE" | jq

# [5] Create interface
echo "[5] Create interface"
INTERFACE=$(curl -s -X POST -H "Content-Type: application/json" --data '{
  "name": "GigabitEthernet0/1",
  "description": "Uplink port",
  "if_index": 1
}' $API_URL/$DEVICE_ID/interfaces/)
echo "$INTERFACE" | jq

# [6] List interfaces
echo "[6] List interfaces"
curl -s $API_URL/$DEVICE_ID/interfaces/ | jq

# [7] Add device metric
echo "[7] Add device metric"
METRIC=$(curl -s -X POST -H "Content-Type: application/json" --data '{
  "cpu_usage": 30,
  "memory_usage": 60,
  "status": "online"
}' $API_URL/$DEVICE_ID/metrics/)
echo "$METRIC" | jq

# [8] List device metrics
echo "[8] List device metrics"
curl -s $API_URL/$DEVICE_ID/metrics/ | jq

# [9] Add interface metric
echo "[9] Add interface metric"
IMETRIC=$(curl -s -X POST -H "Content-Type: application/json" --data '{
  "in_octets": 123456,
  "out_octets": 654321,
  "in_errors": 0,
  "out_errors": 0
}' $API_URL/$DEVICE_ID/interfaces/GigabitEthernet0%2F1/metrics/)
echo "$IMETRIC" | jq

# [10] List interface metrics
echo "[10] List interface metrics"
curl -s $API_URL/$DEVICE_ID/interfaces/GigabitEthernet0%2F1/metrics/ | jq

# [11] Delete device
echo "[11] Delete device"
curl -s -X DELETE $API_URL/$DEVICE_ID -w "\nStatus: %{http_code}\n"

# [12] Confirm device deletion
echo "[12] Confirm device deletion (should 404)"
curl -s -o /dev/null -w "%{http_code}\n" $API_URL/$DEVICE_ID
