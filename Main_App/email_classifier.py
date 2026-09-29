import os
import json
import re
from datetime import datetime

# Toggle AI ON/OFF
USE_AI = os.environ.get("CLAUDE_API_KEY") is not None

def extract_deadline(text):
    """Try to extract deadline dates from email text"""
    patterns = [
        r'by\s+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
        r'before\s+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
        r'deadline[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
        r'last date[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
        r'due[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
        r'register by\s+(\w+ \d{1,2},?\s*\d{0,4})',
        r'apply by\s+(\w+ \d{1,2},?\s*\d{0,4})',
        r'(\d{1,2}\s+\w+\s+\d{4})',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None

def generate_summary(subject, priority, reason_type):
    """Generate a meaningful one-line summary"""
    summaries = {
        'placement': f"Action required: {subject}",
        'internship': f"Internship opportunity: {subject}",
        'interview': f"Interview scheduled: {subject}",
        'exam': f"Exam notice: {subject}",
        'result': f"Results available: {subject}",
        'fee': f"Fee payment required: {subject}",
        'scholarship': f"Scholarship update: {subject}",
        'hall_ticket': f"Download hall ticket: {subject}",
        'event': f"Upcoming event: {subject}",
        'workshop': f"Workshop registration: {subject}",
        'library': f"Library notice: {subject}",
        'default': subject if len(subject) < 80 else subject[:77] + "..."
    }
    return summaries.get(reason_type, summaries['default'])

def rule_based_classification(subject, sender, body):
    text = (subject + " " + sender + " " + body).lower()
    subject_lower = subject.lower()
    sender_lower = sender.lower()

    # Extract deadline
    deadline = extract_deadline(text)

    # ---- CRITICAL ----
    critical_keywords = {
        'placement': ['placement drive', 'campus drive', 'campus recruitment', 'on-campus'],
        'internship': ['internship offer', 'internship opportunity', 'summer internship', 'winter internship'],
        'interview': ['interview schedule', 'interview call', 'hr interview', 'technical interview', 'final round'],
        'job': ['job offer', 'offer letter', 'joining letter', 'appointment letter'],
        'shortlist': ['shortlisted', 'selected candidates', 'you have been selected'],
        'test': ['aptitude test', 'online assessment', 'coding test', 'hackerrank', 'amcat', 'cocubes'],
        'company': ['infosys', 'tcs', 'wipro', 'accenture', 'cognizant', 'capgemini', 'deloitte', 'amazon', 'google', 'microsoft'],
    }

    for reason_type, keywords in critical_keywords.items():
        if any(kw in text for kw in keywords):
            return {
                "priority": "CRITICAL",
                "summary": generate_summary(subject, "CRITICAL", reason_type),
                "deadline": deadline,
                "reason": f"Placement/Career related — {reason_type}"
            }

    # Sender-based critical detection
    critical_senders = ['placement', 'tpo', 'career', 'recruitment', 'hr@', 'jobs@']
    if any(s in sender_lower for s in critical_senders):
        return {
            "priority": "CRITICAL",
            "summary": generate_summary(subject, "CRITICAL", "placement"),
            "deadline": deadline,
            "reason": "Email from Placement/TPO office"
        }

    # ---- HIGH ----
    high_keywords = {
        'exam': ['exam schedule', 'examination', 'end semester', 'mid semester', 'internal assessment', 'ia1', 'ia2', 'university exam'],
        'result': ['result declared', 'marks released', 'grade card', 'marksheet', 'result out'],
        'hall_ticket': ['hall ticket', 'admit card', 'roll number slip'],
        'fee': ['fee deadline', 'fee payment', 'last date to pay', 'dues pending', 'fee defaulter', 'tuition fee'],
        'scholarship': ['scholarship', 'financial aid', 'stipend'],
        'backlog': ['backlog', 're-examination', 'kte', 'atkt', 're-evaluation', 'revaluation'],
        'attendance': ['attendance shortage', 'attendance below', 'detained', 'not eligible'],
    }

    for reason_type, keywords in high_keywords.items():
        if any(kw in text for kw in keywords):
            return {
                "priority": "HIGH",
                "summary": generate_summary(subject, "HIGH", reason_type),
                "deadline": deadline,
                "reason": f"Academic important — {reason_type}"
            }

    # Sender-based high detection
    high_senders = ['exam', 'examination', 'finance', 'accounts', 'academic', 'registrar', 'controller']
    if any(s in sender_lower for s in high_senders):
        return {
            "priority": "HIGH",
            "summary": generate_summary(subject, "HIGH", "exam"),
            "deadline": deadline,
            "reason": "Email from Academic/Finance office"
        }

    # ---- MEDIUM ----
    medium_keywords = {
        'event': ['cultural fest', 'techfest', 'annual day', 'sports day', 'hackathon', 'competition'],
        'workshop': ['workshop', 'training program', 'certification course', 'bootcamp'],
        'seminar': ['seminar', 'guest lecture', 'expert talk', 'webinar', 'conference'],
        'club': ['club registration', 'committee', 'student council', 'nss', 'ncc'],
        'library': ['library', 'book return', 'library fine', 'new books'],
        'notice': ['important notice', 'circular', 'announcement', 'notice board'],
    }

    for reason_type, keywords in medium_keywords.items():
        if any(kw in text for kw in keywords):
            return {
                "priority": "MEDIUM",
                "summary": generate_summary(subject, "MEDIUM", reason_type),
                "deadline": deadline,
                "reason": f"Event/Notice — {reason_type}"
            }

    # ---- LOW (Promotional/Spam) ----
    low_keywords = [
        'sale', 'discount', 'offer', 'deal', 'cashback', 'coupon',
        'unsubscribe', 'newsletter', 'subscribe', 'marketing',
        'congratulations you won', 'click here to claim',
        'limited time', 'free trial', 'upgrade your plan',
        'linkedin', 'naukri', 'indeed', 'internshala alert',
        'swiggy', 'zomato', 'amazon', 'flipkart', 'myntra'
    ]
    if any(kw in text for kw in low_keywords):
        return {
            "priority": "LOW",
            "summary": subject if len(subject) < 80 else subject[:77] + "...",
            "deadline": None,
            "reason": "Promotional or subscription email"
        }

    # ---- Default ----
    # If subject has urgent words, bump to MEDIUM
    if any(word in subject_lower for word in ['urgent', 'important', 'action required', 'reminder', 'alert']):
        return {
            "priority": "HIGH",
            "summary": f"Urgent: {subject}",
            "deadline": deadline,
            "reason": "Marked as urgent"
        }

    return {
        "priority": "LOW",
        "summary": subject if len(subject) < 80 else subject[:77] + "...",
        "deadline": None,
        "reason": "General information email"
    }


def ai_classification(subject, sender, body):
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ.get("CLAUDE_API_KEY"))

    prompt = f"""You are an email classifier for an Indian university student management system.

Classify this email into exactly one priority level:

CRITICAL — placement drives, campus recruitment, job offers, internships, interview calls, aptitude tests, shortlist notifications, offer letters
HIGH — exam schedules, results, hall tickets, fee deadlines, scholarship updates, attendance shortage, backlogs, re-evaluation
MEDIUM — workshops, seminars, guest lectures, club events, fests, hackathons, library notices, circulars
LOW — promotional emails, newsletters, subscription updates, social media notifications, shopping offers

Email:
Subject: {subject}
Sender: {sender}
Body: {body[:800]}

Rules:
- If deadline is mentioned, extract it
- Generate a helpful one-line action summary
- Be specific in the reason

Respond ONLY with valid JSON, no markdown, no extra text:
{{
  "priority": "CRITICAL or HIGH or MEDIUM or LOW",
  "summary": "one line action summary for student",
  "deadline": "extracted deadline or null",
  "reason": "specific reason for this priority"
}}"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )

    text = message.content[0].text.strip()

    # Clean markdown if present
    if "```" in text:
        text = re.sub(r'```json|```', '', text).strip()

    return json.loads(text)


def classify_email(subject, sender, body):
    """Main classification function — tries AI first, falls back to rule-based"""
    if USE_AI:
        try:
            return ai_classification(subject, sender, body)
        except Exception as e:
            print(f"AI classification failed: {e}, using rule-based fallback")

    return rule_based_classification(subject, sender, body)