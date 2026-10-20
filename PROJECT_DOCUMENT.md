# UFC Fight Intelligence Project Document

## 1. Project Overview

This project exists to collect and analyze UFC fight and fighter data in order to generate actionable insights about future fights and to build a reliable understanding of fighter styles, strengths, weaknesses, and matchup patterns.

The project will combine:
- data collection from public online sources,
- data cleaning and normalization,
- exploratory analysis and feature engineering,
- fighter profile modeling,
- matchup analysis and future-fight insight generation,
- optional predictive modeling for outcomes and key performance indicators.

The long-term goal is not just to predict winners, but to understand why certain fighters perform the way they do and how those patterns can inform smarter betting, coaching, scouting, or sports analysis decisions.

---

## 2. Project Goals

### Primary goals
1. Build a dataset of UFC fights and fighters that is structured, reproducible, and easy to analyze.
2. Capture fighter profile information such as style, strengths, weaknesses, tendencies, and history.
3. Analyze fights and matchups to identify trends and patterns that help explain outcomes.
4. Produce actionable insights for future event analysis.
5. Explore whether fight outcomes and performance patterns can be modeled with statistical or machine learning approaches.

### Secondary goals
- Build a reusable data pipeline that can be refreshed on a schedule.
- Produce a research notebook and optional dashboard for analysis.
- Establish a clean schema that future Claude agents or team members can extend safely.
- Create a repeatable workflow for data collection, validation, and analysis.

---

## 3. Questions Captured and Decisions Made

The project was scoped using the following decisions:

- Main objective: both forecasting and fighter analysis
- Scope: all UFC fighters and events
- Data source preference: public/free sources only, with $0 budget
- Time horizon: both historical and future-facing analysis
- Final output: multiple deliverables, including data pipeline, analysis, and model experimentation
- Technical stack: Python, pandas, and scikit-learn
- Data freshness: regular refreshes, not necessarily real time
- Timeline: fast prototype over 1–2 weeks
- Success metric: research and learning first; model quality and insight quality are both prioritized
- Constraints: strict budget and maintainability matter more than a polished commercial product

These assumptions are intentionally lightweight and can be revised as the project matures.

---

## 4. Scope Definition

### In scope
- UFC events and fight cards
- Fighter metadata
- Fight results and stats
- Fighter records and career histories
- Fight-level metrics such as strikes landed, takedowns, control time, and significant events
- Fighting style patterns and matchup tendencies
- Historical trend analysis
- Future matchup insight analysis
- Predictive modeling experiments where justified by the data

### Out of scope for the initial project
- Other combat sports beyond UFC
- Private or licensed datasets unless the project later has a budget
- Real-time betting or market forecasting systems
- A polished commercialization layer or production-grade app at phase 1
- Highly advanced generative AI features or external deployed services

---

## 5. Data Requirements

### Core data entities
1. Fighter
   - name
   - nickname
   - division
   - height, weight, reach
   - age/date of birth
   - nationality
   - record
   - fight history
   - stance
   - team/training camp

2. Event
   - event date
   - location
   - venue
   - promotion
   - card structure

3. Fight
   - fighters involved
   - result
   - method of victory
   - rounds and time
   - card position
   - venue/event information

4. Fight statistics
   - significant strikes landed/attempted
   - strikes laded/attempted
   - takedowns landed/attempted
   - submission attempts
   - control time
   - knockdowns
   - accuracy percentages
   - pace and pressure indicators
   - round-by-round trend metrics

5. Derived style features
   - striker vs grappler profile
   - pressure index
   - pace index
   - grappling frequency
   - finishing rate
   - defense metrics
   - average fight duration

---

## 6. Data Sources

Because the project is budget-constrained and must use legal, ethical, and public-access data, the primary strategy should be to source data only from public sources that permit scraping or reuse for research purposes.

### Preferred source types
- Public fight databases
- Public fighter record pages
- Official UFC event pages or public metadata
- Public fighter stat pages
- Public APIs where available
- Community-maintained sports data sources with clear license terms

### Candidate data sources
Potential sources to evaluate during the first implementation phase include:
- UFC official pages and public event information
- UFCStats-style public fight statistics pages
- Tapology or similar public fight record pages
- FightMatrix or other open public matchup records
- Fighter/profile pages that provide historical results and metadata
- Custom scraping from public stat pages under robots.txt and terms-of-use compliance

### Data collection principles
- Respect robots.txt and site terms
- Prefer stable and consistent public pages
- Avoid scraping personal data or restricted content
- Log every data source and collection date
- Keep raw snapshots for reproducibility
- Maintain provenance metadata per dataset table

---

## 7. Technical Approach

### Recommended stack
- Python
- pandas for data manipulation
- scikit-learn for modeling experiments
- Jupyter notebooks for exploration and reporting
- SQLite or a local relational database for intermediate storage
- CSV exports for lightweight portability
- Optional: SQLAlchemy or DuckDB for richer local querying

### Architecture plan
1. Data acquisition layer
   - fetch raw pages or API responses
   - store raw snapshots

2. Extraction layer
   - parse HTML or API responses
   - normalize into structured records

3. Validation layer
   - audit missing values
   - check duplicates
   - validate fighter/result consistency

4. Transformation layer
   - unify naming conventions
   - merge event/fighter/fight records
   - compute derived features

5. Analysis layer
   - build notebooks forEDA and time-series analysis
   - generate fighter profiles and matchup views

6. Modeling layer
   - test prediction baselines
   - evaluate feature importance and model quality

7. Reporting layer
   - create summary charts, insights, and final results

---

## 8. Research Questions

The project should answer questions like:

- Which fighting styles are most effective against specific opponent archetypes?
- Do certain fighters consistently underperform against grapplers, strikers, or pressure fighters?
- How do finishing rates vary by division, age, and competition level?
- Which metrics best predict future success or failure?
- How do fighter archetypes change over time?
- Are there statistically meaningful patterns in win rates by style, reach, age, or weight class?
- Which underlying features correlate most strongly with fight outcomes?

---

## 9. Project Deliverables

### Phase 1: MVP dataset and analysis
- reproducible data collection scripts
- cleaned fighter and fight dataset
- simple notebook for exploratory analysis
- fighter profile summary tables
- matchup trend findings
- basic feature engineering output

### Phase 2: modeling and insight layer
- baseline outcome prediction models
- fighter style classification
- strength/weakness summaries
- event-level matchup recommendations

### Phase 3: optional decision support layer
- dashboard or interactive summary
- recurring refresh pipeline
- reusable insights report for future fights

---

## 10. Success Metrics

The project should be considered successful if it produces:

- a structured, reusable UFC dataset,
- replicable preprocessing and analysis scripts,
- a clear fighter profile framework,
- evidence-backed style and matchup insights,
- at least one meaningful predictive baseline,
- an organized set of findings that can be extended later.

Success is not defined only by prediction accuracy. The project should prioritize data quality, interpretability, and practical insight.

---

## 11. Risks and Constraints

### Data quality risks
- inconsistent naming across sources
- missing fight metric fields for older fights
- incomplete or low-quality fighter metadata
- site structure changes affecting scraping

### Methodological risks
- small sample sizes in certain divisions or categories
- data leakage when building predictive models
- overfitting to historical patterns without considering changing fighter quality
- style labels being subjective or inconsistently defined

### Operational risks
- scraping restrictions from public websites
- data source instability or outages
- poor documentation from third-party sources
- model results that look strong but are not actually actionable

### Mitigation strategy
- keep raw source data snapshots
- validate with consistency checks and sample audits
- define clear feature categories and labels
- use simple baselines before complex models
- document all assumptions and limitations explicitly

---

## 12. Proposed Workflow for Future Agents

This project should be designed so future AI agents or contributors can continue the work without reinventing the process.

### Agent workflow principles
1. Start with the data source inventory.
2. Prefer reproducible scripts over one-off notebook experiments.
3. Validate raw data before creating derived features.
4. Separate pipeline stages cleanly:
   - acquire
   - parse
   - validate
   - enrich
   - analyze
   - model
5. Keep all intermediate outputs versioned.
6. Document assumptions and limitations in every major step.
7. Prefer simple models before trying complex ones.
8. Always preserve the raw source snapshots used to build each dataset version.

### Suggested file structure
- data/raw/
- data/processed/
- notebooks/
- scripts/
- src/
- reports/
- README.md
- PROJECT_DOCUMENT.md

### Future agent protocol (draft)
A future Claude agent should follow this protocol:
1. Read the project document and project goals.
2. Review the current data source inventory and schema.
3. Check whether the requested task is data collection, cleaning, modeling, or reporting.
4. Write or update reproducible code, not ad hoc scripts.
5. Validate results against a small known-good sample.
6. Log changes to the dataset or methodology.
7. Summarize findings and limitations in plain language.
8. Propose the next step instead of jumping to a new model without evidence.

---

## 13. Initial Roadmap

### Phase 1: foundation
- confirm data sources and legal feasibility
- build raw ingestion scripts
- create schema and validation rules
- generate first fighter and fight dataset version

### Phase 2: analysis
- run EDA on fighter records and outcome distributions
- build fighter style clusters or archetype labels
- analyze matchup patterns and weakness trends

### Phase 3: modeling
- create baseline models for outcomes and key metrics
- compare feature sets
- evaluate predictive value and interpretability

### Phase 4: reporting
- summarize major findings
- produce analysis notebooks and charts
- define a repeatable refresh process

---

## 14. Recommended First Milestone

The first milestone should be modest and achievable:

- collect a historical UFC dataset covering a meaningful range of recent fights,
- clean and validate it,
- produce a fighter profile summary,
- identify a handful of style and matchup insights,
- test a basic predictive baseline,
- capture the results in a reusable notebook.

This milestone creates the foundation for all later work without overcommitting to a large or fragile system before the data quality is proven.

---

## 15. Final Positioning

This project is best framed as an applied sports analytics and research project focused on UFC data. The goal is not merely to generate a model score, but to build a durable understanding of why fighters win, lose, and evolve over time.

The most important principle is this:

Data quality, interpretability, and workflow clarity matter more than flashy modeling early on.

If the dataset is solid and the analysis is disciplined, the project can evolve naturally into deeper prediction work, richer style profiling, and better future-fight insights.

---

## 16. Appendix: Open Questions to Resolve Before Full Execution

These decisions should be revisited as the project moves forward:

- ~~Which public source will be used as the primary source of truth?~~ Resolved: the Greco1899 UFCStats CSV mirror; see [ADR 0002](docs/adr/0002-data-source.md).
- What is the minimum historical range to include?
- Do we require round-by-round stats for all fights or only recent data?
- Are all divisions included from the start, or do we begin with a subset like lightweight, middleweight, or featherweight?
- Should the first modeling attempt target binary outcomes, round predictions, or style classification?
- Is the project being evaluated primarily as research, analytics, or decision-support tooling?

---

## 17. Project Status

Status: initial project definition complete.

Current baseline assumptions:
- all UFC events and fighters as project scope,
- no budget for paid data,
- Python-based analysis stack,
- weekly or regular refresh cycle,
- prototype target within 1–2 weeks,
- emphasis on research and insight quality before heavy model optimization.

This document should be treated as the foundational operating brief for the project and should be updated when new decisions are made.
