#!/usr/bin/env bash
# IN-CORE community pulse: every query behind the page, read-only.
# Runs Flux queries inside the prod InfluxDB pod with the token the pod already holds.
# Nothing is written to the database or the pod. Output goes to stdout.
#
# Usage:  bash community_pulse_queries.sh            # main queries
#         bash community_pulse_queries.sh check      # independent cross-checks
set -euo pipefail
NS=incore
POD=influxdb-influxdb2-0

q() { # q <label> <flux>
  echo "### $1"
  kubectl -n "$NS" exec "$POD" -- sh -c \
    'INFLUX_TOKEN=$DOCKER_INFLUXDB_INIT_ADMIN_TOKEN INFLUX_HOST=http://localhost:8086 INFLUX_ORG=incore influx query --raw "$1"' _ "$2" \
    | grep -v '^#' | grep -v '^$' | cut -d, -f4-
}

# Base: one point per request = the "elapsed" field of measurement "auth".
B='from(bucket:"incore") |> range(start:-90d) |> filter(fn:(r)=>r._measurement=="auth" and r._field=="elapsed")'
P='from(bucket:"incore") |> range(start:-180d, stop:-90d) |> filter(fn:(r)=>r._measurement=="auth" and r._field=="elapsed")'
NAMED='filter(fn:(r)=> exists r.username and r.username!="")'
COMMUNITY='filter(fn:(r)=> r.group!="NCSA")'
REAL_COUNTRY='filter(fn:(r)=> exists r.country and r.country!="-" and r.country!="INVALID IP ADDRESS")'

main() {
  # summary: Signed-in users (current / previous)
  q signed_in_users_90d   "$B |> $NAMED |> keep(columns:[\"username\"]) |> group() |> distinct(column:\"username\") |> count()"
  q signed_in_users_prev  "$P |> $NAMED |> keep(columns:[\"username\"]) |> group() |> distinct(column:\"username\") |> count()"
  # summary: Community requests (current / previous)
  q community_requests_90d  "$B |> $COMMUNITY |> group() |> count()"
  q community_requests_prev "$P |> $COMMUNITY |> group() |> count()"
  # summary: Countries reached (all visitors, real countries only)
  q countries_reached "$B |> $REAL_COUNTRY |> keep(columns:[\"country\"]) |> group() |> distinct(column:\"country\") |> count()"
  # summary: Dataset views / distinct datasets
  q dataset_views    'from(bucket:"incore") |> range(start:-90d) |> filter(fn:(r)=>r._measurement=="auth" and r._field=="dataset") |> group() |> count()'
  q datasets_distinct 'from(bucket:"incore") |> range(start:-90d) |> filter(fn:(r)=>r._measurement=="auth" and r._field=="dataset") |> group() |> distinct() |> count()'
  # weekly_users (Flux 1w windows start on Thursdays)
  q weekly_users "$B |> $NAMED |> keep(columns:[\"_time\",\"username\"]) |> group() |> window(every:1w) |> distinct(column:\"username\") |> count() |> keep(columns:[\"_start\",\"_value\"])"
  # weekly_requests by group (_time is the END of each week)
  q weekly_requests "$B |> group(columns:[\"group\"]) |> aggregateWindow(every:1w, fn:count) |> keep(columns:[\"_time\",\"group\",\"_value\"]) |> group()"
  # tools: users per resource, requests per resource (community only)
  q tool_users    "$B |> $NAMED |> keep(columns:[\"resource\",\"username\"]) |> group(columns:[\"resource\"]) |> distinct(column:\"username\") |> count() |> group() |> sort(columns:[\"_value\"],desc:true)"
  q tool_requests "$B |> $COMMUNITY |> group(columns:[\"resource\"]) |> count() |> group() |> sort(columns:[\"_value\"],desc:true)"
  # countries: signed-in users per country
  q country_users "$B |> $NAMED |> filter(fn:(r)=>exists r.country) |> keep(columns:[\"country\",\"username\"]) |> group(columns:[\"country\"]) |> distinct(column:\"username\") |> count() |> group() |> sort(columns:[\"_value\"],desc:true)"
  # playbooks: opens per playbook (community only)
  q playbooks 'from(bucket:"incore") |> range(start:-90d) |> filter(fn:(r)=>r._measurement=="auth" and r._field=="playbook" and r.group!="NCSA") |> group(columns:["_value"]) |> count(column:"_field") |> group() |> sort(columns:["_field"],desc:true) |> limit(n:10)'
  # docs: top 15 /doc/ pages (community only)
  q docs 'from(bucket:"incore") |> range(start:-90d) |> filter(fn:(r)=>r._measurement=="auth" and r._field=="url" and r.resource=="doc" and r.group!="NCSA") |> group(columns:["_value"]) |> count(column:"_field") |> group() |> sort(columns:["_field"],desc:true) |> limit(n:15)'
  # First-time users: computed locally = usernames seen in the window but never before it (tag index, no data scan).
  tv() { kubectl -n "$NS" exec "$POD" -- sh -c \
    'INFLUX_TOKEN=$DOCKER_INFLUXDB_INIT_ADMIN_TOKEN INFLUX_HOST=http://localhost:8086 INFLUX_ORG=incore influx query --raw "$1"' _ \
    "import \"influxdata/influxdb/schema\" schema.tagValues(bucket:\"incore\", tag:\"username\", predicate:(r)=>r._measurement==\"auth\", start:$1, stop:$2)" \
    | grep -v '^#' | cut -d, -f4 | grep -v -e '^_value' -e '^$' | sort -u; }
  echo "### first_time_users"; comm -13 <(tv 0 -90d) <(tv -90d 'now()') | wc -l | tr -d ' '
}

check() {
  # Independent re-derivations of the same figures, by a different route.
  q x_users_by_group      "$B |> $NAMED |> keep(columns:[\"group\",\"username\"]) |> group(columns:[\"group\"]) |> distinct(column:\"username\") |> count() |> group()"
  q x_requests_by_group   "$B |> group(columns:[\"group\"]) |> count() |> group() |> keep(columns:[\"group\",\"_value\"])"
  q x_requests_daily_sum  "$B |> $COMMUNITY |> group() |> aggregateWindow(every:1d, fn:count) |> sum()"
  q x_anon_requests       "$B |> filter(fn:(r)=> not exists r.username or r.username==\"\") |> group(columns:[\"group\"]) |> count() |> group() |> keep(columns:[\"group\",\"_value\"])"
  q x_country_values_odd  "$B |> filter(fn:(r)=> not exists r.country or r.country==\"-\" or r.country==\"INVALID IP ADDRESS\") |> group() |> count()"
  q x_playbooks_all_groups 'from(bucket:"incore") |> range(start:-90d) |> filter(fn:(r)=>r._measurement=="auth" and r._field=="playbook") |> group(columns:["_value"]) |> count(column:"_field") |> group() |> sort(columns:["_field"],desc:true) |> limit(n:3)'
  q x_docs_resource_total "$B |> $COMMUNITY |> filter(fn:(r)=>r.resource==\"doc\") |> count() |> group() |> sum()"
}

case "${1:-main}" in
  main) main ;;
  check) check ;;
  *) echo "usage: $0 [main|check]"; exit 1 ;;
esac
