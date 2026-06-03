#!/usr/bin/env python3

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
import logging
import sys

WINDOW_DAYS = 90 # 90 days

@dataclass
class Service:
    id: int
    slug: str
    name: str


def parse_iso(ts: str | None) -> datetime:
    if ts is None:
        return datetime.now(timezone.utc)

    # JSON timestamps end with "Z"; datetime.fromisoformat handles "+00:00".
    return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))

def collect_services(incidents: dict) -> dict[int, Service]:
    services : dict[int, Service] = dict()
    
    for incident in incidents['items']:
        for service in incident['services']:
            service_id = service['id']
            if service_id not in services:
                services[service_id] = Service(
                    id=service_id,
                    slug=service['slug'],
                    name=service['name']
                )
    
    return services

class RawDay:
    def __init__(self, date: int):
        self.date = date
        self.incidents: list = []
        self.services: set[int] = set()

    def attach_incident(self, incident: dict):
        self.incidents.append(incident)
        for service in incident['services']:
            self.services.add(service['id'])

    def build_response_item(self, service_id=None) -> dict:
        incidents = self.incidents
        if service_id is not None:
            incidents = [i for i in self.incidents if service_id in [s['id'] for s in i['services']]]

        status = "operational"
        if len([i for i in incidents if i['maxLevel']['level'] == 2]) > 0:
            status = "outage"
        elif len([i for i in incidents if i['maxLevel']['level'] == 1]) > 0:
            status = "degraded"
        return {
            "date": self.date,
            "status" : status,
            "incidents": [
                {
                    "id": i['id'],
                    "title": i['title'],
                    "status": i['status'],
                    "level": "major" if i['maxLevel']['level'] == 2 else "minor"
                }
                for i in incidents
            ]
        }

def build_raw_days(incidents: dict, window_days: int) -> list[RawDay]:
    start_dates = [parse_iso(incident['startDate']) for incident in incidents['items']]
    end_dates = [parse_iso(incident['endDate']) for incident in incidents['items']]
    
    min_date = min(start_dates)
    max_date = max(end_dates)

    min_date = max(min_date, max_date - timedelta(days=window_days-1))
    date_range = list(min_date + timedelta(days=i) for i in range((max_date - min_date).days + 1))

    # Build raw list of days.
    raw_days : list[RawDay] = []
    raw_days_dict : dict[int, RawDay] = dict()
    for date in date_range:
        date_slug = date.year * 10000 + date.month * 100 + date.day
        raw_day = RawDay(date_slug)
        raw_days.append(raw_day)
        raw_days_dict[date_slug] = raw_day

    # Scan incidents and fill raw days.
    for incident in incidents['items']:
        start_date = parse_iso(incident['startDate'])
        end_date = parse_iso(incident['endDate'])
        date_range = (start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1))
        
        for date in date_range:
            date_slug = date.year * 10000 + date.month * 100 + date.day
            raw_day = raw_days_dict.get(date_slug)
            if raw_day is not None:
                raw_day.attach_incident(incident)

    return raw_days

def calculate_uptime(raw_days, service_id=None):
    total_seconds = 0.0
    downtime_seconds = 0.0

    for raw_day in raw_days:
        day_start = datetime.strptime(str(raw_day.date), "%Y%m%d").replace(tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)
        total_seconds += (day_end - day_start).total_seconds()

        intervals = []
        for incident in raw_day.incidents:
            if service_id is not None and service_id not in [service['id'] for service in incident['services']]:
                continue

            incident_start = max(parse_iso(incident['startDate']), day_start)
            incident_end = min(parse_iso(incident['endDate']), day_end)
            if incident_end > incident_start:
                intervals.append((incident_start, incident_end))

        if not intervals:
            continue

        intervals.sort(key=lambda interval: interval[0])
        merged_start, merged_end = intervals[0]
        for interval_start, interval_end in intervals[1:]:
            if interval_start <= merged_end:
                merged_end = max(merged_end, interval_end)
                continue

            downtime_seconds += (merged_end - merged_start).total_seconds()
            merged_start, merged_end = interval_start, interval_end

        downtime_seconds += (merged_end - merged_start).total_seconds()

    if total_seconds == 0:
        return 100.0

    uptime = (1 - (downtime_seconds / total_seconds)) * 100
    return max(0.0, uptime)

def build_response_chunk(raw_days, service_id=None, services_lookup=None):
    days = [d.build_response_item(service_id=service_id) for d in raw_days]
    uptime = calculate_uptime(raw_days, service_id=service_id)
    result = {
        "uptime": uptime,
        "days": days,
    }
    if service_id is not None and services_lookup is not None:
        service = services_lookup.get(service_id)
        if service is not None:
            result['service'] = {
                "id": service.id,
                "slug": service.slug,
                "name": service.name,
            }

    return result

def preprocess(incidents: dict):
    services_lookup = collect_services(incidents)
    services = services_lookup.values()
    services = sorted(services, key=lambda s: s.slug)
    logging.info(f"Collected {len(services)} unique services from incidents data")

    raw_days = build_raw_days(incidents, WINDOW_DAYS)
    logging.info(f"Built raw days for a window of {len(raw_days)} days (expected {WINDOW_DAYS} days)")

    uniq_incidents : set[int] = set()
    for day in raw_days:
        for incident in day.incidents:
            uniq_incidents.add(incident['id'])
    logging.info(f"Collected {len(uniq_incidents)} unique incidents for a window of {WINDOW_DAYS} days")

    global_response = build_response_chunk(raw_days)
    per_service_responses = [build_response_chunk(raw_days, service_id=s.id, services_lookup=services_lookup) for s in services]

    return {
        "window": WINDOW_DAYS,
        "last_updated": datetime.now().isoformat(),
        "total_incidents": len(uniq_incidents),
        "global": global_response,
        "services": per_service_responses,
    }

def preprocess_incidents(input_file: str, output_file: str) -> None:
    with open(input_file, "r") as f:
        input_json = f.read()
    input_data = json.loads(input_json)
    output_data = preprocess(input_data)
    output_json = json.dumps(output_data, indent=2)

    with open(output_file, "w") as f:
        f.write(output_json)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.stderr.write("Usage: preprocess.py <input_file> <output_file>\n")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    preprocess_incidents(input_file, output_file)
