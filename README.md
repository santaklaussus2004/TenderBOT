# TenderBOT

AI-powered Telegram bot for monitoring and analyzing public procurement tenders in Kazakhstan.

TenderBOT is currently used in a real business workflow by **AstanaTech**.

The system automatically monitors Kazakhstan's public procurement market, collects tender information, analyzes documents, identifies winners, searches for company contacts, filters relevant opportunities using an LLM, and delivers the results directly through Telegram.

## Production Use

🟢 **Status: Active / In Production**

TenderBOT is currently used by **AstanaTech** to automate tender monitoring, procurement analysis, winner discovery, and business development workflows.

Instead of manually searching through procurement announcements, opening documents, identifying winners, searching for company contacts, and preparing outreach messages, the system automates most of this process.

The goal is to transform raw procurement data into actionable business opportunities.

## Main Features

### Tender Monitoring

TenderBOT automatically searches the Kazakhstan public procurement portal:

`goszakup.gov.kz`

The system collects information such as:

- tender name;
- announcement number;
- publication date;
- application deadlines;
- tender status;
- tender amount;
- lots;
- winners;
- second-place suppliers;
- procurement documents.

## AI Tender Filtering

Not every procurement announcement is relevant to AstanaTech.

TenderBOT uses an LLM to analyze tenders and determine whether they match the company's business areas.

Relevant tenders continue through the processing pipeline.

Irrelevant tenders are automatically separated and stored in:

```text
trash.json
```

This significantly reduces the amount of procurement data that needs to be reviewed manually.

## Tender Winner Extraction

For each relevant tender, the system extracts information about the winning company.

This can include:

- company name;
- BIN / IIN;
- lot number;
- lot description;
- contract amount;
- winner status.

## Company Enrichment

After identifying the winner, TenderBOT attempts to collect additional company information.

The enrichment pipeline can retrieve:

- phone numbers;
- email addresses;
- company websites;
- company activity status;
- registration information;
- available company information;
- known violations.

If the primary company information source does not contain enough data, the system can use additional web searches as a fallback.

## Tender Document Analysis

TenderBOT downloads available procurement documents and extracts their text.

The documents can then be analyzed using an LLM.

Instead of manually reading large technical specifications or procurement documents, the system generates short summaries containing the most important information.

Example:

```json
{
  "name": "technical_specification.pdf",
  "url": "https://goszakup.gov.kz/...",
  "summary": "Short AI-generated summary of the tender document."
}
```

## AI-Generated Outreach

After identifying the tender winner, the system can generate a personalized business outreach message.

The message can be created using information about:

- the tender;
- the lot;
- the winner;
- the company;
- AstanaTech's services.

This provides a starting point for B2B outreach through channels such as email or direct communication.

## Telegram Bot

TenderBOT provides a Telegram interface for accessing collected procurement information.

### Commands

| Command | Description |
|---|---|
| `/start` | Start the bot and subscribe to automatic notifications |
| `/today` | Show tenders collected today |
| `/before` | Show tenders from previous days |
| `/past` | Show historical tenders |
| `/trash` | Show tenders rejected by the AI filter |
| `/stop` | Disable automatic notifications |
| `/id` | Show your Telegram user ID |

## Automatic Notifications

The Telegram bot periodically checks whether new tenders have appeared.

By default, the system can perform a check every:

```text
3 hours
```

When a new relevant tender is detected, subscribed Telegram users can automatically receive it.

The bot stores its state so that previously processed tenders are not repeatedly sent.

## System Architecture

```text
                 Kazakhstan Public Procurement
                       goszakup.gov.kz
                              |
                              v
                     Tender Web Scraper
                              |
              +---------------+---------------+
              |                               |
              v                               v
       Tender Metadata                  Tender Documents
              |                               |
              v                               v
       Winner Extraction               Text Extraction
              |                               |
              v                               v
      Company Enrichment                 LLM Summary
              |
              v
       LLM Tender Filtering
              |
              v
     Personalized Outreach
              |
              v
          JSON Storage
              |
              v
         Telegram Bot
              |
              v
          AstanaTech
```

## Workflow

```text
1. Generate tender search queries
2. Search goszakup.gov.kz
3. Collect procurement announcements
4. Extract tender information
5. Use an LLM to determine tender relevance
6. Extract lots and tender winners
7. Search for winner contact information
8. Download procurement documents
9. Extract text from documents
10. Generate AI summaries
11. Generate personalized outreach messages
12. Store processed data in JSON
13. Telegram bot reads the processed data
14. Send relevant tenders to users
15. Continue monitoring for new opportunities
```

## Example Data Structure

Tender information is stored in JSON.

Example:

```json
[
  {
    "url": "https://goszakup.gov.kz/ru/announce/index/...",
    "general": {
      "announcement_number": "...",
      "announcement_name": "...",
      "status": "...",
      "publication_date": "..."
    },
    "documents": [
      {
        "name": "technical_specification.pdf",
        "url": "https://goszakup.gov.kz/...",
        "summary": "AI-generated summary of the document."
      }
    ],
    "winners": [
      {
        "lot_number": "...",
        "lot_name": "...",
        "amount": "...",
        "winner_name": "...",
        "winner_iin": "...",
        "phone_number": "...",
        "email": "...",
        "is_active": true,
        "has_violations": false,
        "winner_websites": [],
        "message": "AI-generated personalized outreach message."
      }
    ]
  }
]
```

## Tech Stack

- Python
- OpenAI API
- Telegram Bot API
- `python-telegram-bot`
- Requests
- BeautifulSoup
- Web scraping
- LLM-based classification
- LLM-based document summarization
- Company data enrichment
- JSON storage
- Automated background monitoring

## Installation

Clone the repository:

```bash
git clone https://github.com/santaklaussus2004/TenderBOT.git
cd TenderBOT
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install python-telegram-bot python-dotenv python-dateutil requests beautifulsoup4 openai
```

## Environment Variables

Create a `.env` file and store API keys and configuration there.

Example:

```env
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
OPENAI_API_KEY=YOUR_OPENAI_API_KEY

ALLOWED_TELEGRAM_IDS=123456789

CHECK_INTERVAL_SECONDS=10800

DATA_DIR=.
BOT_STATE_DIR=.
```

Multiple Telegram users can be specified:

```env
ALLOWED_TELEGRAM_IDS=123456789,987654321
```

> Never commit API keys, Telegram tokens, passwords, or other credentials to GitHub.

Add `.env` to `.gitignore`:

```text
.env
```

## Running the Bot

Start the Telegram bot:

```bash
python tender_bot_compact.py
```

Then open the bot in Telegram and run:

```text
/start
```

The user will be registered for automatic tender notifications.

## Access Control

TenderBOT includes a Telegram whitelist.

Only Telegram accounts whose IDs are specified in:

```env
ALLOWED_TELEGRAM_IDS
```

can access protected bot functionality.

The `/id` command can be used to find the current Telegram user ID.

## Storage

The project currently uses JSON files for storing processed information.

Example files:

```text
22.09.2026.json
21.09.2026.json
21.01.2026Past.json

trash.json

telegram_subscribers.json
telegram_check_state.json
```

Daily JSON files contain processed tenders.

`trash.json` contains tenders rejected by the LLM relevance filter.

`telegram_subscribers.json` stores Telegram chats subscribed to automatic notifications.

`telegram_check_state.json` stores previously detected tenders so the bot can identify newly discovered opportunities.

## Project Structure

```text
TenderBOT/
│
├── tender_bot_compact.py
│   Telegram bot interface and automatic notifications
│
├── main2 (2).py
│   Tender scraping, winner extraction,
│   company enrichment and AI processing
│
├── llm.py
│   OpenAI API integration
│
├── main (1).py
├── main (2).py
├── main2 (1).py
├── today_bot_every_3_hours (2).py
│   Earlier / experimental versions
│
└── README.md
```

## Why TenderBOT Was Built

Public procurement contains a large number of potential business opportunities, but manually monitoring the market is time-consuming.

A typical workflow may require someone to:

```text
Find tender
    ↓
Read tender
    ↓
Check relevance
    ↓
Open documents
    ↓
Read technical specifications
    ↓
Find winner
    ↓
Research winner
    ↓
Find contacts
    ↓
Prepare outreach
```

TenderBOT automates a large part of this workflow:

```text
Tender
   ↓
AI relevance analysis
   ↓
Winner
   ↓
Contacts
   ↓
Documents
   ↓
AI summary
   ↓
Personalized outreach
   ↓
Telegram notification
```

The project combines traditional web scraping and automation with LLM-based analysis to create a practical procurement intelligence system.

## Real-World Usage

TenderBOT is not only a demonstration or educational project.

It is currently used by **AstanaTech** as part of its real tender monitoring and business development process.

The system was designed around an actual business problem: continuously discovering relevant government procurement opportunities while reducing repetitive manual research.

## Disclaimer

This project is intended for procurement monitoring, automation, and research purposes.

Users are responsible for complying with:

- applicable laws;
- external website terms of service;
- data protection requirements;
- procurement regulations;
- rules regarding commercial communications and outreach.

## Author

**Sanat Tokmagambet**

AI / ML Engineer

GitHub: [@santaklaussus2004](https://github.com/santaklaussus2004)
