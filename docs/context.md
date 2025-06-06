# Network Switch Monitoring Application Context

## Primary Objective
Develop a robust application for real-time remote monitoring of Cisco and Huawei switches, featuring interactive dashboards, asset management, and comprehensive reporting.

## Technology Stack
### Backend (Python)
- **Framework**: FastAPI (ASGI for high performance)
- **Database**:
  - PostgreSQL (structured data)
  - TimescaleDB (time-series metrics)
- **Asynchronous Processing**: Celery + Redis
- **Switch Communication**:
  - PySNMP (SNMPv2/v3)
  - Netmiko (SSH)
- **Internal Monitoring**: Prometheus + Grafana

### Frontend
- **Framework**: React with TypeScript
- **Visualization**:
  - Recharts (main charts)
  - D3.js (network topology)
- **UI Kit**: Material-UI
- **Real-time Communication**: Socket.io

## Monitored Metrics
### Devices (Cisco & Huawei)
| Category            | Specific Metrics                          | Protocol |
|---------------------|------------------------------------------|-----------|
| **System Health**   | CPU Usage, Memory, Temperature, Uptime    | SNMP      |
| **Interfaces**      | Status, Traffic (in/out), Errors, Discards| SNMP      |
| **Power**           | Consumption, PSU Status, POE Usage        | SNMP      |
| **Security**        | Login Attempts, Configuration Changes      | Syslog    |
| **Storage**         | Flash Usage, Running/Startup Configs      | SSH       |

### Supported Models
| Vendor  | Common Models                         | OS Versions  |
|---------|--------------------------------------|--------------|
| **Cisco** | Catalyst 2960/3560/3850/9000        | IOS, IOS-XE  |
|          | Nexus 2000/3000/5000/7000/9000      | NX-OS        |
| **Huawei**| S5700/S6700/S7700/S9700 Series      | VRP V5/V8    |
|          | CE6800/CE12800 Series               | VRP V8       |

## Functional Requirements
1. Real-time monitoring (<2s latency)
2. Unified dashboard with views by:
   - Physical location
   - Business criticality
   - Device type
3. Configurable alert system based on:
   - Performance thresholds
   - Behavior patterns
   - Business hours
4. Historical reports:
   - Monthly availability
   - Top 10 problematic interfaces
   - Capacity trends
5. Centralized management of:
   - Access credentials
   - Backup configurations
   - Firmware/OS versions

## Non-Functional Requirements
- **Performance**: Support for 1,000+ devices
- **Availability**: 99.95% uptime
- **Security**:
  - OAuth2 authentication
  - AES-256 encryption
  - Role-Based Access Control (RBAC)
- **Scalability**: Containerized architecture (Docker/K8s)
