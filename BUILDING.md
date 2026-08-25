# YouTube LeadGen Tool - Build Instructions

## Overview
This is a refactored YouTube lead generation tool with a modern GUI that allows you to:
- Search YouTube channels by keywords
- Filter by subscriber count, country, and bio keywords
- Scrape emails from channel About pages
- Export results to CSV

## Files Structure
```
project_root/
├── ytleadgen_core.py       # Core scraping logic
├── ytleadgen_gui.py        # GUI application
├── requirements.txt        # Python dependencies
├── BUILD_INSTRUCTIONS.md   # This file
└── chromedriver.exe        # (optional) Place here if not in PATH
```

## Prerequisites

### 1. Python Installation
- Python 3.8 or higher
- Download from: https://www.python.org/downloads/

### 2. Chrome Browser
- Install Google Chrome browser
- Download from: https://www.google.com/chrome/

### 3. ChromeDriver
- Download ChromeDriver matching your Chrome version
- Get it from: https://chromedriver.chromium.org/downloads
- Either:
  - Add to your system PATH, OR
  - Place `chromedriver.exe` in the same folder as the Python scripts

### 4. YouTube API Key
- Go to: https://console.developers.google.com/
- Create a new project
- Enable "YouTube Data API v3"
- Create credentials (API key)
- Copy the API key for use in the app

## Installation Steps

### Step 1: Install Dependencies
Open Command Prompt or Terminal in the project folder and run:
```bash
pip install -r requirements.txt
```

### Step 2: Test the Application
Run the GUI application directly:
```bash
python ytleadgen_gui.py
```

The GUI should open. Test it with your API key and a simple search.

### Step 3: Build the EXE File
Once testing is successful, build the executable:

```bash
pyinstaller --onefile --noconsole --name="YouTubeLeadGen" ytleadgen_gui.py
```

**Build Options Explained:**
- `--onefile`: Creates a single .exe file (all dependencies bundled)
- `--noconsole`: No console window (GUI only)
- `--name="YouTubeLeadGen"`: Name of the output executable

**Alternative: With Console (for debugging)**
If you want to see error messages during testing:
```bash
pyinstaller --onefile --name="YouTubeLeadGen" ytleadgen_gui.py
```

### Step 4: Locate the EXE
After building, you'll find the executable at:
```
dist/YouTubeLeadGen.exe
```

### Step 5: Prepare for Distribution
1. Copy `YouTubeLeadGen.exe` from the `dist` folder
2. (Optional) Copy `chromedriver.exe` to the same folder as the .exe
3. The .exe can now run independently without Python installed

## Using the Application

### First Run
1. Launch `YouTubeLeadGen.exe`
2. Enter your YouTube API key
3. Click "Save" to store it for future use
4. All settings are automatically saved between sessions

### Configuration Options

**Required Fields:**
- **API Key**: Your YouTube Data API v3 key
- **Keywords**: Comma-separated search terms (e.g., "tech review, gaming")

**Subscriber Filters:**
- **Min Subscribers**: Minimum subscriber count (default: 0)
- **Max Subscribers**: Maximum subscriber count (default: 1,000,000,000)

**Optional Filters:**
- **Bio Keyword**: Filter channels that include this word in their description
- **Country**: Filter by country code (e.g., US, IN, UK)

**Options:**
- **Require Email**: Only save channels with found emails
- **Test Mode**: Limit to 5 channels for testing
- **Headless Browser**: Run Chrome invisibly (faster, less distracting)

**Output:**
- **Output Folder**: Where to save the CSV file
- Click "Browse" to select a folder

### Running Lead Generation
1. Fill in all required fields
2. Click "Run LeadGen"
3. Watch the log for progress
4. Results are saved to `youtube_results.csv` (or `test_results.csv` in test mode)

### Output Format
CSV file with columns:
- `channel_id`: YouTube channel ID
- `title`: Channel name
- `subs`: Subscriber count
- `country`: Country code (if available)
- `emails`: Semicolon-separated email addresses

## Troubleshooting

### "ChromeDriver not found"
- Download ChromeDriver for your Chrome version
- Place `chromedriver.exe` next to `YouTubeLeadGen.exe`

### "API Key invalid"
- Verify your API key is correct
- Ensure YouTube Data API v3 is enabled in Google Cloud Console
- Check API quotas haven't been exceeded

### "ModuleNotFoundError" when running Python script
```bash
pip install -r requirements.txt
```

### EXE won't start
- Rebuild with console mode to see errors:
  ```bash
  pyinstaller --onefile ytleadgen_gui.py
  ```
- Check antivirus isn't blocking it

### Selenium/ChromeDriver issues
- Update Chrome browser to latest version
- Download matching ChromeDriver version
- Make sure Chrome is installed (not just Chromium)

### CAPTCHAs appearing
- Uncheck "Headless Browser" to solve CAPTCHAs manually
- Add delays between requests (already implemented)
- Use test mode to verify without hitting rate limits

## Advanced Configuration

### Config File Location
Settings are saved in `ytleadgen_config.json` in the same folder as the executable.

You can manually edit this file to:
- Preset values for multiple users
- Backup/restore configurations

### Running in Non-Headless Mode
Uncheck "Headless Browser" to:
- See what the browser is doing
- Manually solve CAPTCHAs
- Debug scraping issues

### API Rate Limits
YouTube API has quotas (typically 10,000 units/day):
- Each search costs ~100 units
- Each channel detail fetch costs ~1 unit
- Use test mode to avoid burning quota during development

## Tips for Best Results

1. **Start with Test Mode**: Always test with 5 channels first
2. **Use Specific Keywords**: More targeted = better results
3. **Set Reasonable Filters**: Not all channels show subscriber counts
4. **Don't Require Email**: Many channels don't publicly list emails
5. **Use Headless Mode**: Faster and less distracting for large batches
6. **Monitor Quotas**: Keep track of your API usage

## Building for Different Platforms

### Windows
```bash
pyinstaller --onefile --noconsole --name="YouTubeLeadGen" ytleadgen_gui.py
```

### macOS
```bash
pyinstaller --onefile --windowed --name="YouTubeLeadGen" ytleadgen_gui.py
```

### Linux
```bash
pyinstaller --onefile --name="YouTubeLeadGen" ytleadgen_gui.py
```

Note: ChromeDriver must match the platform (download the appropriate version).

## Support & Issues

If you encounter issues:
1. Check the log output in the GUI
2. Try running in non-headless mode
3. Verify all prerequisites are installed
4. Check that ChromeDriver version matches Chrome browser version

## License & Usage

This tool is for legitimate business research only. Always respect:
- YouTube's Terms of Service
- Google API usage limits
- Privacy laws in your jurisdiction
- Anti-spam regulations

Do not use for spam or unauthorized contact.
