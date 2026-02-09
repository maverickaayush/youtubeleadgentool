# youtubeleadgentool
A YouTube lead generation tool built using the official YouTube Data API v3 and browser automation. It discovers relevant channels via keywords, fetches channel metadata, and extracts publicly available business emails from About pages, exporting clean CSVs for outreach.

Features

Keyword-based YouTube channel discovery

Subscriber count, country, and metadata filtering

Public business email extraction from About pages

Test Mode (low-risk validation)

Full Mode (high-volume lead generation)

Clean CSV export for campaigns

Tech Stack

YouTube Data API v3 (Google Console)

Selenium (browser automation)

Python backend

CSV-based output

How It Works

API Robot

Searches channels using YouTube Data API v3

Fetches metadata and About page links

Browser Robot

Opens verified browser session

Navigates to About pages

Extracts publicly visible business emails

Setup

Create a Google Cloud project

Enable YouTube Data API v3

Generate an API key

Add the key to the project config

Run in Test Mode before Full Mode

Output

Channel ID

Channel Name

Subscriber Count

Country

Extracted Email(s)

Use Cases

Influencer outreach

Brand collaborations

Agency lead generation

Market research
