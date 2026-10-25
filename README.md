# ClearTerms

**See what you're agreeing to.**

ClearTerms is an AI-powered tool that helps people understand privacy policies and terms of service without struggling through complicated legal language. It turns lengthy documents into clear, structured explanations so users can make more informed decisions about the services they use.

## The Problem

Privacy policies and terms of service often contain lengthy paragraphs and complex language that are difficult for everyday users to understand. Important details about personal data collection, third-party sharing, data retention, and account deletion can be easy to overlook.

ClearTerms aims to make these details easier to find and understand.

## Our Solution

ClearTerms uses Google's Gemma model through the Gemini API to analyze policy text and explain important clauses in plain English, while keeping the original text available for verification.

## Features

- **Plain-English Summaries:** Understand lengthy policies through concise explanations.
- **Data Collection Analysis:** Identify what types of personal information a policy says it collects.
- **Third-Party Sharing:** Understand what the policy says about sharing information with other parties.
- **Data Retention and Deletion:** Find statements about how long information may be retained and what happens when an account is deleted.
- **Important Clause Detection:** Highlight clauses that deserve closer attention.
- **Evidence-Based Explanations:** Show relevant excerpts from the original text alongside AI-generated interpretations.
- **User-Friendly Interface:** Analyze policy text through a simple web application.

## Tech Stack

- **Language:** Python
- **Frontend:** Streamlit
- **AI:** Google Gemma through the Gemini API
- **SDK:** Google Gen AI Python SDK
- **Version Control:** Git and GitHub

## How It Works

1. Paste the text of a privacy policy or terms of service.
2. Submit the text for analysis.
3. ClearTerms uses the Gemma model to identify relevant clauses and summarize their meaning.
4. Review the structured report, including explanations and supporting excerpts.
5. Use the report to decide which parts of the policy deserve closer attention.

## Getting Started

### Prerequisites

- Python 3.10 or later, compatible with the selected dependencies
- Git
- A Google API key with access to a supported Gemma model through the Gemini API

### Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/clearterms.git
cd clearterms
```

Create and activate a virtual environment.

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS or Linux:**

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

### Configure the API Key

Set your API key as an environment variable.

**Windows PowerShell:**

```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```

**macOS or Linux:**

```bash
export GEMINI_API_KEY="your_api_key_here"
```

Never commit API keys or other secrets to GitHub.

### Run the Application

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal.

## Responsible Use

ClearTerms is an informational tool, not a substitute for legal advice.

- AI-generated interpretations may be incomplete or incorrect.
- Always verify important conclusions against the original policy.
- The absence of a clause from an analysis does not mean the policy excludes that practice.
- Risk indicators do not, by themselves, establish that a company is acting unlawfully.
- Do not submit sensitive personal information unnecessarily.

## Open Source

ClearTerms is being developed as an open-source project to make complex policy language more accessible.

Contributions, feedback, bug reports, and suggestions are welcome.

## Project Status

Built as a Hacktoberfest 2026 Hackday project. Features and implementation details may evolve as development progresses.

## License

This project is intended to be released under the MIT License. See [LICENSE](LICENSE) for the terms once the license file has been added.

