# Frost Dates Feature: Implementation Proposal

**Author:** Claude (Principal SW Architect)
**Date:** January 2026
**Status:** Draft - Awaiting Review
**Branch:** `feature/frost-dates`

---

## Executive Summary

This proposal outlines a feature to track and compare frost dates using the user's own weather station data against NOAA Climate Normals. The goal is to help gardeners understand their microclimate and make informed planting decisions.

**Key Principles:**
- User's observed data remains pristine (no gap-filling from external sources)
- External data (NOAA) is clearly delineated and used only for comparison
- Configurable temperature thresholds for different crop sensitivities
- **Fahrenheit and Celsius support** from day one (display in user's preferred unit)
- Open-source friendly (works for any Ambient Weather user worldwide)

---

## Table of Contents

1. [Temperature Unit Support](#temperature-unit-support)
2. [NOAA Climate Normals Data Access](#noaa-climate-normals-data-access)
3. [Proposed Architecture](#proposed-architecture)
4. [Database Schema Changes](#database-schema-changes)
5. [API Endpoints](#api-endpoints)
6. [UI Components](#ui-components)
7. [Data Flow Summary](#data-flow-summary)
8. [Implementation Phases](#implementation-phases)
9. [Open Questions](#open-questions)
10. [Sources](#sources)

---

## Temperature Unit Support

> **Note:** The current app is Fahrenheit-only throughout. This feature will be the first to support both units, establishing patterns that can later be applied app-wide.

### Design Approach

| Aspect | Approach |
|--------|----------|
| **Storage** | Fahrenheit (canonical) - matches Ambient Weather API and NOAA data |
| **Conversion** | At API response time and UI display time |
| **User Preference** | Stored in `frost_settings` table, respected by all frost endpoints |
| **Default** | Fahrenheit (matches current app behavior) |

### Standard Frost Thresholds (F and C)

| Fahrenheit | Celsius | Condition | Agricultural Impact |
|------------|---------|-----------|---------------------|
| 36°F | 2°C | Light frost | Tender annuals damaged (basil, tomatoes, peppers) |
| **32°F** | **0°C** | Freeze | Most plants affected (standard threshold) |
| 28°F | -2°C | Hard freeze | Cold-hardy plants damaged |
| 24°F | -4°C | Severe freeze | Even hardy perennials at risk |
| 20°F | -7°C | Deep freeze | Root damage possible |
| 16°F | -9°C | Extreme freeze | Severe damage to most perennials |

### Conversion Formulas

```python
def fahrenheit_to_celsius(f: float) -> float:
    """Convert Fahrenheit to Celsius, rounded to 1 decimal."""
    return round((f - 32) * 5 / 9, 1)

def celsius_to_fahrenheit(c: float) -> float:
    """Convert Celsius to Fahrenheit, rounded to 1 decimal."""
    return round(c * 9 / 5 + 32, 1)

# Standard threshold mappings (pre-computed for consistency)
THRESHOLD_MAP = {
    # Fahrenheit: Celsius
    36: 2,
    32: 0,
    28: -2,
    24: -4,
    20: -7,
    16: -9,
}
```

### API Unit Parameter

All frost endpoints accept an optional `unit` parameter:

```
GET /api/frost/actual?unit=celsius
GET /api/frost/comparison?unit=fahrenheit  (default)
```

Response includes the unit used:

```json
{
  "unit": "celsius",
  "events": [
    {
      "year": 2025,
      "threshold": 0,
      "threshold_unit": "celsius",
      "min_temp": -1.2,
      ...
    }
  ]
}
```

### UI Unit Selector

The frost feature will include a unit toggle (°F / °C) that:
- Persists to user settings
- Applies to all frost-related displays
- Shows thresholds in the selected unit
- Could later be promoted to an app-wide setting

---

## NOAA Climate Normals Data Access

### API Details

| Property | Value |
|----------|-------|
| **Endpoint** | `https://www.ncei.noaa.gov/cdo-web/api/v2/` |
| **Authentication** | Free API token required ([Request here](https://www.ncdc.noaa.gov/cdo-web/token)) |
| **Rate Limits** | 5 requests/second, 10,000 requests/day |
| **Key Dataset** | `NORMAL_ANN` (Annual Normals including Agricultural Normals) |

### Finding Nearest Station

```bash
# Find stations within a bounding box near lat/lon
GET /stations?datasetid=NORMAL_ANN&extent={lat-0.5},{lon-0.5},{lat+0.5},{lon+0.5}
```

### Frost/Freeze Data Types Available

| Data Type Pattern | Description | Example |
|-------------------|-------------|---------|
| `ANN-TMIN-PRBLST-T{temp}FP{prob}` | Last spring occurrence probability | `ANN-TMIN-PRBLST-T32FP50` = 50% prob of last 32°F |
| `ANN-TMIN-PRBFST-T{temp}FP{prob}` | First fall occurrence probability | `ANN-TMIN-PRBFST-T32FP50` = 50% prob of first 32°F |
| `ANN-TMIN-PRBGSL-T{temp}FP{prob}` | Growing season length (days) | `ANN-TMIN-PRBGSL-T32FP50` |

**Temperature thresholds available:** 16°F, 20°F, 24°F, 28°F, 32°F, 36°F (in 4°F increments)

**Probability levels available:** 10%, 20%, 30%, 40%, 50%, 60%, 70%, 80%, 90%

### Probability Interpretation

From [NC State Extension](https://content.ces.ncsu.edu/interpreting-freezefrost-probabilities-from-the-national-centers-for-environmental-information):

| Probability | Spring Frost | Fall Frost | Risk Level | Use Case |
|-------------|--------------|------------|------------|----------|
| 10% | Latest possible | Earliest possible | Conservative | Tender transplants |
| 50% | Median date | Median date | Moderate | General planning |
| 90% | Earliest possible | Latest possible | Aggressive | Cold-hardy crops |

### Temperature Thresholds Explained

> See [Temperature Unit Support](#temperature-unit-support) for full F/C threshold table.

| Threshold (F) | Threshold (C) | Condition | NOAA Data Type Suffix |
|---------------|---------------|-----------|----------------------|
| 36°F | 2°C | Light frost | `T36F` |
| **32°F** | **0°C** | Freeze | `T32F` |
| 28°F | -2°C | Hard freeze | `T28F` |
| 24°F | -4°C | Severe freeze | `T24F` |

**Note:** NOAA data uses Fahrenheit internally (e.g., `ANN-TMIN-PRBLST-T32FP50`). Conversion to Celsius happens at display time.

---

## Proposed Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FROST DATES FEATURE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        DATA SOURCES                                  │   │
│  │                                                                      │   │
│  │  YOUR STATION (Primary)          NOAA NORMALS (Reference)           │   │
│  │  ┌─────────────────────┐         ┌─────────────────────┐            │   │
│  │  │ Ambient Weather API │         │ CDO API v2          │            │   │
│  │  │ • 5-min intervals   │         │ • 30-year averages  │            │   │
│  │  │ • Your actual temps │         │ • Probability dates │            │   │
│  │  │ • Microclimate data │         │ • Regional baseline │            │   │
│  │  └──────────┬──────────┘         └──────────┬──────────┘            │   │
│  │             │                               │                        │   │
│  └─────────────┼───────────────────────────────┼────────────────────────┘   │
│                │                               │                            │
│                ▼                               ▼                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        DATABASE LAYER                                │   │
│  │                                                                      │   │
│  │  weather_data (existing)    frost_events (new)    noaa_normals (new)│   │
│  │  ┌─────────────────┐       ┌─────────────────┐   ┌─────────────────┐│   │
│  │  │ dateutc         │       │ id              │   │ station_id      ││   │
│  │  │ tempf           │       │ event_date      │   │ threshold_f     ││   │
│  │  │ ...             │       │ event_type      │   │ probability     ││   │
│  │  │                 │       │ threshold_f     │   │ spring_date     ││   │
│  │  │                 │       │ min_temp_f      │   │ fall_date       ││   │
│  │  │                 │       │ year            │   │ season_length   ││   │
│  │  │                 │       │ source          │   │ fetched_at      ││   │
│  │  └─────────────────┘       └─────────────────┘   └─────────────────┘│   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│                ▼                               ▼                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        API LAYER (FastAPI)                           │   │
│  │                                                                      │   │
│  │  /api/frost/actual                 /api/frost/normals               │   │
│  │  • Get actual frost events         • Get NOAA probability dates     │   │
│  │  • Filter by year, threshold       • Station lookup by lat/lon      │   │
│  │                                                                      │   │
│  │  /api/frost/comparison             /api/frost/settings              │   │
│  │  • Side-by-side actual vs normal   • User threshold preferences     │   │
│  │  • Microclimate deviation calc     • NOAA station selection         │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│                ▼                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        UI COMPONENTS (React)                         │   │
│  │                                                                      │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │              FROST DATES DASHBOARD CARD                      │    │   │
│  │  │  ┌──────────────────┐  ┌──────────────────┐                 │    │   │
│  │  │  │ YOUR DATA        │  │ NOAA NORMAL      │                 │    │   │
│  │  │  │ Last Spring: 4/2 │  │ 50%: 4/15        │  ← You're 13    │    │   │
│  │  │  │ First Fall: 10/28│  │ 50%: 10/12       │    days ahead!  │    │   │
│  │  │  │ Season: 209 days │  │ 50%: 180 days    │                 │    │   │
│  │  │  └──────────────────┘  └──────────────────┘                 │    │   │
│  │  │                                     [°F] [°C] ← Unit Toggle │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  │                                                                      │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │              THRESHOLD SELECTOR (showing °F, or °C if set)   │    │   │
│  │  │  [ ] 36°F / 2°C  (Light frost - tender annuals)             │    │   │
│  │  │  [✓] 32°F / 0°C  (Freeze - most plants)    ← Default        │    │   │
│  │  │  [ ] 28°F / -2°C (Hard freeze - cold-hardy)                 │    │   │
│  │  │  [ ] 24°F / -4°C (Severe freeze)                            │    │   │
│  │  │  [ ] Custom: [____]                                         │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  │                                                                      │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │              FROST HISTORY CHART                             │    │   │
│  │  │                                                              │    │   │
│  │  │  Year  │ Last Spring │ First Fall │ Season │ vs Normal      │    │   │
│  │  │  ──────┼─────────────┼────────────┼────────┼────────────    │    │   │
│  │  │  2025  │ Apr 2       │ Oct 28     │ 209d   │ +29 days       │    │   │
│  │  │  2024  │ Apr 15      │ Oct 10     │ 178d   │ -2 days        │    │   │
│  │  │  2023  │ Mar 28      │ Nov 1      │ 218d   │ +38 days       │    │   │
│  │  │                                                              │    │   │
│  │  │  ══════════════════════════════════════════════════════     │    │   │
│  │  │  NOAA   │ Apr 15     │ Oct 12     │ 180d   │ (baseline)     │    │   │
│  │  │  Normal │ (50% prob) │ (50% prob) │        │                │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Database Schema Changes

### New Tables

```sql
-- Track actual frost events detected from your weather data
CREATE TABLE frost_events (
    id INTEGER PRIMARY KEY,
    event_date DATE NOT NULL,
    event_type VARCHAR(20) NOT NULL,  -- 'last_spring' | 'first_fall'
    threshold_f DOUBLE NOT NULL,       -- 36, 32, 28, 24, etc.
    min_temp_f DOUBLE NOT NULL,        -- Actual minimum temperature that day
    year INTEGER NOT NULL,
    source VARCHAR(20) DEFAULT 'observed',  -- Always 'observed' (never filled)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, event_type, threshold_f)
);

-- Cache NOAA normals data for reference station
CREATE TABLE noaa_normals (
    id INTEGER PRIMARY KEY,
    noaa_station_id VARCHAR(20) NOT NULL,
    station_name VARCHAR(100),
    latitude DOUBLE,
    longitude DOUBLE,
    threshold_f DOUBLE NOT NULL,       -- 36, 32, 28, 24, 20, 16
    probability INTEGER NOT NULL,      -- 10, 20, 30, 40, 50, 60, 70, 80, 90
    spring_date VARCHAR(10),           -- 'MM-DD' format
    fall_date VARCHAR(10),             -- 'MM-DD' format
    season_length_days INTEGER,
    normals_period VARCHAR(20),        -- '1991-2020'
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(noaa_station_id, threshold_f, probability)
);

-- User preferences for frost tracking
CREATE TABLE frost_settings (
    id INTEGER PRIMARY KEY,
    noaa_station_id VARCHAR(20),       -- Selected reference station
    temperature_unit VARCHAR(10) DEFAULT 'fahrenheit',  -- 'fahrenheit' | 'celsius'
    default_threshold_f DOUBLE DEFAULT 32,  -- Always stored in F (canonical)
    enabled_thresholds_f JSON,         -- [36, 32, 28] array (always in F)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Note: Thresholds are stored in Fahrenheit as the canonical unit.
-- Conversion to Celsius happens at API/UI layer based on temperature_unit preference.
```

### New View

```sql
-- Computed view: Daily temperature summary from raw data
CREATE VIEW daily_temp_summary AS
SELECT
    DATE(dateutc) as date,
    MIN(tempf) as min_temp_f,
    MAX(tempf) as max_temp_f,
    AVG(tempf) as avg_temp_f,
    COUNT(*) as reading_count
FROM weather_data
WHERE tempf IS NOT NULL
GROUP BY DATE(dateutc);
```

---

## API Endpoints

### Frost Analysis Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/frost/actual` | Get actual frost events from your data |
| `GET` | `/api/frost/normals` | Get NOAA normal dates for reference station |
| `GET` | `/api/frost/stations` | Find nearby NOAA stations |
| `GET` | `/api/frost/comparison` | Side-by-side actual vs normal comparison |
| `GET` | `/api/frost/settings` | Get user frost preferences |
| `PUT` | `/api/frost/settings` | Update user frost preferences |
| `POST` | `/api/frost/recalculate` | Trigger recalculation from raw data |

### Endpoint Details

#### GET /api/frost/actual

**Query Parameters:**
- `year` (optional): Filter by year
- `threshold` (optional, default: 32°F / 0°C): Temperature threshold (in requested unit)
- `unit` (optional, default: from settings or 'fahrenheit'): `fahrenheit` | `celsius`

**Response:**
```json
{
  "unit": "fahrenheit",
  "events": [
    {
      "year": 2025,
      "last_spring": "2025-04-02",
      "first_fall": "2025-10-28",
      "season_days": 209,
      "threshold": 32,
      "min_temp_spring": 31.2,
      "min_temp_fall": 30.8,
      "source": "observed"
    }
  ]
}
```

**Celsius Example:**
```json
{
  "unit": "celsius",
  "events": [
    {
      "year": 2025,
      "last_spring": "2025-04-02",
      "first_fall": "2025-10-28",
      "season_days": 209,
      "threshold": 0,
      "min_temp_spring": -0.4,
      "min_temp_fall": -0.7,
      "source": "observed"
    }
  ]
}
```

#### GET /api/frost/normals

**Query Parameters:**
- `station_id`: NOAA station ID (or use lat/lon for lookup)
- `lat`, `lon`: Coordinates for station lookup
- `threshold` (optional): Filter by threshold (in requested unit)
- `probability` (optional): Filter by probability level
- `unit` (optional, default: from settings or 'fahrenheit'): `fahrenheit` | `celsius`

**Response:**
```json
{
  "unit": "fahrenheit",
  "station": {
    "id": "USW00013722",
    "name": "RALEIGH-DURHAM INTL AP",
    "latitude": 35.8944,
    "longitude": -78.7819
  },
  "normals": [
    {
      "threshold": 32,
      "probability": 50,
      "spring_date": "04-15",
      "fall_date": "10-12",
      "season_days": 180,
      "period": "1991-2020"
    }
  ]
}
```

**Celsius Example:**
```json
{
  "unit": "celsius",
  "station": { ... },
  "normals": [
    {
      "threshold": 0,
      "probability": 50,
      "spring_date": "04-15",
      "fall_date": "10-12",
      "season_days": 180,
      "period": "1991-2020"
    }
  ]
}
```

#### GET /api/frost/stations

**Query Parameters:**
- `lat`, `lon`: Center coordinates
- `radius_miles` (optional, default: 50): Search radius

**Response:**
```json
{
  "stations": [
    {
      "id": "USW00013722",
      "name": "RALEIGH-DURHAM INTL AP",
      "distance_miles": 12.3,
      "latitude": 35.8944,
      "longitude": -78.7819
    }
  ]
}
```

#### GET /api/frost/comparison

**Query Parameters:**
- `year` (optional): Specific year or current
- `threshold` (optional, default: 32°F / 0°C): Temperature threshold
- `unit` (optional, default: from settings or 'fahrenheit'): `fahrenheit` | `celsius`

**Response:**
```json
{
  "unit": "fahrenheit",
  "threshold": 32,
  "actual": {
    "year": 2025,
    "last_spring": "2025-04-02",
    "first_fall": "2025-10-28",
    "season_days": 209,
    "min_temp_spring": 31.2,
    "min_temp_fall": 30.8
  },
  "normal": {
    "station_name": "RALEIGH-DURHAM INTL AP",
    "probability": 50,
    "spring_date": "04-15",
    "fall_date": "10-12",
    "season_days": 180
  },
  "deviation": {
    "spring_days": -13,
    "fall_days": 16,
    "season_days": 29
  },
  "interpretation": "Your microclimate has a 29-day longer growing season than the regional average."
}
```

**Celsius Example:**
```json
{
  "unit": "celsius",
  "threshold": 0,
  "actual": {
    "year": 2025,
    "last_spring": "2025-04-02",
    "min_temp_spring": -0.4,
    ...
  },
  ...
}
```

---

## UI Components

### 1. Frost Dashboard Card (Main Display)

**Purpose:** At-a-glance comparison of your frost dates vs NOAA normals

**Features:**
- Current year's frost dates (yours vs NOAA)
- Visual indicator of microclimate advantage/disadvantage
- Quick threshold selector chips (displayed in user's preferred unit)
- **Unit toggle** (°F / °C) - persists to settings

**Accessibility:**
- Screen reader announces comparison values with units (e.g., "32 degrees Fahrenheit")
- Keyboard navigation between threshold options
- High contrast colors for deviation indicators

### 2. NOAA Station Selector

**Purpose:** Allow users to select their reference NOAA station

**Features:**
- Search by location (city, zip, or coordinates)
- List nearby stations with distance
- Show station metadata (name, coordinates, data availability)
- Store selection in settings

### 3. Frost History Table

**Purpose:** Multi-year historical comparison

**Features:**
- Sortable columns (year, dates, season length, deviation)
- Clear visual distinction between observed data and NOAA baseline
- Export to CSV option

### 4. Threshold Configuration Panel

**Purpose:** Customize which temperature thresholds to track

**Features:**
- Checkbox list with descriptions of agricultural impact
- Custom threshold input for specific crops (accepts F or C based on unit setting)
- Persistence to user settings
- Displays all values in user's preferred unit

**Default Thresholds (shown in both units for reference):**

| Enabled | Fahrenheit | Celsius | Description |
|---------|------------|---------|-------------|
| ☐ | 36°F | 2°C | Light frost (tender annuals) |
| ☑ | **32°F** | **0°C** | Freeze (most plants) - Default |
| ☐ | 28°F | -2°C | Hard freeze (cold-hardy plants) |
| ☐ | 24°F | -4°C | Severe freeze |

### 5. Growing Season Countdown (Enhancement)

**Purpose:** Real-time awareness of frost risk

**Features:**
- Days since last spring frost
- Estimated days until first fall frost (based on NOAA probability)
- Visual "frost risk" indicator as fall approaches

---

## Data Flow Summary

### Principle: Data Source Integrity

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA FLOW & SOURCES                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  YOUR OBSERVED DATA (Sacred - Never Modified)                        │   │
│  │  ════════════════════════════════════════════                        │   │
│  │  Source: Ambient Weather API → weather_data table                    │   │
│  │  Processing: SQL aggregation to find daily min temps                 │   │
│  │  Output: frost_events table (source='observed')                      │   │
│  │  Gaps: Preserved as gaps (NOT filled by external data)               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  NOAA REFERENCE DATA (Clearly Labeled External Source)              │   │
│  │  ═══════════════════════════════════════════════════                │   │
│  │  Source: NOAA CDO API v2 → noaa_normals table                       │   │
│  │  Purpose: Regional baseline for comparison only                     │   │
│  │  Refresh: On-demand or annual (normals don't change often)          │   │
│  │  Display: Always marked as "NOAA Normal (50% probability)"          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  UI PRESENTATION                                                     │   │
│  │  ════════════════                                                    │   │
│  │  • Two distinct columns: "Your Station" | "NOAA Reference"          │   │
│  │  • Different visual styling (your data prominent, NOAA muted)       │   │
│  │  • Deviation shown as comparison metric, not merged data            │   │
│  │  • Tooltips explain data sources when hovering                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

| Phase | Scope | Deliverables | Dependencies |
|-------|-------|--------------|--------------|
| **1. Core Analysis** | Frost detection from existing data | `daily_temp_summary` view, `frost_events` table, detection queries | None |
| **2. Unit Support** | F/C conversion infrastructure | Conversion utilities, unit parameter on endpoints, settings table with `temperature_unit` | Phase 1 |
| **3. NOAA Integration** | External API integration | NOAA client, `noaa_normals` table, station finder | NOAA API token |
| **4. Backend API** | FastAPI endpoints | All `/api/frost/*` endpoints with unit support | Phases 1-3 |
| **5. Comparison UI** | Main dashboard components | Frost card, history table, deviation display, unit toggle | Phase 4 |
| **6. Settings** | User configuration | Threshold selector, station picker, unit preference persistence | Phase 5 |
| **7. Enhancements** | Additional features | Growing season countdown, multi-year trends | Phase 6 |

---

## Open Questions

### 1. NOAA API Token Management

**Question:** Should the NOAA API token be:
- **Option A:** User-provided (each user registers for their own free token)
- **Option B:** App-provided (single token for all users, with rate limit considerations)

**Recommendation:** Option A for open-source flexibility, with clear setup documentation.

### 2. Default Thresholds

**Question:** Which thresholds should be enabled by default?
- **Option A:** 32°F only (simplest)
- **Option B:** 36°F, 32°F, 28°F (common agricultural set)

**Recommendation:** Option B with 32°F as the primary display threshold.

### 3. Historical Calculation Trigger

**Question:** When should frost events be calculated from existing data?
- **Option A:** Automatically on app startup / data sync
- **Option B:** On-demand via user action or API call
- **Option C:** Scheduled (e.g., daily at midnight)

**Recommendation:** Option C with Option B as manual override.

### 4. UI Placement

**Question:** Where should the frost dates feature live?
- **Option A:** New dedicated page (`/frost` or `/growing-season`)
- **Option B:** Card/section on existing dashboard
- **Option C:** Both (summary card on dashboard, detail page)

**Recommendation:** Option C for progressive disclosure.

### 5. App-Wide Unit Support (Future)

**Question:** Should the temperature unit preference be:
- **Option A:** Frost-feature only (isolated to this feature)
- **Option B:** App-wide setting (frost feature introduces it, other features adopt it later)

**Recommendation:** Option B - Design the setting to be promotable to app-wide. Store in a way that other features can read it. The frost feature will be the first to use it, establishing the pattern.

**Implementation note:** The `frost_settings.temperature_unit` field could later be migrated to a general `user_settings` table when app-wide unit support is implemented.

---

## Sources

- [NOAA CDO Web Services API v2](https://www.ncdc.noaa.gov/cdo-web/webservices/v2) - Official API documentation
- [U.S. Climate Normals (NCEI)](https://www.ncei.noaa.gov/products/land-based-station/us-climate-normals) - Climate normals product page
- [Interpreting Freeze/Frost Probabilities - NC State Extension](https://content.ces.ncsu.edu/interpreting-freezefrost-probabilities-from-the-national-centers-for-environmental-information) - Agricultural interpretation guide
- [NCEI API Guide (GitHub)](https://github.com/partytax/ncei-api-guide) - Community API guide
- [Open-Meteo Historical API](https://open-meteo.com/en/docs/historical-weather-api) - Alternative historical data source
- [NOAA Climate Normals Quick Access](https://www.ncei.noaa.gov/access/us-climate-normals/) - Interactive station finder

---

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2026-01-27 | Claude | Initial draft |
| 2026-01-27 | Claude | Added Fahrenheit/Celsius dual-unit support throughout |
