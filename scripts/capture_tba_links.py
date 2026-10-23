"""One-time capture of team websites and social accounts (no TBA API key yet).

Merges the curated `socials` on The REFINERY website's team pages (BioNanomics/REFINERY-site
src/content/teams/*.mdx) with the links on saved TBA team pages. Each link keeps its source.

    python scripts/capture_tba_links.py <TBA pages folder> <REFINERY team .mdx folder> broadcast/data/team-links.json 1501 1720 ...

With a TBA key, scripts/fetch_tba.py returns the TBA fields (website, social) through the API.
"""
import hashlib
import html
import json
import os
import re
import sys

TBA_KINDS = {"facebook-profile": "Facebook", "instagram-profile": "Instagram", "twitter-profile": "X", "youtube-channel": "YouTube",
             "github-profile": "GitHub", "gitlab-profile": "GitLab"}
REFINERY_KINDS = {"instagram": "Instagram", "facebook": "Facebook", "twitter": "X", "x": "X", "youtube": "YouTube", "tiktok": "TikTok",
                  "github": "GitHub", "flickr": "Flickr", "website": "Website"}


def refinery_links(folder, number, program):
    """The `socials:` block from The REFINERY's page for this team, if there is one."""
    for name in os.listdir(folder):
        if not name.startswith(f"{program}-{number}-"):
            continue
        front = open(os.path.join(folder, name), encoding="utf-8").read().split("---")[1]
        block = re.search(r"^socials:\n((?:[ \t]+.*\n)+)", front, flags=re.M)
        pairs = re.findall(r"^\s+(\w+):\s*[\"']([^\"']+)[\"']", block.group(1), flags=re.M) if block else []
        page = f"https://github.com/BioNanomics/REFINERY-site/blob/main/src/content/teams/{name}"
        return [{"type": REFINERY_KINDS.get(k, k.title()), "url": u, "source": "The REFINERY", "sourceUrl": page} for k, u in pairs]
    return []


def tba_links(path, number):
    raw = open(path, "rb").read()
    page = raw.decode("utf-8")
    source = f"https://www.thebluealliance.com/team/{number}/2026"
    links = []
    site = re.search(r'id="team-website" href="([^"]+)"', page)
    if site and "firstinspires.org" not in site.group(1):  # a FIRST link is not the team's own site
        links.append({"type": "Website", "url": html.unescape(site.group(1)), "source": "The Blue Alliance", "sourceUrl": source})
    for url, kind in re.findall(r'<a href="([^"]+)" class="hashtag-link-wrapper"[^>]*data-media-type="([^"]+)"', page):
        links.append({"type": TBA_KINDS.get(kind, kind), "url": html.unescape(url), "source": "The Blue Alliance", "sourceUrl": source})
    return links, hashlib.sha256(raw).hexdigest()


def same(url):
    url = url.lower().rstrip("/").replace("http://", "https://").replace("://www.", "://").replace("twitter.com", "x.com")
    return url


def main():
    tba_folder, refinery_folder, out = sys.argv[1], sys.argv[2], sys.argv[3]
    teams = []
    for number in map(int, sys.argv[4:]):
        path = os.path.join(tba_folder, f"{number}-2026.html")
        program = "frc" if os.path.exists(path) else "ftc"
        tba, digest = tba_links(path, number) if program == "frc" else ([], None)
        links, seen = [], set()
        for link in refinery_links(refinery_folder, number, program) + tba:  # curated list first, then anything TBA adds
            if same(link["url"]) not in seen:
                seen.add(same(link["url"]))
                links.append(link)
        teams.append({"teamNumber": number, "program": program, "links": links, **({"tbaResponseSha256": digest} if digest else {})})
    doc = {"sources": ["The REFINERY website team pages", "The Blue Alliance public team pages"], "retrievedDate": "2026-10-22",
           "note": "Public team links. Confirm with the team before publishing a contact.", "teams": teams}
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
    for t in teams:
        print(t["teamNumber"], [f"{x['type']}" for x in t["links"]])


if __name__ == "__main__":
    main()
