# Azure SQL Database Setup Guide (Free Tier)

This guide walks you through creating a free Azure SQL Database for the patent intelligence demo. The free tier includes **100,000 vCore-seconds** of compute and **32 GB of storage** — more than enough for this project.

Total time: ~10 minutes.

---

## Step 1: Navigate to Azure SQL

1. Go to **[aka.ms/azuresqlhub](https://aka.ms/azuresqlhub)** (or search "Azure SQL" in the Azure portal)
2. You'll see four options:

| Option | Type | Use Case |
|--------|------|----------|
| Azure SQL Database Hyperscale | PaaS | Large-scale production workloads |
| Azure SQL Managed Instance | PaaS | Migrating on-prem SQL Server |
| **Azure SQL Database** | **PaaS** | **Our choice — lightweight, free tier available** |
| SQL Server on Azure VMs | IaaS | Full VM control |

3. Click **"Try for free"** under **Azure SQL Database** (bottom-left card)

---

## Step 2: Create the Database

On the "Create SQL Database" page:

| Field | Value |
|-------|-------|
| **Subscription** | Your Azure subscription |
| **Resource group** | Create new or use existing (e.g., `your_resource_group`) |
| **Database name** | `PatentIntelligence` |
| **Server** | Click "Create new" (see Step 3) |
| **Want to use SQL elastic pool?** | No |
| **Workload environment** | Development |
| **Compute + storage** | Free tier should be auto-selected for "Try for free" |

> **Note**: If asked about a data source, select "None" — we'll create the schema ourselves.

---

## Step 3: Create the SQL Server

When you click "Create new" for the server, you'll see the **Create SQL Database Server** page:

| Field | Value |
|-------|-------|
| **Server name** | Choose a unique name (e.g., `yourname`) — this becomes `yourname.database.windows.net` |
| **Location** | Pick your nearest region (e.g., "(US) East US") |

### Authentication

You'll see three authentication options:

| Option | Description |
|--------|-------------|
| Microsoft Entra-only | Uses your Microsoft account (Azure AD) — no SQL password |
| Both SQL and Microsoft Entra | Supports both — flexible |
| **SQL authentication** | **Username + password — required for this demo's CLI tools** |

**Select "Use SQL authentication"** (or "Use both SQL and Microsoft Entra authentication").

Set your SQL admin credentials:

| Field | Value |
|-------|-------|
| **Server admin login** | `sqladmin` (or your preferred username) |
| **Password** | Choose a strong password — you'll need it for `.env` |

> **Why SQL authentication?** The demo tools (`sqlcmd`, `pyodbc`) all connect using username/password. Entra-only authentication won't work with these CLI tools without additional configuration.

Click **OK** to return to the database creation page.

---

## Step 4: Review and Create

1. Click **"Review + create"**
2. Verify the settings look correct
3. Click **"Create"**

The deployment will take 1-3 minutes. You'll see a "Deployment is in progress" page showing your server resource being provisioned.

Once you see **"Your deployment is complete"**, proceed to Step 5.

---

## Step 5: Configure Firewall Rules

By default, Azure SQL blocks all external connections. You need to add your IP address.

1. Navigate to your **SQL server** resource (not the database — the server itself)
   - From the deployment page, click "Go to resource", then click the server name
   - Or search for your server name in the Azure portal search bar
2. In the left sidebar, under **Security**, click **"Networking"**
3. Under **Public network access**, ensure **"Selected networks"** is selected
4. Scroll down to **Firewall rules**
5. Click **"+ Add your client IPv4 address"** — Azure will auto-detect your current IP
6. **(Recommended)** Also toggle **"Allow Azure services and resources to access this server"** to **Yes**
7. Click **Save**

> **Important**: Firewall changes can take up to 5 minutes to take effect. If your first connection attempt fails, wait a few minutes and try again.

> **Changing networks?** If you're at a coffee shop, office, or meetup venue, your IP will be different. You'll need to add the new IP as a firewall rule each time you connect from a new network.

---

## Step 6: Add Credentials to `.env`

Copy `.env.example` to `.env` (if you haven't already) and fill in your Azure SQL credentials:

```bash
cp .env.example .env
```

Edit `.env` and update these values:

```
AZURE_SQL_SERVER=yourname.database.windows.net
AZURE_SQL_DATABASE=PatentIntelligence
AZURE_SQL_USER=sqladmin
AZURE_SQL_PASSWORD=your-password-here
```

> **Security**: The `.env` file is listed in `.gitignore` and will never be committed to the repository. Never share or commit your password.

---

## Step 7: Test the Connection

```bash
# Load environment variables and test with sqlcmd
source .env
sqlcmd -S "$AZURE_SQL_SERVER" -d "$AZURE_SQL_DATABASE" -U "$AZURE_SQL_USER" -P "$AZURE_SQL_PASSWORD" \
  -Q "SELECT DB_NAME() AS CurrentDB, SUSER_NAME() AS CurrentUser, GETDATE() AS ServerTime"
```

Expected output:

```
CurrentDB            CurrentUser          ServerTime
-------------------- -------------------- -----------------------
PatentIntelligence   sqladmin             2026-02-18 23:21:24.123
```

If you get a firewall error, double-check that your IP was added in Step 5 and wait a few minutes.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Client with IP address X is not allowed" | Add your IP in Server > Networking > Firewall rules, then wait 5 min |
| "Login failed for user" | Verify username/password in `.env` match what you set in Step 3 |
| "Cannot open server" | Check the server name in `.env` — it should end with `.database.windows.net` |
| "Connection timeout" | The free tier may be paused — run the query again to wake it up (takes ~30 seconds) |
| sqlcmd not found | Install it: `brew install microsoft/mssql-release/mssql-tools18` (macOS) |

---

## Free Tier Limits

| Resource | Limit |
|----------|-------|
| Compute | 100,000 vCore-seconds/month |
| Storage | 32 GB |
| Databases | 1 free database per subscription |
| Auto-pause | Yes — pauses after inactivity, resumes on first query (~30s wake-up) |

The free tier is more than sufficient for this demo. For details, see [Azure SQL Database free offer](https://learn.microsoft.com/en-us/azure/azure-sql/database/free-offer).
