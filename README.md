# 📊 Enterprise Observability Stack

[![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?logo=prometheus&logoColor=white)](https://prometheus.io/) [![Grafana](https://img.shields.io/badge/Grafana-F46800?logo=grafana&logoColor=white)](https://grafana.com/) [![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io/) [![Helm](https://img.shields.io/badge/Helm-0F1689?logo=helm&logoColor=white)](https://helm.sh/) [![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/) [![AlertManager](https://img.shields.io/badge/AlertManager-E6522C?logo=prometheus&logoColor=white)](https://prometheus.io/docs/alerting/latest/alertmanager/) [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Kubernetes-first observability stack: scrape hosts and platforms with Prometheus, visualize with Grafana Morning dashboards, and deploy the control plane via **Helm** (`kube-prometheus-stack`) plus in-cluster exporters/ServiceMonitors. Docker Compose remains available for standalone exporters and local labs.

## 🏗️ **Architecture Overview**

```text
┌─────────────────────────────────────────────────────────────┐
│                    Monitoring Targets                       │
├─────────────────┬─────────────────┬─────────────────────────┤
│   Infrastructure│    Applications │      Services           │
│                 │                 │                         │
│ • Linux Servers │ • Airflow       │ • API / OpenAPI         │
│ • Windows Hosts │ • Databases     │ • Web Applications      │
│ • K8s Nodes     │ • Kafka         │ • Custom Exporters      │
└─────────────────┴─────────────────┴─────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Deployment (Kubernetes + Helm)                 │
├─────────────────────────────────────────────────────────────┤
│ • Helm: kube-prometheus-stack (Prometheus / Grafana / AM)   │
│ • Manifests: base/, exporters/, grafana/configmaps, rules/  │
│ • Optional Docker Compose for host-side / lab exporters     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Exporters Layer                            │
├─────────────────────────────────────────────────────────────┤
│ • Node Exporter      • Blackbox Exporter                    │
│ • Windows Exporter   • Database Exporters                   │
│ • Custom Exporters   • Application Metrics                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 Prometheus Stack                            │
├─────────────────────────────────────────────────────────────┤
│ • Metrics Collection    • Time Series Database              │
│ • Alert Rules          • Target Discovery                   │
│ • AlertManager         • Service Discovery                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Grafana Dashboards                         │
├─────────────────────────────────────────────────────────────┤
│ • Infrastructure Monitoring  • Application Performance      │
│ • Business Metrics          • Custom Visualizations         │
│ • Alerting & Notifications  • Multi-tenant Dashboards       │
└─────────────────────────────────────────────────────────────┘
```

## 📁 **Project Structure**

```text
observability/
├── 🔍 prometheus/                   # Prometheus configuration
│   ├── prometheus.yml              # Main configuration
│   ├── alert_rules.yml             # Alerting rules
│   ├── alertmanager.yml            # Alert routing
│   ├── targets/                    # Target configurations
│   │   ├── infrastructure/         # Server monitoring
│   │   │   ├── windows-app.json        # windows-app site targets
│   │   │   ├── linux.json          # Linux servers
│   │   │   └── windows.json        # Windows hosts
│   │   ├── platform/              # Platform services
│   │   │   ├── airflow/            # Airflow monitoring
│   │   │   ├── postgres/           # PostgreSQL metrics
│   │   │   └── influxdb/           # InfluxDB monitoring
│   │   └── service/               # Application services
│   │       └── openapi.json        # API service monitoring
│   └── exporters/                 # Exporter configurations
│       ├── windows/               # Windows exporters
│       └── Docker/                # Containerized exporters
│
├── 📈 grafana/                     # Grafana configuration
│   ├── docker-compose.yml         # Grafana deployment
│   ├── .env                       # Environment variables
│   └── img/                       # Dashboard screenshots
│
├── 🔧 exporter/                    # Custom exporters
│   ├── docker-compose.yml         # Exporter services
│   ├── blackbox/                  # Blackbox exporter config
│   │   ├── blackbox.yml           # Probe configurations
│   │   └── docker-compose.blackbox.yml
│   └── os/                        # OS-specific exporters
│       └── docker-compose.yml
│
└── 📋 docker-compose.yml           # Complete stack deployment
```

## ⚡ **Key Features**

### 🔍 **Comprehensive Monitoring**

- **Infrastructure Monitoring**: Linux/Windows servers, network devices
- **Application Performance**: Airflow, databases, web services
- **Business Metrics**: Custom application metrics and KPIs
- **Multi-site Coverage**: windows-app manufacturing sites integration

### 📊 **Advanced Visualization**

- **Grafana Dashboards**: Pre-configured dashboards for all services
- **Real-time Alerts**: Intelligent alerting with AlertManager
- **Custom Metrics**: Application-specific monitoring capabilities
- **Multi-tenant Views**: Role-based dashboard access

### 🛠️ **Enterprise Features**

- **High Availability**: Clustered Prometheus deployment ready
- **Scalable Architecture**: Horizontal scaling with federation
- **Security**: SSL/TLS encryption and authentication integration
- **Data Retention**: Configurable retention policies and storage

## 🚀 **Quick Start**

### **1. Complete Stack Deployment**

```bash
# Deploy entire observability stack
docker-compose up -d

# Access services
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000
# AlertManager: http://localhost:9093
```

### **2. Individual Service Deployment**

#### **Prometheus Only**

```bash
cd prometheus/
docker-compose -f docker-compose.yml up -d
```

#### **Grafana Only**

```bash
cd grafana/
docker-compose up -d
```

#### **Custom Exporters**

```bash
cd exporter/
# Deploy blackbox exporter
docker-compose -f blackbox/docker-compose.blackbox.yml up -d

# Deploy OS exporters
docker-compose -f os/docker-compose.yml up -d
```

## 🎯 **Monitoring Targets**

### **📡 Infrastructure Targets**

| Category              | Targets                               | Metrics                          |
| --------------------- | ------------------------------------- | -------------------------------- |
| **Linux Servers**     | Production hosts, development servers | CPU, Memory, Disk, Network       |
| **Windows Hosts**     | Windows servers, workstations         | System performance, services     |
| **windows-app Sites** | Manufacturing facility systems        | Industrial metrics, connectivity |
| **Network**           | Switches, routers, firewalls          | Bandwidth, latency, availability |

### **🔧 Platform Services**

| Service        | Port  | Monitoring Focus                              |
| -------------- | ----- | --------------------------------------------- |
| **Airflow**    | 8080  | DAG performance, task duration, worker health |
| **PostgreSQL** | 5432  | Query performance, connections, replication   |
| **InfluxDB**   | 8086  | Write performance, query latency, storage     |
| **MongoDB**    | 27017 | Operations, replication lag, storage          |

### **🌐 Application Services**

- **OpenAPI Services**: Response times, error rates, throughput
- **Web Applications**: User metrics, performance monitoring
- **Custom Applications**: Business-specific KPIs and metrics

## 📊 **Available Exporters**

### **🖥️ System Exporters**

- **Node Exporter**: Linux system metrics
- **Windows Exporter**: Windows system monitoring
- **Blackbox Exporter**: HTTP/HTTPS/DNS/TCP probing

### **🗄️ Database Exporters**

- **PostgreSQL Exporter**: Database performance metrics
- **MySQL Exporter**: MySQL/MariaDB monitoring
- **MongoDB Exporter**: MongoDB cluster metrics
- **InfluxDB Exporter**: Time-series database monitoring

### **🐳 Containerized Exporters**

All exporters are available as Docker containers with pre-configured compose files for easy deployment.

## 🚨 **Alerting & Notifications**

### **Alert Categories**

- **Critical**: System down, database unavailable
- **Warning**: High CPU usage, disk space low
- **Info**: Service restarts, configuration changes

### **Notification Channels**

- **Email**: SMTP integration for critical alerts
- **Slack**: Real-time notifications for teams
- **Webhook**: Custom integrations with external systems

## 📚 **Documentation**

| Component                                                         | Documentation                     |
| ----------------------------------------------------------------- | --------------------------------- |
| **[Prometheus Setup](./prometheus/README.md)**                    | Prometheus configuration guide    |
| **[Grafana Dashboards](./grafana/README.md)**                     | Dashboard setup and customization |
| **[Exporters Guide](./exporter/README.md)**                       | Custom exporter deployment        |
| **[Windows Exporters](./prometheus/exporters/windows/README.md)** | Windows-specific monitoring       |

## 🔧 **Configuration**

### **Environment Variables**

```bash
# Grafana Configuration
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=your-password

# Prometheus Configuration
PROMETHEUS_STORAGE_RETENTION=15d
PROMETHEUS_STORAGE_RETENTION_SIZE=10GB
```

### **Custom Targets**

Add new monitoring targets by creating JSON files in the `targets/` directory:

```json
[
  {
    "targets": ["your-service:port"],
    "labels": {
      "job": "your-application",
      "env": "production"
    }
  }
]
```

## 🛡️ **Security Considerations**

- **Authentication**: Grafana user management and LDAP integration
- **SSL/TLS**: Encrypted communication between components
- **Network Security**: Proper firewall rules and network segmentation
- **Access Control**: Role-based access to dashboards and metrics

## 💡 **Use Cases**

✅ **Infrastructure Monitoring** - Server health, network performance  
✅ **Application Performance** - Response times, error rates, throughput  
✅ **Business Intelligence** - KPI tracking, operational metrics  
✅ **DevOps Integration** - CI/CD pipeline monitoring, deployment tracking  
✅ **Capacity Planning** - Resource utilization analysis, growth forecasting  
✅ **Incident Response** - Real-time alerting, automated notifications

## 🏆 **Production Stats**

- **Multi-site Monitoring**: windows-app manufacturing facilities
- **100+ Targets**: Servers, applications, and services
- **24/7 Alerting**: Real-time incident detection
- **Enterprise Scale**: TB-level metrics storage and processing
- **High Availability**: Clustered deployment with redundancy

## 📄 **License**

This project is licensed under the MIT License. See [LICENSE](./LICENSE) for details.

---

**📊 Enterprise Observability at Scale**  
Built with ❤️ for comprehensive infrastructure and application monitoring.
