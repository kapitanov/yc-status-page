#!/usr/bin/env python3

from datetime import datetime
from html import escape
import json
import sys


def format_date(date_slug):
    return datetime.strptime(str(date_slug), "%Y%m%d").strftime("%b %d, %Y")

def format_uptime(value):
    return f"{value:.2f}% uptime"

def render_timeline_day(day, large=False):
    class_name = "bg-green-500"
    if day['status'] == "degraded":
        class_name = "bg-yellow-500"
    elif day['status'] == "outage":
        class_name = "bg-red-500"
    height = "h-8" if large else "h-4"
    title = f"{format_date(day['date'])}: {day['status'].title()}"
    return f"""
        <div class="w-1/90 {height}" title="{escape(title)}">
            <div class="{class_name} h-full md:rounded-lg md:mx-[1px] md:mx-[2px]">
            </div>
        </div>
    """

def render_timeline_hints():
    return f"""
    <div class="text-xs sm:text-sm text-slate-500 mt-2">
        <div class="w-2 h-2 rounded-full bg-green-500 inline-block mr-1"></div>
        <span class=" mr-4">Operational</span>
        <div class="w-2 h-2 rounded-full bg-yellow-500 inline-block mr-1"></div>
        <span class=" mr-4">Degraded</span>
        <div class="w-2 h-2 rounded-full bg-red-500 inline-block mr-1"></div>
        <span class="">Outage</span>
    </div>
    """

def render_timeline(title, uptime, days, display_hints=False, large=False):
    return f"""
    <div class="flex flex-col gap-2">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between">
            <h3 class="text-xl font-bold">
                {escape(title)}
            </h3>
            <span class="font-semibold text-slate-700">
                {escape(format_uptime(uptime))}
            </span>
        </div>
        <div class="flex flex-row items-center">
            {''.join(render_timeline_day(day, large=large) for day in days)}
        </div>
        {display_hints and render_timeline_hints() or ''}
    </div>
    """

def render_global_status(model):
    return f"""
      <section id="main-section" class="flex flex-col gap-2 p-4 bg-white rounded-lg shadow border border-slate-300">
        <div class="flex flex-col md:flex-row items-center justify-between mb-4">
            <h2 class="text-2xl font-bold">
                Last {model['window']} days uptime
            </h2>
            <div class="text-sm text-slate-500">
                <span>
                    Last updated {escape(datetime.fromisoformat(model['last_updated']).strftime('%b %d, %Y'))}
                </span>
                <span class="border-l border-slate-300 pr-1"></span>
                <span>
                    {model['total_incidents']} incidents in last {model['window']} days
                </span>
            </div>
        </div>
        {render_timeline("Yandex Cloud status", model["global"]["uptime"], model["global"]["days"], display_hints=True, large=True)}
        <div class="text-sm mt-2 text-end __noprint">
            <a href="https://github.com/kapitanov/yc-status-page" target="_blank" class="text-slate-500 hover:text-slate-600 underline">GitHub Repository</a>
            <a href="#" class="text-slate-500 hover:text-slate-600 underline ml-4" onclick="copyToClipboard('main-section'); return false;">Export as image</a>
        </div>
      </section>
    """

def render_per_service_status(model):
    services = model['services']
    services = sorted(services, key=lambda x: x['uptime'])
    return f"""
        <section class="flex flex-col gap-2 p-4 bg-white rounded-lg shadow border border-slate-300">
            <div class="flex flex-col md:flex-row items-center justify-between mb-4">
                <h2 class="text-2xl font-bold">
                    Service uptime ({model['window']} days)
                </h2>
                <div class="text-sm text-slate-500">
                    Per-component uptime from incidents
                </div>
            </div>
            {
            ''.join([ render_timeline(title=s['service']['name'], uptime=s['uptime'], days=s['days']) for s in services])
            }
        </section>
    """

def render(model):
    html = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>The Unofficial Yandex Cloud Status Page</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <script src="https://cdn.jsdelivr.net/npm/html-to-image@1.11.13/dist/html-to-image.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/downloadjs@1.4.7/download.min.js"></script>
  </head>
  <body class="bg-slate-100">
    <main class="flex flex-col gap-8 max-w-4xl mx-auto p-8">
      <section class="">
        <h1 class="font-bold text-3xl text-center">The Unofficial Yandex Cloud Status Page</h1>
        <p class="text-xs text-slate-600 mt-4">
            This page is generated based on the incidents reported by Yandex Cloud over the last 90 days.
            It provides an overview of the overall uptime and a breakdown of incidents by service.
            The data is sourced from the official Yandex Cloud status page and is updated regularly to reflect the latest information.
        </p>
        <p class="text-xs text-slate-600 mt-4">
            Why unofficial?
            Because you can't use it as a way to prove Yandex's SLA violations.
            And it's not affiliated with Yandex in any way.
            It's just a pet project to visualize the reliability of Yandex Cloud services.
        </p>
        <p class="text-xs text-slate-600 mt-4">
            Why do I need this page anyway?
            Just out of curiosity and for fun.
        </p>
        <p class="text-xs text-slate-600 mt-4">
            Heavily inspired by
            <a href="https://mrshu.github.io/github-statuses/" class="text-slate-500 hover:text-slate-600 underline">The Missing GitHub Status Page</a>.
        </p>
      </section>
      {render_global_status(model)}
      {render_per_service_status(model)}
    </main>
    <script src="app.js"></script>
  </body>
</html>
    """

    return html

def render_incidents(input_file: str, output_file: str) -> None:
    with open(input_file, "r") as f:
        input_json = f.read()
    model = json.loads(input_json)
    output_html = render(model)

    with open(output_file, "w") as f:
        f.write(output_html)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.stderr.write("Usage: render.py <input_file> <output_file>\n")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    render_incidents(input_file, output_file)
