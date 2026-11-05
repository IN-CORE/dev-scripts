# telemetry

Community usage telemetry for IN-CORE, read from the production InfluxDB (`influxdb-influxdb2-0`, namespace `incore`, bucket `incore`, measurement `auth`).

## Files

- `community_pulse_queries.sh`: every Flux query behind the Community Pulse page. Read-only: it runs `influx query` inside the InfluxDB pod with the token the pod already holds, and writes nothing to the database or the pod.
- `community_pulse.html`: a standalone snapshot of the Community Pulse page for the 90 days Aug 7 – Nov 5, 2026. The aggregated data is embedded in the file; open it in a browser.

## Usage

Needs `kubectl` access to the `incore-prod` cluster.

```bash
bash community_pulse_queries.sh          # the page's queries
bash community_pulse_queries.sh check    # independent cross-checks of the same figures
```

## Definitions

- **Signed-in users**: distinct non-empty `username` tags. Anonymous requests count toward requests and countries only.
- **Community requests**: all requests except the `NCSA` group (three staff accounts, mostly automated traffic).
- **First-time users**: usernames seen in the window but never before it (from the tag index).
- **Countries**: from IP location. Most requests carry no location; `-` and `INVALID IP ADDRESS` are excluded.
- **Weeks**: Flux `1w` windows, which start on Thursdays.

The JupyterHub gauges (`jupyterhub_*` measurements) stopped reporting on Jan 16, 2025, so they are not used.
