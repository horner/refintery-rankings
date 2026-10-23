# Action photo plan

**Goal:** at least one action photo of every team on the site. Right now only four teams have one: 4982, 8742, 9119 and 9431. There are 13 FRC teams and 3 FTC teams in all. Photos show up on the team pages, the main gallery, the press kit's logos & photos page, and the team share cards. Each photo gets a credit line.

## Where photos will come from

| Source | What we can use | Before using |
|---|---|---|
| The REFINERY's own photos (website, events it runs) | Yes | Nothing extra; credit "The REFINERY". |
| Photos teams send us | Yes, with the team's OK | Get a short written OK from the team lead or coach, and the photographer's name for the credit. |
| FIRST Indiana Robotics photos (Flickr, social) | Only if the album's license allows it | Check the license on each album. Ask FIRST Indiana if unclear. |
| Robot photos on The Blue Alliance | Ask the team first | Teams upload these, and the rights stay with the team. |
| Local news photos | No | Link to the story instead. |

## Students in photos

- Most people on robotics teams are minors. Use photos that teams or their schools have already shared publicly, or that a coach has approved.
- Don't name students in captions unless the team provides the names for that purpose.
- Prefer robot, match and crowd shots over close-up portraits.
- If a family or school asks for a photo to come down, remove it the same day: delete the entry from `broadcast/data/photos.json` and the file from `broadcast/dist/assets/photos/`, then rebuild.

## Shot list (per team)

1. The robot on the field during a match, with its bumper number readable.
2. The drive team at the driver station.
3. Pit work: students fixing or tuning the robot.
4. A celebration: alliance selection, a win, or an award.
5. One team group photo with the robot (optional; teams usually have one).

Landscape, at least 1,600 pixels wide, in focus, no heavy filters.

## Upcoming chances

- **Boiler Bot Battle**, Oct 23–24, 2026, Lafayette: ask attending teams to send shots.
- **Monster Match**, Oct 31, 2026, Wayne High School. The REFINERY runs this event, so assign a photographer:
  - every team's robot on the field
  - drive teams
  - the crowd and costumes
  - the college and career fair
- **2027 district events**, starting March 12. The Fort Wayne event (Apr 1–3, Homestead High School) is the home event for most teams.

## How to add a photo

```bash
python broadcast/scripts/add_photo.py path/to/photo.jpg --id robot-1501 \
  --caption "THRUST (1501) climbs the tower at Mishawaka." --credit "Photographer Name" \
  --source "Sent by Team 1501, 2027-03-14" --teams 1501
python broadcast/scripts/build.py
python broadcast/scripts/build_share_images.py
python scripts/verify.py --write-checksums && python broadcast/scripts/verify.py
```

The script resizes the photo to WebP, records its source, credit and checksum in `broadcast/data/photos.json`, and tags the teams. A tagged photo appears on that team's page automatically.

## Asking teams

A short note to send to team leads:

> We're building out Northeast Indiana Robotics, a sports-style page for every robotics team in the region (link). We'd love a couple of action photos of your robot and team for your team page. Send them to celder@bionanomics.com with the photographer's name for the credit and a quick OK to post them. Thanks!
