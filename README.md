# Network Switch Monitoring Application

A comprehensive solution for real-time monitoring of Cisco and Huawei network switches with interactive dashboards, asset management, and reporting capabilities.

## Project Structure

```
asset_monitoring/
├── docs/                    # Documentation files
│   ├── context.md          # Project context and overview
│   ├── execution_plan.md   # Project phases and timeline
│   └── requirements.md     # Technical requirements
├── src/                    # Source code
├── tests/                  # Test files
└── README.md               # This file
```

## Getting Started

1. Clone the repository
2. Install dependencies (see `docs/requirements.md` for details)
3. Configure environment variables in `.env` (ensure DB, Redis, and all services match Docker Compose)
4. Start the application using Docker Compose:
   ```bash
   docker-compose up --build
   ```
5. Apply Alembic migrations:
   ```bash
   docker-compose exec app alembic upgrade head
   ```
6. (Optional) Initialize DB from models if migrations are missing.

---

## Documentation Index

- **Project context:** [`docs/context.md`](docs/context.md)
- **Execution plan & phases:** [`docs/execution_plan.md`](docs/execution_plan.md)
- **Requirements:** [`docs/requirements.md`](docs/requirements.md)
- **Troubleshooting & FAQ:** [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)
- **Alembic migration usage:** [`alembic/README`](alembic/README)

---

## Quick Troubleshooting

- **DB errors?** Ensure `.env` and Docker Compose use the same DB host (`db`).
- **Migrations missing?** Run Alembic upgrade as above.
- **API 307 redirect?** Use trailing slash in URLs.
- **Other issues?** See [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).

---

## Features

- Real-time monitoring of network devices
- Interactive dashboards
- Alerting system
- Asset management
- Configuration management
- Reporting engine

## Supported Devices

- **Cisco**: Catalyst 2960/3560/3850/9000, Nexus 2000-9000 series
- **Huawei**: S5700/S6700/S7700/S9700, CE6800/CE12800 series

## License

Copyright (c) 2025 - Asset Monitoring

All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

