<img width="1127" height="972" alt="image" src="https://github.com/user-attachments/assets/e4ac7889-40f3-45af-a6f4-72bf4774b382" />
# YouTube LeadGen Tool

A desktop application for discovering relevant YouTube channels and extracting publicly listed business contact emails into structured CSV output.

Built with **Python, YouTube Data API v3, Selenium, Tkinter, and CSV-based data processing**.

## Overview

YouTube LeadGen Tool automates the repetitive parts of finding potentially relevant channels for business research.

The application:

1. Discovers channels using the YouTube Data API.
2. Retrieves channel metadata and descriptions.
3. Filters channels by configurable criteria.
4. Visits publicly accessible YouTube About pages with Selenium.
5. Extracts publicly listed business email addresses.
6. Deduplicates and writes results incrementally to CSV.

The project is designed for legitimate research and outreach workflows and only targets information that is publicly available.

## Architecture

```text
                ┌─────────────────────┐
                │     Tkinter GUI     │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   Core Processing   │
                │   ytleadgen_core.py │
                └──────────┬──────────┘
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
   ┌──────────────────┐        ┌──────────────────┐
   │ YouTube Data API  │        │     Selenium     │
   │ Channel discovery │        │ About-page data  │
   └────────┬─────────┘        └────────┬─────────┘
            │                           │
            └────────────┬──────────────┘
                         ▼
                ┌─────────────────────┐
                │ Filtering + Email   │
                │ Extraction + Dedup  │
                └──────────┬──────────┘
                           ▼
                    ┌─────────────┐
                    │ CSV Output  │
                    └─────────────┘
```

## Features

### Channel Discovery

Search for channels using configurable keywords through the YouTube Data API v3.

### Metadata Filtering

Filter discovered channels using criteria such as:

* Subscriber count
* Country
* Description keywords
* Presence of publicly listed business contact information

### Public Email Extraction

Selenium visits channel About pages and extracts email addresses that are publicly exposed by the channel.

### Deduplication

Duplicate channel IDs and duplicate email addresses are removed before export.

### Incremental CSV Output

Results are written as they are processed rather than waiting for the entire scan to finish.

### Desktop GUI

The Tkinter interface provides:

* API key configuration
* Keyword configuration
* Filtering controls
* Test mode
* Headless browser mode
* Output directory selection
* Progress reporting
* Runtime logs

## Project Structure

```text
.
├── ytleadgen_core.py
├── ytleadgen_gui.py
├── requirements.txt
├── BUILDING.md
├── .gitignore
└── README.md
```

## Requirements

* Python 3.9+
* Google/YouTube Data API v3 key
* Google Chrome
* Selenium-compatible ChromeDriver environment

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Create a local `ytleadgen_config.json` file in the project directory.

Example:

```json
{
  "api_key": "YOUR_YOUTUBE_API_KEY",
  "keywords": "ai,technology",
  "min_subs": 0,
  "max_subs": 1000000,
  "bio_key": "",
  "country": "",
  "require_email": true,
  "test_mode": true,
  "headless": true,
  "out_dir": "./output"
}
```

Do **not** commit your API key or other local credentials to GitHub.

## Running

Launch the graphical interface with:

```bash
python ytleadgen_gui.py
```

Configure the search criteria and start a scan from the GUI.

For development and verification, enable **Test Mode** to keep scans small and easier to inspect.

## Engineering Notes

The application separates discovery, metadata processing, filtering, browser automation, extraction, and export into distinct functions rather than implementing the entire workflow in one script.

Channel lookups are batched to reduce unnecessary API requests, while discovered channel IDs are deduplicated before metadata processing.

CSV output is written incrementally so that completed results are preserved even if a later channel fails during processing.

Selenium is used only where browser-rendered channel information is required, while the YouTube API handles structured channel discovery and metadata retrieval.

## Responsible Use

This project is intended for legitimate business research and outreach workflows.

It only extracts contact information that channel owners have chosen to make publicly available. Users are responsible for complying with applicable laws, platform terms, API policies, privacy requirements, and anti-spam regulations.

## Documentation

See [BUILDING.md](BUILDING.md) for development and packaging instructions.

## License

See the repository license for usage and redistribution terms.

