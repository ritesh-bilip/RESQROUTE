<!-- We need to store two things: Crisis Incidents (what is happening on the ground) and Logistics Hubs (where the supplies are). Open core/models.py and replace it with this clean, straightforward code:

Username (leave blank to use 'dasri'): res20
Email address: res2072026@gmail.com
Password: RES7047648483
 -->



## 🎯 What is "ResQRoute" For?

In major humanitarian crises—like acute climate shocks, earthquakes, or supply chains broken by conflict—the biggest issue isn’t usually a lack of resources globally. **The bottleneck is coordination at the local level (the "last mile" problem).**

Traditional logistics software (like what Amazon uses) assumes stable electricity, constant 5G internet, working roads, and static warehouses. In a crisis zone, none of those exist. Roads wash away in hours, fuel depots run dry, and cell towers collapse.

**ResQRoute** is built specifically for **unstable, high-velocity environments**. It acts as a lightweight, decentralized routing grid that coordinates needs and resources when traditional infrastructure is failing.

---

## 🛠️ The Real-World Problems vs. ResQRoute’s Solutions

| The Real-World Failure | How ResQRoute Solves It |
| --- | --- |
| **The Blind Spot:** Centralized aid agencies take 24–72 hours to map damage, creating a dangerous data lag while people need immediate help. | **Crowdsourced Telemetry:** Local citizens and field workers act as sensors, instantly submitting live coordinate data of hazards (e.g., mudslides, collapsed buildings) directly from their phones. |
| **The "Dead Zone" Problem:** Field workers lose internet access entirely, meaning they cannot report casualties or resource shortages. | **Offline-First Synchronization:** The application caches data locally on devices using light databases and syncs it automatically using resilient UUID conflict logic the moment a faint cell signal or satellite connection is found. |
| **Wasted Resources:** Aid trucks blindly drive into flooded zones, getting stuck, while another route just 2 miles away is perfectly clear. | **Spatial Visibility (GeoDjango):** The backend instantly cross-references coordinate points against dynamic danger zones (polygons) to dynamically flag which supply hubs are cut off and which are accessible. |

---

## 👥 Who Uses It & What Services Do They Get?

This platform serves three distinct user groups, providing each with custom services based on their environment:

### 1. Field Volunteers & First Responders (The Eyes on the Ground)

* **The Service:** A mobile-responsive web portal optimized to work on incredibly low bandwidth.
* **What they do with it:**
* Drop a digital pin on a map to log a new hazard (e.g., "Live power lines down here").
* Request immediate specialized assets (e.g., "We need an inflatable boat at these exact coordinates").
* Check a localized offline map showing verified safe paths to the nearest medical hub.



### 2. Crisis Dispatchers & Logistics Coordinators (The Brains in the Hub)

* **The Service:** A live, real-time dashboard powered by WebSockets that updates continuously without manual page refreshes.
* **What they do with it:**
* Monitor incoming chaotic data streams and verify reports.
* See a live inventory of supplies across all active regional warehouses.
* Run spatial radius queries to find the closest asset to an emergency (e.g., *"Show me all operational 4x4 trucks within 10 kilometers of Incident X"*).



### 3. Affected Citizens / The Public (The Crowdsourced Signal)

* **The Service:** A ultra-lightweight, public-facing SMS or web form.
* **What they do with it:**
* Submit basic SOS signals or register their safety status.
* View real-time public updates regarding where clean drinking water distribution trucks will be parked.



---

## 💡 Why This Project Matters For Your Portfolio

If you build an e-commerce site, an interviewer will ask you how you designed the database tables.

If you build **ResQRoute**, an interviewer will ask you: *"How did you handle race conditions when two dispatchers tried to allocate the same remaining medical kit to two different locations?"* or *"How did you keep the database from grinding to a halt when querying thousands of complex spatial coordinates?"*

It proves you don't just write code—you build software that keeps working when the real world gets messy.
To build **ResQRoute** professionally, we cannot use a standard monolithic architecture where Django handles everything synchronously. If a disaster hits and thousands of field agents or IoT devices flood the server with spatial data, a typical synchronous Django setup will drop connections, timing out right when people need it most.

We need a **decentralized, event-driven architecture** that isolates heavy GIS computing, protects the database from connection spikes, and handles real-time data streaming asynchronously.

---

## 🏗️ High-Level System Architecture

Here is how the data flows through the system, separated into logical tiers:

```
[ Field Mobile App / Web / SMS Clients ]
                  │
                  ▼  (HTTPS / WSS Protocols)
      [ Nginx Reverse Proxy / Load Balancer ]
                  │
         ┌────────┴────────┐
         ▼ (WSGI)          ▼ (ASGI / WebSockets)
   [ Django / Gunicorn ]   [ Django Channels / Daphne ]
   (REST API, Auth,        (Live Map Updates, 
    Business Logic)         Real-time Dispatch Streams)
         │                         │
         ├─────────────────────────┼────────────────────────┐
         ▼                         ▼                        ▼
[ PostgreSQL + PostGIS ]   [ Redis Broker ] ◄───► [ Celery Workers ]
(Spatial Data, Audits,     (Pub/Sub, Caching,     (Heavy Route Optimization,
 Multi-Polygon Zones)       Task Queue)            Third-Party Weather Sync)

```

---

## 🗺️ Architectural Core Tiers

### 1. Ingress & Routing Tier (Nginx)

* **Role:** Nginx acts as the gatekeeper. It terminates SSL/TLS certificates and inspects incoming traffic headers.
* **Routing Logic:** It separates traffic on a path basis. Standard API requests (`/api/v1/`) are passed to **Gunicorn** (WSGI). Persistent real-time connections (`/ws/`) are routed to **Daphne** (ASGI) to manage WebSockets without tying up application workers.

### 2. Application & Execution Tier (Django + Channels)

* **Django (WSGI Layer):** Handles user authentication, RBAC (Role-Based Access Control) for dispatchers versus volunteers, data validation through DRF, and structural database reads/writes.
* **Django Channels (ASGI Layer):** Maintains open stateful channels to dispatch dashboards. It listens to internal events and instantly pushes JSON payloads to clients when incident conditions change.

### 3. Asynchronous Task Tier (Celery + Redis)

* **Role:** Heavy calculations must never block the user request. When a volunteer submits a 5MB offline telemetry sync package, Django validates the payload structure, immediately writes it to a temporary staging area, returns an `HTTP 202 Accepted` status, and offloads processing to **Celery**.
* **Tasks Handled:**
* Geospatial calculations (determining if an incident sits inside a hazardous polygon).
* External API polling (fetching live radar data from meteorological services every 5 minutes).
* SMS notification batches to affected populations near a hazard zone.



### 4. Data Storage Tier (PostgreSQL + PostGIS + Redis Cache)

* **PostgreSQL with PostGIS:** The absolute source of truth. Spatial indexes (`R-Tree`) are built over `Geometry` and `Geography` columns. This structure allows the database to instantly filter points within geometric bounds without executing full-table scans.
* **Redis:** Serves a double purpose. It acts as the high-speed caching layer for static data (like list of active logistics hubs) and acts as the transit memory broker for Celery and WebSocket channels.

---

## 📡 The Data Lifecycle: Handling an Emergency SOS Signal

To see how these architectural components communicate cleanly, let's track a single real-world event: **A volunteer reports a collapsed bridge in a storm zone.**

```
[Volunteer Client]     [Django API]      [Celery Worker]     [PostGIS DB]    [Channels/Daphne]   [Dispatcher UI]
        │                   │                   │                  │                 │                  │
        │── Submit SOS ────>│                   │                  │                 │                  │
        │   (Lat/Lon, UUID) │                   │                  │                 │                  │
        │                   │── Write Record ─────────────────────>│                 │                  │
        │                   │   (Status: Raw)   │                  │                 │                  │
        │                   │                   │                  │                 │                  │
        │                   │── Trigger Task ──>│                  │                 │                  │
        │<── Return 202 ────│                   │                  │                 │                  │
        │    (Accepted)     │                   │── Spatial Query >│                 │                  │
        │                   │                   │   (Check Zones)  │                 │                  │
        │                   │                   │                  │                 │                  │
        │                   │                   │<── Return Results│                 │                  │
        │                   │                   │                  │                 │                  │
        │                   │                   │── Update Status >│                 │                  │
        │                   │                   │   (Status: Verified)               │                  │
        │                   │                   │                                    │                  │
        │                   │                   │── Broadcast Event ────────────────>│                  │
        │                   │                   │                                    │── Push Payload ─>│

```

1. **Ingress:** The field volunteer app sends an offline-cached POST request containing GPS coordinates, a locally generated UUID, and a description.
2. **Ingest:** Django receives it, authenticates the device token, ensures the UUID does not conflict with existing records, saves the row with a raw status, and pushes the event id to Redis. Django instantly frees the client connection by returning `202 Accepted`.
3. **Process:** A Celery worker picks up the task from Redis, loads the coordinate point, and runs an internal spatial intersection query against known active flood zones stored in PostGIS.
4. **Evaluate:** The worker discovers the point sits directly within a dynamic high-risk flood polygon. It updates the incident row severity to `CRITICAL`.
5. **Broadcast:** Upon saving the row, a Django post-save signal executes, pushing a message containing the clean JSON payload into the Django Channels group layer.
6. **Deliver:** Daphne routes this real-world update through open WebSockets straight to the maps of active disaster dispatchers within 100 milliseconds of calculation completion.

---

## 🔒 Security & Resilience Design Principles

* **Idempotency Keys:** Every data submission uses Client-Side generated UUIDs. If a field device loses connection midway through a POST request and resends the data three times, Django checks the database for that UUID first, ignoring duplicate payloads to save database processing power.
* **Rate Limiting at Edge:** Nginx throttles public-facing ingestion endpoints using leaky bucket algorithms. This ensures malicious bots or faulty IoT hardware cannot inadvertently launch a Denial of Service (DoS) attack on the routing grid during a real emergency.
* **Database Connection Pooling:** Because WebSockets keep long-lived connections open, we do not let them connect directly to Postgres. We route analytical tasks through Celery or use a pooler like **PgBouncer** to prevent the database from running out of file descriptors.
---