Here are 10 investigative questions a local NYC journalist could pursue with this knowledge graph:

---

**1. Which landlords have the highest ratio of "rent-impairing" violations — and are they still collecting rent?**
The `Violation` nodes have a `rent_impairing` field. A landlord collecting rent on buildings with uncorrected rent-impairing violations may be violating tenant protections. Cross-referencing portfolios could reveal serial offenders.

**2. Which buildings have had the same violations cited repeatedly — never corrected, just re-issued?**
By comparing violation descriptions and issue dates on the same BBL over time, you could identify "zombie violations" that cycle through the system without ever being fixed — a sign of regulatory failure or deliberate neglect.

**3. Are there neighborhoods where complaint rates are high but violation findings are low — suggesting under-enforcement?**
Complaints (`FILED_AGAINST` buildings) don't always result in `Violation` nodes. A gap between complaints filed and violations issued in a specific neighborhood could point to inconsistent inspection practices or resource gaps at HPD.

**4. How long does it take from a complaint being filed to a violation being issued — and does that lag vary by borough?**
The `Complaint.created_date` and `Violation.nov_issued_date` fields could reveal whether tenants in some boroughs wait significantly longer for enforcement action than others.

**5. Which buildings have active Class C (immediately hazardous) violations and are still occupied?**
`Violation.class` = "C" represents the most serious HPD violations — things like no heat in winter, lead paint, or structural danger. A list of buildings with open Class C violations and active complaints would be a powerful public safety story.

**6. Are landlords who receive DOB violations for facade failures (LL6291/FISP) also ignoring tenant-facing HPD violations?**
Landlord 911741's portfolio showed heavy facade inspection non-compliance. Do those same portfolios also have open HPD violations? A "dual neglect" pattern — ignoring both structural safety and tenant conditions — is a compelling narrative.

**7. Which community boards have the most unresolved violations per building — and does that correlate with income or demographics?**
Buildings have a `community_board` field. Mapping violation density by community board and overlaying public census data could reveal whether enforcement outcomes differ by neighborhood wealth or demographics.

**8. Has the volume of heat and hot water complaints spiked in recent winters — and in which zip codes?**
Heat/hot water was the #1 complaint type (19,643 cases). Filtering by `created_date` and `zip` could reveal whether certain landlords or neighborhoods are chronic cold-weather offenders, especially relevant given NYC's right-to-heat laws.

**9. Which landlords purchased buildings recently and immediately accumulated violations — a "predatory equity" pattern?**
`Registration.last_registration_date` could proxy for recent acquisition. If violations cluster shortly after a registration date changes, it may signal a new owner cutting maintenance costs after purchase — a known displacement tactic.

**10. Are buildings with DOB elevator violations also generating tenant complaints about elevator service — and which buildings have the longest-running unresolved cases?**
DOB elevator filing violations (`FTF-EN` codes) don't always show up in tenant-facing complaints. But where they overlap — buildings with both DOB elevator violations *and* complaints — residents may be living with dangerous, unverified equipment. In high-rise buildings, this is a serious safety story.

---

Each of these is answerable with the existing graph using Cypher queries — want me to run any of them?