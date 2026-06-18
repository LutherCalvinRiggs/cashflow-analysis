# Categories — cashflow-analysis

This file defines the default transaction categories. On first run, the backend seeds the `categories` table from this list. You can add, rename, or reorder categories here — the AI will use these definitions when categorizing new transactions.

---

## Default Categories

These are designed for a household budget covering two working adults with children.

```json
[
  {
    "name": "Rent",
    "description": "Monthly rent payments. Includes payments to landlords, property management companies, or rent platforms like Bilt.",
    "color": "#E24B4A"
  },
  {
    "name": "Groceries",
    "description": "Food purchased at supermarkets, warehouse stores, and specialty food shops. Includes Costco, Food Cellar, Trader Joe's, Key Food, Dumbo Market, Food Bazaar, and similar.",
    "color": "#5B9E3B"
  },
  {
    "name": "Dining",
    "description": "Restaurants, cafes, coffee shops, fast food, food delivery apps (Seamless, DoorDash, Grubhub, Uber Eats). Excludes grocery stores.",
    "color": "#D4844A"
  },
  {
    "name": "Kid Activities",
    "description": "After-school programs, weekend activities, sports, arts, and enrichment programs for children. Includes Little Ones LLC, Gantry View School, LIC Stars, Queens School of Ballet, NY Kids Club, Xanh, Goldfish Swim School, Afterschool Collective, and similar programs. Also includes registration fees and deposits for these programs.",
    "color": "#378ADD"
  },
  {
    "name": "Childcare",
    "description": "Nanny, babysitter, or au pair payments. Includes Zelle or Venmo payments to named individuals who provide regular or periodic childcare.",
    "color": "#6A5ACD"
  },
  {
    "name": "Utilities",
    "description": "Electric, gas, water, and internet bills. Includes Con Edison, National Grid, and similar utility providers.",
    "color": "#BA7517"
  },
  {
    "name": "Phone",
    "description": "Mobile phone bills. Includes Verizon, AT&T, T-Mobile, and similar carriers.",
    "color": "#BA7517"
  },
  {
    "name": "Car",
    "description": "Car loan payments, insurance, parking, tolls, and E-ZPass. Excludes ride-share (see Transport).",
    "color": "#888780"
  },
  {
    "name": "Transport",
    "description": "Ride-share (Uber, Lyft), public transit (MTA, LIRR), and taxi. Excludes car loan or insurance payments.",
    "color": "#9E7A3B"
  },
  {
    "name": "Shopping",
    "description": "General merchandise, clothing, household goods, and online retail. Includes Amazon, Target, and similar retailers.",
    "color": "#C45E9E"
  },
  {
    "name": "Travel",
    "description": "Flights, hotels, vacation rentals (Airbnb, VRBO), and travel booking platforms. Includes vacation-related spending away from home base.",
    "color": "#3BA89E"
  },
  {
    "name": "Healthcare",
    "description": "Doctor visits, dentist, pharmacy, prescriptions, health insurance premiums, and medical supplies. Includes CVS, Duane Reade, and similar.",
    "color": "#4A90E2"
  },
  {
    "name": "Subscriptions",
    "description": "Recurring digital subscriptions. Includes Netflix, Spotify, Apple, Hulu, Disney+, YouTube Premium, and similar services.",
    "color": "#7B68EE"
  },
  {
    "name": "Credit Card Payment",
    "description": "Payments made to credit card accounts to pay down the balance. These reduce credit card debt — they are not spending.",
    "color": "#555555"
  },
  {
    "name": "Savings Transfer",
    "description": "Transfers to dedicated savings accounts. Includes scheduled monthly transfers to savings, emergency funds, or activity reserves.",
    "color": "#3B6D11"
  },
  {
    "name": "Internal Transfer",
    "description": "Movement of money between the user's own accounts with no external payee. Automatically flagged by extraction — should not represent real spending.",
    "color": "#444444"
  },
  {
    "name": "Income",
    "description": "Payroll deposits, direct deposits, freelance payments, business revenue, and other incoming funds. Applies to credit transactions only.",
    "color": "#3B6D11"
  },
  {
    "name": "Taxes",
    "description": "Federal and state tax payments. Includes IRS payments, state tax authority payments, and estimated quarterly taxes.",
    "color": "#A04040"
  },
  {
    "name": "Fees & Interest",
    "description": "Bank fees, overdraft fees, wire transfer fees, and credit card interest charges.",
    "color": "#888780"
  },
  {
    "name": "Uncategorized",
    "description": "Transactions that could not be confidently assigned to any other category. Review and reassign manually.",
    "color": "#666666"
  }
]
```

---

## Customizing Categories

To change the default categories:

1. Edit this file before the first run. The database seeds from this file on startup if the `categories` table is empty.
2. To update categories after the database is already seeded, use the category management UI (available in Phase 2+) or modify the database directly.

### Adding a category

Add a new object to the JSON array with:
- `name` — short, unique label (used in the UI and by the AI)
- `description` — one or two sentences describing what belongs in this category. The more specific, the better the AI categorization.
- `color` — hex color for chart display

### Removing a category

Remove the object from the list. Transactions already assigned to that category will retain the old category name in the database — they will not be automatically re-categorized.

### Guidance for good descriptions

The AI uses the description field directly when categorizing transactions. Vague descriptions produce vague categorization. Be specific:

**Weak:** `"description": "Food and drinks"`
**Strong:** `"description": "Restaurants, cafes, coffee shops, fast food, and food delivery apps (Seamless, DoorDash, Grubhub). Excludes grocery stores."`

If you have recurring vendors that are consistently miscategorized, add them explicitly to the relevant category's description.
