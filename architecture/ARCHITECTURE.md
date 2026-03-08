# Rayeva AI — Architecture Overview

All four modules in the Rayeva sustainable commerce platform.

---

## Module 1: AI Auto-Category & Tag Generator (✅ Implemented)

Takes a product name + description, sends it to Gemini, gets back a structured categorization with sustainability filters and SEO tags. Results are persisted to the `products` table.

**Flow:** Frontend → `POST /api/v1/category/generate` → `category/service.py` → `ai_client.py` → Gemini → parse JSON → save to DB → return response

**Key design choices:**
- Categories are constrained to a fixed list of 10 — Gemini is instructed via system prompt to only pick from those
- Sustainability filters also constrained to a fixed list of 10
- SEO tags are freely generated (5-10 per product)
- Confidence score lets downstream systems decide whether to auto-approve or flag for human review

---

## Module 2: AI B2B Proposal Generator (✅ Implemented)

Takes company context (name, industry, budget, requirements, sustainability preferences) and generates a full procurement proposal with product recommendations, budget allocation, and environmental impact estimates.

**Flow:** Frontend → `POST /api/v1/proposal/generate` → `proposal/service.py` → `ai_client.py` → Gemini → parse JSON → save to DB → return response

**Key design choices:**
- Budget utilization is nudged to 70-95% via the prompt (realistic, not wasteful)
- Impact estimates (plastic saved, carbon avoided) are AI-generated estimates — not precise calculations
- The proposal_statement gives a human-readable summary suitable for client-facing docs
- Full generated proposal is stored as JSON blob in the `proposals` table

---

## Module 3: AI Impact Reporting (📐 Planned)

### Purpose
Generate sustainability impact reports from order/transaction data. Show businesses how much plastic, carbon, and waste they've avoided by choosing sustainable products.

### Data Requirements
- **Orders table** (new): `id, company_id, product_id, quantity, order_date`
- **Product sustainability data**: from existing `products` table (sustainability_filters, category)
- **Impact coefficients table** (new): `category, plastic_saved_per_unit_kg, carbon_saved_per_unit_kg, waste_diverted_per_unit_kg`
  - Pre-populated with reasonable estimates per product category
  - Example: "Personal Care" → 0.05 kg plastic/unit, 0.12 kg carbon/unit

### Calculation Logic
```
For each order:
  impact = quantity × coefficient_for_category

Aggregate by:
  - Time period (monthly, quarterly, annual)
  - Company
  - Product category
```

### API Design
```
POST /api/v1/impact/report
{
  "company_id": 1,
  "period": "2024-Q1"
}

Response:
{
  "total_plastic_saved_kg": 245.5,
  "total_carbon_avoided_kg": 1230.0,
  "total_waste_diverted_kg": 89.2,
  "breakdown_by_category": { ... },
  "trend_vs_previous_period": "+12%",
  "human_summary": "GreenOffice saved 245kg of plastic this quarter..."
}
```

### AI Integration
- Gemini generates the `human_summary` — a readable paragraph summarizing impact
- Could also generate comparison statements ("equivalent to X trees planted")
- The numerical calculations should NOT use AI — those should be deterministic from the coefficients

### DB Schema
```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    company_id INTEGER,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER,
    order_date DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE impact_coefficients (
    id INTEGER PRIMARY KEY,
    category VARCHAR,
    plastic_saved_per_unit FLOAT,
    carbon_saved_per_unit FLOAT,
    waste_diverted_per_unit FLOAT
);

CREATE TABLE impact_reports (
    id INTEGER PRIMARY KEY,
    company_id INTEGER,
    period VARCHAR,
    report_data TEXT,  -- JSON
    generated_summary TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## Module 4: AI WhatsApp Support Bot (📐 Planned)

### Purpose
Handle customer support via WhatsApp — order status inquiries, product questions, and escalation to human agents when the bot can't handle something.

### Integration: Twilio WhatsApp API

**Setup:**
1. Twilio account with WhatsApp sandbox (or approved business number)
2. Webhook endpoint: `POST /api/v1/whatsapp/webhook`
3. Twilio sends incoming messages to webhook, bot responds via Twilio API

**Inbound flow:**
```
Customer sends WhatsApp message
  → Twilio forwards to POST /api/v1/whatsapp/webhook
  → Parse message, load conversation history
  → Classify intent (order_status / product_question / complaint / other)
  → Handle based on intent
  → Respond via Twilio API
```

### Intent Handling

**Order Status:**
```python
# pull from orders table
order = db.query(Order).filter_by(tracking_id=extracted_id).first()
# format response: "Your order #123 is currently: Shipped. Expected delivery: March 10"
```

**Product Questions:**
- Query products table based on keywords
- Use Gemini to generate a natural-language answer from product data
- Include sustainability info in response

**Complaints / Escalation:**
- If sentiment is negative OR user explicitly asks for human → escalate
- Escalation = mark conversation as `needs_human`, notify support team
- Bot responds: "I'm connecting you with our team. Someone will respond within 2 hours."

### Conversation Logging

```sql
CREATE TABLE whatsapp_conversations (
    id INTEGER PRIMARY KEY,
    phone_number VARCHAR,
    direction VARCHAR,  -- 'inbound' or 'outbound'
    message_text TEXT,
    intent VARCHAR,
    escalated BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Escalation Logic (decision tree)
```
1. Message received
2. Check if conversation is already escalated → if yes, forward to human queue
3. Classify intent via Gemini
4. If intent = "complaint" or sentiment < 0.3 → escalate
5. If user says "talk to human" / "agent" / "help" → escalate
6. If bot has failed to answer 2+ times in same conversation → escalate
7. Otherwise → handle normally
```

### Config Requirements
```env
TWILIO_ACCOUNT_SID=xxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

### Dependencies (additional)
```
twilio
```

---

## Shared Infrastructure

All four modules share:
- **`ai_client.py`** — single Gemini wrapper with retry logic
- **`logger.py`** — all AI calls logged to `ai_logs` table
- **`database.py`** — single SQLite database, shared session management
- **`models.py`** — all SQLAlchemy models in one file (keeps it simple)

### Logging Strategy
Every Gemini API call goes through `log_ai_call()` which:
1. Saves the full prompt and response to `ai_logs`
2. Records success/failure status
3. Prints a one-line summary to console

This gives full auditability of AI behavior without any extra tooling.
