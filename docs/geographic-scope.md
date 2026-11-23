# Geographic scope and evidence

**Research date: October 22, 2026. Season: 2026 FIRST Robotics Competition (FRC).**

The 16 identified teams—12 in Indiana and four in nearby Michigan or Ohio—have reference points within **60 straight-line miles of downtown Fort Wayne** under the convention documented here. This is a point-to-point radius, not driving mileage. The other rows use a linked school or community host as their geographic reference; these points do not establish where each robot is built.

This verification was **newly rebuilt for publication on October 22, 2026**. The earlier geographic artifacts were unavailable. The coordinates and fixed downtown origin below are newly documented inputs, not a claim that the original calculations were recovered. No team was added to or removed from the roster by this rebuild. Team 1720 PhyXTGears is not part of The REFINERY and is not included. The complete inputs, source URLs, returned coordinate fields, and calculations are in [geography.json](../data/geography.json).

## Radius and origin

The fixed origin is **Citizens Square, 200 East Berry Street, Fort Wayne, IN 46802**. The [City of Fort Wayne contact page](https://www.cityoffortwayne.in.gov/1109/Contact-Us) supplies this civic address; the city's [customer-service page](https://www.cityoffortwayne.org/publicworks/52-mayors-office/neighborhoods/196-customer-service.html) places it in downtown Fort Wayne. It is an operational downtown reference, not the geographic centroid of the city or a definition of the entire downtown area.

The Census geocoder returned:

| Origin component | Frozen value |
|---|---:|
| Latitude | 41.079467666017 |
| Longitude | -85.137939575106 |
| Radius | 60 miles |
| Earth radius used in calculation | 3,958.7613 miles |

Distances use the haversine great-circle formula with that fixed Earth radius. A point qualifies when the **unrounded calculated distance is at most 60 miles**. Tables display one decimal mile to avoid implying building-level measurement precision. The JSON preserves six decimal places for checking the arithmetic, alongside the original coordinate values.

## Indiana teams

The school or program links in this table lead to official address or location evidence. Team-number links lead to the corresponding FIRST season page, which supplies team identity and affiliation context. East Noble appears three times because it has three separate FRC teams; all three use the same school reference point.

| Team | High school or community program | Location | Reference used | Approx. miles |
|---|---|---|---|---:|
| [1501](https://frc-events.firstinspires.org/2026/team/1501) | [Huntington North High School / Huntington County 4-H](https://hnhs.hccsc.k12.in.us/services/administration/main-office) | Huntington, IN | School address | 23.3 |
| [9119](https://frc-events.firstinspires.org/2026/team/9119) | [North Side High School](https://northside.fortwayneschools.org/contact-us) | Fort Wayne, IN | School address | 1.2 |
| [9431](https://frc-events.firstinspires.org/2026/team/9431) | [R. Nelson Snider High School](https://snider.fortwayneschools.org/) | Fort Wayne, IN | School address | 3.4 |
| [4982](https://frc-events.firstinspires.org/2026/team/4982) | [Homestead High School](https://homestead.sacs.k12.in.us/home) | Fort Wayne, IN | School address | 8.0 |
| [10434](https://frc-events.firstinspires.org/2026/team/10434) | [Northrop High School](https://northrop.fortwayneschools.org/) | Fort Wayne, IN | School address | 4.5 |
| [8103](https://frc-events.firstinspires.org/2026/team/8103) | [East Noble High School](https://hs.eastnoble.net/page/contact-us/) | Kendallville, IN | School address | 25.3 |
| [10332](https://frc-events.firstinspires.org/2026/team/10332) | [Carroll High School](https://ch.nacs.k12.in.us/51740_2) | Fort Wayne, IN | School address | 8.2 |
| [8742](https://frc-events.firstinspires.org/2026/team/8742) | [Madison-Grant Jr./Sr. High School](https://park.mgusc.k12.in.us/o/mghs/page/contact-us) | Fairmount, IN | School address | 55.5 |
| [10172](https://frc-events.firstinspires.org/2026/team/10172) | [South Side High School](https://southside.fortwayneschools.org/contact-us) | Fort Wayne, IN | School address | 1.9 |
| [8431](https://frc-events.firstinspires.org/2026/team/8431) | [East Noble High School](https://hs.eastnoble.net/page/contact-us/) | Kendallville, IN | School address | 25.3 |
| [10411](https://frc-events.firstinspires.org/2026/team/10411) | [Wayne High School](https://wayne.fortwayneschools.org/contact-us) | Fort Wayne, IN | School address | 5.4 |
| [8432](https://frc-events.firstinspires.org/2026/team/8432) | [East Noble High School](https://hs.eastnoble.net/page/contact-us/) | Kendallville, IN | School address | 25.3 |

**Huntington, 1501:** the [school's robotics page](https://huntingtonnhs.ss13.sharpschool.com/get_involved/clubs/robotics) documents the Huntington North connection, and the [team FAQ](https://huntingtonrobotics.org/faq/) describes the wider community program. Huntington North's campus is a useful reference for the requested high-school connection, but it should not be described as the only school students can come from or as a verified workshop address. The [canonical roster](../data/roster.json) preserves the affiliation distinction.

## Nearby teams across the state line

These four teams belong in a separate nearby-border group. Their inclusion does not make their schools part of Northeast Indiana.

| Team | High school or community program | Location | Reference used | Approx. miles |
|---|---|---|---|---:|
| [5559](https://frc-events.firstinspires.org/2026/team/5559) | [Camden-Frontier School](https://www.camdenfrontier.org/) | Camden, MI | School address | 53.4 |
| [3777](https://frc-events.firstinspires.org/2026/team/3777) | [Lima Family YMCA (community team)](https://limaymca.net/contact-us/) | Lima, OH | Host address | 58.8 † |
| [6556](https://frc-events.firstinspires.org/2026/team/6556) | [Waldron School](https://www.waldronspartans.org/) | Waldron, MI | School address | 58.6 † |
| [11407](https://frc-events.firstinspires.org/2026/team/11407) | [Sturgis High School](https://shs.sturgisps.org/home) | Sturgis, MI | NCES school point | 51.4 |

† **Boundary-sensitive references:** Waldron's school point is about **1.4 miles inside** the radius; the Lima YMCA host point is about **1.2 miles inside**. Both satisfy the stated calculation. A materially different downtown origin or team facility would require recalculation.

For **3777**, the reference is the [Lima Family YMCA](https://limaymca.net/contact-us/), a community host. Its [FIRST record](https://frc-events.firstinspires.org/2026/team/3777) identifies a community program associated with the YMCA and University of Northwestern Ohio. Using the YMCA address does not establish that its workshop is there, and the program should not be relabeled as one high school's exclusive team.

## How the reference points were established

### Published street address plus Census geocoding

Official school and host pages supplied the addresses. These were submitted to the [U.S. Census Bureau geocoder](https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html), using `Public_AR_Current`. The JSON retains the exact query URL, matched address, benchmark, TIGER line identifier, and returned coordinates for each successful match.

The Census Bureau explains that its service [interpolates positions along address ranges](https://cdn.www.census.gov/programs-surveys/geography/technical-documentation/complete-technical-documentation/census-geocoder.html). These are approximate address locations. A successful geocode is not a surveyed rooftop coordinate and does not independently validate team occupancy. Official address evidence and FIRST/team affiliation evidence are therefore kept separately.

### Sturgis and Elkhart High School: NCES school points

Census geocoding returned no match for the submitted Sturgis and Elkhart High School addresses. The replacement evidence is the official **NCES CCD school-point layer** exposed through the [NCES School & District Navigator](https://nces.ed.gov/ccd/schoolmap/) and its [public geographic data service](https://nces.ed.gov/arcgis/rest/services/CCD/CCD_Data/MapServer/0?f=pjson).

The queried records identify the **2024–2025 survey year**:

| School | NCES ID | Latitude | Longitude | Current address corroboration |
|---|---|---:|---:|---|
| Sturgis High School | 263309006864 | 41.7975 | −85.4002 | [216 Vinewood Avenue](https://shs.sturgisps.org/home) |
| Elkhart High School | 180327002693 | 41.6965 | −86.014211 | [2608 California Road](https://ehs.elkhart.k12.in.us/about/administration) |

These are school-location points, not new 2026 measurements. The record's own survey-year field is retained; the older generic description on the service landing page is not used as the record date. The exact query and returned identifying fields are in the JSON.

### E3 Robotics Center: official contact-map marker

The [E3 Robotics Center contact page](https://www.e3robotics.org/contact.html) lists **3709 Cassopolis Street, Elkhart, IN 46514** and embeds a map with `lat=41.7424151`, `long=-85.9749921`, and `point=1`. These parameters provide a reproducible official host-map reference. The exact iframe URL is retained in the JSON. Census geocoding did not return a match for the submitted address.

## Exclusions and boundary decisions

| Team or category | Decision | Evidence and reason |
|---|---|---|
| **1555, CryoFrost / E3 Robotics Center**, Elkhart, IN | Outside: **63.1 miles** | The current [FIRST season page](https://frc-events.firstinspires.org/2026/team/1555) identifies the team. Its E3 connection is documented by the [team profile](https://www.instagram.com/frc1555/) and [E3's public organizational profile](https://www.linkedin.com/company/e3rc); the [official E3 contact map](https://www.e3robotics.org/contact.html) supplies the host reference. |
| **2867, ElkLogics / Elkhart High School**, Elkhart, IN | Outside: **62.3 miles** | The [FIRST team page](https://frc-events.firstinspires.org/team/2867) and [school board packet](https://docs.elkhart.k12.in.us/board/public_packets/2024/November%2012%202024%20-%20Public%20Board%20Packet.pdf) establish the school connection. The current [California Road campus address](https://ehs.elkhart.k12.in.us/about/administration) matches the NCES point. A city-center estimate for Elkhart is not an appropriate substitute for this campus. |
| **6181, Cryptic Cyborgs**, Archbold, OH | Excluded from the 2026 comparison for activity | [The Blue Alliance team history](https://www.thebluealliance.com/team/6181) says it last competed in **2025**; no 2026 competition record was found. This does not establish that the organization has permanently ceased operating. No exact geographic distance is asserted here, because activity is the exclusion reason. |
| **FIRST Tech Challenge and FIRST LEGO League** | Outside program scope | This study compares FRC teams and their Statbotics results. Other FIRST programs should be inventoried separately rather than mixed into the FRC rankings. |

The two Elkhart reference points are approximately **62–63 miles** from this origin, consistent with the earlier broad 62–64-mile campus estimate. The publication now has specific, reproducible support for those exclusions.

## Reproducing the arithmetic

Run the following from the repository root. It uses only Python's standard library and the frozen coordinates in the JSON; no network access is needed.

```python
import json
import math
from pathlib import Path

data = json.loads(Path("data/geography.json").read_text())
origin = data["origin"]["coordinates"]
radius = data["scope"]["radius_miles"]
earth_radius = data["scope"]["earth_radius_miles"]
locations = {x["location_id"]: x for x in data["locations"]}

def miles(point):
    lat1 = math.radians(origin["latitude"])
    lat2 = math.radians(point["latitude"])
    dlat = lat2 - lat1
    dlon = math.radians(point["longitude"] - origin["longitude"])
    a = (math.sin(dlat / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2)
    return earth_radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

for row in data["teams"] + data["exclusions"]:
    if row["location_id"] is None:
        continue
    value = miles(locations[row["location_id"]]["coordinates"])
    assert abs(value - row["distance_miles"]) < 0.000001
    assert (value <= radius) == row["within_radius"]
    print(row["team_number"], f"{value:.1f} miles", value <= radius)
```

## Interpretation limits

The geographic evidence supports the **identified roster under a stated location convention**. It is not a census of all FIRST programs, a verified inventory of every robot workshop, or proof that no unlisted community team exists.

The principal remaining geographic uncertainty is the relationship between each proxy and the team's actual working location, especially the Matthews town point and the Lima community host. Near-boundary membership should be revisited if a different origin, campus, or workshop becomes the intended reference. The haversine sphere is also an approximation to an ellipsoidal Earth, and extra saved decimals do not remove location uncertainty.

Live sources and the Census `Public_AR_Current` benchmark can change. Preserving the returned coordinates and identifying fields makes this calculation reproducible even when a future lookup gives a slightly different point. All links in this document were researched or retrieved for this rebuild on **October 22, 2026**.

