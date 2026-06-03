import unittest

from scripts.preprocess import build_raw_days, build_response_chunk


class PreprocessUptimeTests(unittest.TestCase):
    def test_global_uptime_uses_partial_day_duration(self):
        incidents = {
            "items": [
                {
                    "id": 1,
                    "title": "Thirty minute incident",
                    "status": "resolved",
                    "startDate": "2026-06-01T12:00:00Z",
                    "endDate": "2026-06-01T12:30:00Z",
                    "maxLevel": {"level": 1},
                    "services": [{"id": 10, "slug": "compute", "name": "Compute"}],
                }
            ]
        }

        raw_days = build_raw_days(incidents, window_days=1)
        response = build_response_chunk(raw_days)

        self.assertAlmostEqual(response["uptime"], ((24 * 60 - 30) / (24 * 60)) * 100)

    def test_overlapping_incidents_do_not_double_count_downtime(self):
        incidents = {
            "items": [
                {
                    "id": 1,
                    "title": "First",
                    "status": "resolved",
                    "startDate": "2026-06-01T12:00:00Z",
                    "endDate": "2026-06-01T13:00:00Z",
                    "maxLevel": {"level": 2},
                    "services": [{"id": 10, "slug": "compute", "name": "Compute"}],
                },
                {
                    "id": 2,
                    "title": "Second",
                    "status": "resolved",
                    "startDate": "2026-06-01T12:30:00Z",
                    "endDate": "2026-06-01T14:00:00Z",
                    "maxLevel": {"level": 1},
                    "services": [{"id": 10, "slug": "compute", "name": "Compute"}],
                },
            ]
        }

        raw_days = build_raw_days(incidents, window_days=1)
        response = build_response_chunk(raw_days)

        self.assertAlmostEqual(response["uptime"], ((24 - 2) / 24) * 100)

    def test_service_uptime_only_counts_matching_service_incidents(self):
        incidents = {
            "items": [
                {
                    "id": 1,
                    "title": "Compute incident",
                    "status": "resolved",
                    "startDate": "2026-06-01T00:00:00Z",
                    "endDate": "2026-06-01T01:00:00Z",
                    "maxLevel": {"level": 2},
                    "services": [{"id": 10, "slug": "compute", "name": "Compute"}],
                },
                {
                    "id": 2,
                    "title": "Storage incident",
                    "status": "resolved",
                    "startDate": "2026-06-01T02:00:00Z",
                    "endDate": "2026-06-01T04:00:00Z",
                    "maxLevel": {"level": 2},
                    "services": [{"id": 20, "slug": "storage", "name": "Storage"}],
                },
            ]
        }

        raw_days = build_raw_days(incidents, window_days=1)
        response = build_response_chunk(raw_days, service_id=10)

        self.assertAlmostEqual(response["uptime"], ((24 - 1) / 24) * 100)


if __name__ == "__main__":
    unittest.main()
