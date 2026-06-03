# The Unofficial Yandex Cloud Status Page

This page is generated based on the incidents reported by Yandex Cloud over the last 90 days.
It provides an overview of the overall uptime and a breakdown of incidents by service.
The data is sourced from the official [Yandex Cloud status page](https://status.yandex.cloud/) and is updated regularly to reflect the latest information.

Why unofficial? Because you can't use it as a way to prove Yandex's SLA violations.
And it's not affiliated with Yandex in any way. It's just a pet project to visualize the reliability of Yandex Cloud services.

Why do I need this page anyway? Just out of curiosity and for fun.

## Disclaimer

This is a pet project, created just for fun and to satisfy my curiosity.
The data is sourced from the official Yandex Cloud status page, but I make no guarantees about its accuracy or completeness.

Moreover, there's no guarantee that the uptime calculations are correct and are in line with Yandex's official SLI.

## Acknowledgements

Heavily inspired by [The Missing GitHub Status Page](https://mrshu.github.io/github-statuses/).

## How it works

1. Fetch the incident data from the Yandex Cloud status page using the `scripts/fetch.py` script.
2. Preprocess the raw incident data using the `scripts/preprocess.py` script to extract relevant information and format it for rendering.
3. Render the incident timelines and uptime statistics into an HTML page using the `scripts/render.py` script.
4. The rendered HTML page is saved in the `web` directory and can be served using any static file server.
5. A dedicated GitHub Action workflow is set up to publish the rendered page to GitHub Pages on every push to the master branch and on a daily schedule.

## How to run locally

### Prerequisites

Install [uv](https://github.com/astral-sh/uv) per the [installation docs](https://docs.astral.sh/uv/getting-started/installation/).

### Running the project

```shell
$ uv venv
$ uv sync
$ make run
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.