#!/usr/bin/env python3

import json
import os
import urllib.request
from datetime import datetime


USERNAME = os.environ.get("GITHUB_USERNAME", "mmlubag")
TOKEN = os.environ["GITHUB_TOKEN"]
OUTPUT_FILE = os.environ.get("OUTPUT_FILE", "contribution-garden.svg")


QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            contributionLevel
            date
          }
        }
      }
    }
  }
}
"""


payload = json.dumps({
    "query": QUERY,
    "variables": {
        "login": USERNAME
    }
}).encode("utf-8")


request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=payload,
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "contribution-garden"
    },
    method="POST",
)


with urllib.request.urlopen(request) as response:
    result = json.loads(response.read().decode("utf-8"))


if "errors" in result:
    raise SystemExit(
        json.dumps(result["errors"], indent=2)
    )


calendar = (
    result["data"]["user"]["contributionsCollection"]["contributionCalendar"]
)

weeks = calendar["weeks"]
total = calendar["totalContributions"]


LEVELS = {
    "NONE": 0,
    "FIRST_QUARTILE": 1,
    "SECOND_QUARTILE": 2,
    "THIRD_QUARTILE": 3,
    "FOURTH_QUARTILE": 4,
}


# ---------------------------------------------------------
# Layout
# ---------------------------------------------------------

CELL = 14
GAP = 4
STEP = CELL + GAP

LEFT = 48
TOP = 28

WIDTH = LEFT + len(weeks) * STEP + 24
HEIGHT = TOP + 7 * STEP + 50


# ---------------------------------------------------------
# Colors
# ---------------------------------------------------------

BG = "#0D1117"

TEXT = "#F0F6FC"
MUTED = "#8B949E"

EMPTY = "#21262D"
BORDER = "#30363D"

SOIL = "#7A5A4A"

STEM = "#82A878"

LEAF = "#A8C79D"
LEAF_DARK = "#6F9969"

PINK = "#D98FA3"
PINK_LIGHT = "#F1BBC9"

CREAM = "#F5DDA4"


# ---------------------------------------------------------
# Plant renderer
# ---------------------------------------------------------

def plant(level, x, y, delay):

    cx = x + CELL / 2
    bottom = y + CELL - 2

    cls = f"plant grow d{delay % 10}"

    # -----------------------------------------------------
    # Level 1 — tiny seedling
    # -----------------------------------------------------

    if level == 1:

        return f"""
<g class="{cls}">

  <ellipse
    cx="{cx}"
    cy="{bottom}"
    rx="2.2"
    ry="1.1"
    fill="{SOIL}"
  />

  <path
    d="M {cx} {bottom - 1}
       L {cx} {bottom - 4.5}"
    stroke="{STEM}"
    stroke-width="1.2"
    stroke-linecap="round"
  />

  <ellipse
    cx="{cx + 1.8}"
    cy="{bottom - 4.2}"
    rx="1.6"
    ry="0.9"
    fill="{LEAF}"
  />

</g>
"""


    # -----------------------------------------------------
    # Level 2 — sprout
    # -----------------------------------------------------

    if level == 2:

        return f"""
<g class="{cls}">

  <ellipse
    cx="{cx}"
    cy="{bottom}"
    rx="2.4"
    ry="1.1"
    fill="{SOIL}"
  />

  <path
    d="M {cx} {bottom - 1}
       L {cx} {bottom - 7}"
    stroke="{STEM}"
    stroke-width="1.25"
    stroke-linecap="round"
  />

  <ellipse
    cx="{cx - 2}"
    cy="{bottom - 5.1}"
    rx="2"
    ry="1"
    fill="{LEAF}"
  />

  <ellipse
    cx="{cx + 2}"
    cy="{bottom - 6.4}"
    rx="2"
    ry="1"
    fill="{LEAF_DARK}"
  />

</g>
"""


    # -----------------------------------------------------
    # Level 3 — leafy plant
    # -----------------------------------------------------

    if level == 3:

        return f"""
<g class="{cls}">

  <ellipse
    cx="{cx}"
    cy="{bottom}"
    rx="2.5"
    ry="1.1"
    fill="{SOIL}"
  />

  <path
    d="M {cx} {bottom - 1}
       L {cx} {bottom - 9}"
    stroke="{STEM}"
    stroke-width="1.3"
    stroke-linecap="round"
  />

  <ellipse
    cx="{cx - 2.6}"
    cy="{bottom - 4.7}"
    rx="2.3"
    ry="1.1"
    fill="{LEAF_DARK}"
  />

  <ellipse
    cx="{cx + 2.6}"
    cy="{bottom - 6.4}"
    rx="2.3"
    ry="1.1"
    fill="{LEAF}"
  />

  <ellipse
    cx="{cx - 1.9}"
    cy="{bottom - 8}"
    rx="1.9"
    ry="0.9"
    fill="{LEAF}"
  />

</g>
"""


    # -----------------------------------------------------
    # Level 4 — flower
    # -----------------------------------------------------

    fy = bottom - 8.3

    return f"""
<g class="{cls}">

  <ellipse
    cx="{cx}"
    cy="{bottom}"
    rx="2.5"
    ry="1.1"
    fill="{SOIL}"
  />

  <path
    d="M {cx} {bottom - 1}
       L {cx} {fy + 1}"
    stroke="{STEM}"
    stroke-width="1.3"
    stroke-linecap="round"
  />

  <ellipse
    cx="{cx - 2.4}"
    cy="{bottom - 4.8}"
    rx="2.2"
    ry="1"
    fill="{LEAF_DARK}"
  />

  <ellipse
    cx="{cx + 2.4}"
    cy="{bottom - 6.2}"
    rx="2.2"
    ry="1"
    fill="{LEAF}"
  />

  <circle
    cx="{cx}"
    cy="{fy - 2}"
    r="2"
    fill="{PINK_LIGHT}"
  />

  <circle
    cx="{cx + 2}"
    cy="{fy}"
    r="2"
    fill="{PINK}"
  />

  <circle
    cx="{cx}"
    cy="{fy + 2}"
    r="2"
    fill="{PINK_LIGHT}"
  />

  <circle
    cx="{cx - 2}"
    cy="{fy}"
    r="2"
    fill="{PINK}"
  />

  <circle
    cx="{cx}"
    cy="{fy}"
    r="1.2"
    fill="{CREAM}"
  />

</g>
"""


# ---------------------------------------------------------
# Month labels
# ---------------------------------------------------------

months = []
seen_months = set()


for week_index, week in enumerate(weeks):

    for day in week["contributionDays"]:

        dt = datetime.strptime(
            day["date"],
            "%Y-%m-%d"
        )

        key = (
            dt.year,
            dt.month
        )

        if key not in seen_months:

            seen_months.add(key)

            months.append(
                (
                    week_index,
                    dt.strftime("%b")
                )
            )


# ---------------------------------------------------------
# Build SVG
# ---------------------------------------------------------

svg = []


svg.append(
    f"""
<svg
  xmlns="http://www.w3.org/2000/svg"
  width="{WIDTH}"
  height="{HEIGHT}"
  viewBox="0 0 {WIDTH} {HEIGHT}"
  role="img"
  aria-labelledby="title desc"
>

<title id="title">
  {USERNAME}'s contribution garden
</title>

<desc id="desc">
  GitHub contributions visualized as plants growing
  from seedlings to pink flowers.
</desc>

<style>

.label {{
  font:
    11px
    -apple-system,
    BlinkMacSystemFont,
    "Segoe UI",
    sans-serif;

  fill: {MUTED};
}}


.plant {{
  transform-box: fill-box;
  transform-origin: center bottom;
}}


.grow {{
  opacity: 0;

  transform:
    translateY(3px)
    scale(.4);

  animation:
    grow
    .7s
    cubic-bezier(.2,.85,.25,1.15)
    forwards;
}}


@keyframes grow {{

  0% {{
    opacity: 0;

    transform:
      translateY(3px)
      scale(.4);
  }}

  75% {{
    opacity: 1;

    transform:
      translateY(-.5px)
      scale(1.08);
  }}

  100% {{
    opacity: 1;

    transform:
      translateY(0)
      scale(1);
  }}

}}


.d0 {{ animation-delay: .05s; }}
.d1 {{ animation-delay: .10s; }}
.d2 {{ animation-delay: .15s; }}
.d3 {{ animation-delay: .20s; }}
.d4 {{ animation-delay: .25s; }}
.d5 {{ animation-delay: .30s; }}
.d6 {{ animation-delay: .35s; }}
.d7 {{ animation-delay: .40s; }}
.d8 {{ animation-delay: .45s; }}
.d9 {{ animation-delay: .50s; }}


@media (prefers-reduced-motion: reduce) {{

  .grow {{
    opacity: 1;
    transform: none;
    animation: none;
  }}

}}

</style>


<rect
  width="100%"
  height="100%"
  rx="12"
  fill="{BG}"
/>

"""
)


# ---------------------------------------------------------
# Month labels
# ---------------------------------------------------------

for week_index, label in months:

    x = LEFT + week_index * STEP

    svg.append(
        f"""
<text
  x="{x}"
  y="22"
  class="label"
>
  {label}
</text>
"""
    )


# ---------------------------------------------------------
# Day labels
# ---------------------------------------------------------

for row, label in [
    (1, "Mon"),
    (3, "Wed"),
    (5, "Fri")
]:

    y = TOP + row * STEP + 10

    svg.append(
        f"""
<text
  x="8"
  y="{y}"
  class="label"
>
  {label}
</text>
"""
    )


# ---------------------------------------------------------
# Contribution cells
# ---------------------------------------------------------

for week_index, week in enumerate(weeks):

    for day_index, day in enumerate(
        week["contributionDays"]
    ):

        x = LEFT + week_index * STEP
        y = TOP + day_index * STEP

        level = LEVELS[
            day["contributionLevel"]
        ]

        count = day[
            "contributionCount"
        ]


        if level == 0:

            tile_fill = EMPTY
            tile_stroke = BORDER

        else:

            tile_fill = "#17251B"
            tile_stroke = "#334A37"


        svg.append(
            f"""
<rect
  x="{x}"
  y="{y}"
  width="{CELL}"
  height="{CELL}"
  rx="3"
  fill="{tile_fill}"
  stroke="{tile_stroke}"
  stroke-width=".65"
>

<title>
  {day["date"]}: {count}
  contribution{"s" if count != 1 else ""}
</title>

</rect>
"""
        )


        if level > 0:

            svg.append(
                plant(
                    level,
                    x,
                    y,
                    week_index + day_index
                )
            )


# ---------------------------------------------------------
# Legend
# ---------------------------------------------------------

legend_y = (
    TOP
    + 7 * STEP
    + 22
)


svg.append(
    f"""
<text
  x="{LEFT}"
  y="{legend_y}"
  class="label"
>
  less
</text>
"""
)


legend_x = LEFT + 28


for level in range(5):

    x = (
        legend_x
        + level * 30
    )


    tile_fill = (
        EMPTY
        if level == 0
        else "#17251B"
    )


    tile_stroke = (
        BORDER
        if level == 0
        else "#334A37"
    )


    svg.append(
        f"""
<rect
  x="{x}"
  y="{legend_y - 11}"
  width="{CELL}"
  height="{CELL}"
  rx="3"
  fill="{tile_fill}"
  stroke="{tile_stroke}"
  stroke-width=".65"
/>
"""
    )


    if level > 0:

        svg.append(
            plant(
                level,
                x,
                legend_y - 11,
                level
            )
        )


svg.append(
    f"""
<text
  x="{legend_x + 150}"
  y="{legend_y}"
  class="label"
>
  more
</text>
"""
)


# ---------------------------------------------------------
# Bottom-right legend explanation
# ---------------------------------------------------------

svg.append(
    f"""
<text
  x="{WIDTH - 255}"
  y="{HEIGHT - 12}"
  class="label"
>
  seedling → sprout → leaves → flower 🌷
</text>
"""
)


svg.append(
    "</svg>"
)


# ---------------------------------------------------------
# Save SVG
# ---------------------------------------------------------

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "\n".join(svg)
    )


print(
    f"Generated {OUTPUT_FILE} "
    f"for {USERNAME} "
    f"with {total} contributions."
)
