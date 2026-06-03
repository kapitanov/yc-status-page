import unittest

from scripts.render import render


class RenderTests(unittest.TestCase):
    def test_render_builds_status_page_html(self):
        model = {
            "window": 3,
            "last_updated": "2026-06-03T10:30:00+00:00",
            "total_incidents": 3,
            "global": {
                "uptime": 98.5,
                "days": [
                    {"date": 20260601, "status": "operational", "incidents": []},
                    {
                        "date": 20260602,
                        "status": "degraded",
                        "incidents": [
                            {
                                "id": 1,
                                "title": "API latency <check>",
                                "status": "resolved",
                                "level": "minor",
                            }
                        ],
                    },
                    {
                        "date": 20260603,
                        "status": "outage",
                        "incidents": [
                            {
                                "id": 2,
                                "title": "Storage outage",
                                "status": "investigating",
                                "level": "major",
                            }
                        ],
                    },
                ],
            },
            "services": [
                {
                    "uptime": 99.9,
                    "service": {"id": 10, "slug": "compute", "name": "Compute Cloud"},
                    "days": [
                        {"date": 20260601, "status": "operational", "incidents": []},
                        {"date": 20260602, "status": "operational", "incidents": []},
                        {
                            "date": 20260603,
                            "status": "degraded",
                            "incidents": [
                                {
                                    "id": 3,
                                    "title": "Host maintenance",
                                    "status": "resolved",
                                    "level": "minor",
                                }
                            ],
                        },
                    ],
                }
            ],
        }

        html = render(model)

        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("<title>The Unofficial Yandex Cloud Status Page</title>", html)
        self.assertIn("The Unofficial Yandex Cloud Status Page", html)
        self.assertIn("98.50% uptime", html)
        self.assertIn("Last 3 days uptime", html)
        self.assertIn("Last updated Jun 03, 2026", html)
        self.assertIn("3 incidents in last 3 days", html)
        self.assertIn("Service uptime", html)
        self.assertIn("Compute Cloud", html)
        self.assertIn("bg-red-500", html)
        self.assertIn("bg-yellow-500", html)


if __name__ == "__main__":
    unittest.main()
