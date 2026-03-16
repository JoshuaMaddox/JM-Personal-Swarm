# JM Personal Swarm

An agentic marketing team built as [Claude Code Skills](https://docs.anthropic.com/en/docs/claude-code). Five autonomous agents form a pipeline that takes a personal brand from market research through content publication — no external frameworks required.

## Architecture

```
market-research ──> brand-strategy ──> copywriter ──> brand-guardian ──> distribution
    (gather)          (decide)         (write)         (review)        (publish)
```

Each agent is a self-contained Claude Code Skill with YAML frontmatter, structured workflows, and reference files for deep-dive methodology. Agents communicate through structured markdown documents with defined section contracts.

## Skill Inventory

| # | Skill | Status | Input | Output | Description |
|---|-------|--------|-------|--------|-------------|
| 1 | `market-research` | Complete | User's niche, name, goals | 9-section Research Brief | Audience analysis, competitor intelligence, trend identification, content gap analysis, platform mapping |
| 2 | `brand-strategy` | Complete | Research Brief | 10-section Strategy Document | Positioning, content pillars, platform strategy, 4-week calendar, 90-day growth playbook, voice guide |
| 3 | `copywriter` | Complete | Strategy Document | Platform-ready content drafts | LinkedIn carousels, text posts, newsletters, X threads, tweets — all voice-matched |
| 4 | `brand-guardian` | Complete | Content draft | APPROVED / REJECTED verdict | 7-check review against positioning, voice, pillars, audience, format, ratio, red flags |
| 5 | `distribution` | Complete | Approved content | Scheduled posts via Metricool | API-driven scheduling with cadence rules, posting windows, repurpose flow |

## Quick Start

### 1. Install Skills

Copy each skill to your Claude Code skills directory:

```bash
cp -r skills/market-research ~/.claude/skills/
cp -r skills/brand-strategy ~/.claude/skills/
cp -r skills/copywriter ~/.claude/skills/
cp -r skills/brand-guardian ~/.claude/skills/
cp -r skills/distribution ~/.claude/skills/
```

### 2. Run the Pipeline

In Claude Code, use natural language to trigger each skill:

```
"Research my market in AI + Creativity"          → triggers market-research
"Build my strategy"                               → triggers brand-strategy
"Write a LinkedIn carousel for Pillar 1"          → triggers copywriter
"Review this post"                                → triggers brand-guardian
"Schedule this week's content"                    → triggers distribution
```

### 3. Configure Distribution (Metricool)

The distribution skill uses [Metricool's API](https://app.metricool.com/resources/apidocs/index.html) for scheduling. Set these environment variables:

```bash
export METRICOOL_USER_TOKEN="your-token-here"
export METRICOOL_USER_ID="your-user-id"
export METRICOOL_BLOG_ID="your-blog-id"
```

Find these in your Metricool account: **Settings > API**. Requires Advanced or Custom plan.

**MCP Alternative:** If you prefer the MCP integration, install the [official Metricool MCP server](https://github.com/metricool/mcp-metricool):

```bash
uvx mcp-metricool
```

## Pipeline Flow

### Stage 1: Market Research
- **Trigger:** "Research my market in [niche]"
- **What it does:** Launches 5 parallel research tracks (Audience, Competitors, Trends, Platforms, Content Gaps) using web search, social media analysis, and public data
- **Output:** 9-section Research Brief with confidence-tagged findings (`[verified]`, `[strong-signal]`, `[emerging]`, `[assumed]`)
- **Core principle:** "Gather, don't advise" — surfaces findings without making strategic decisions

### Stage 2: Brand Strategy
- **Trigger:** "Build my strategy" (after research is complete)
- **What it does:** Answers 5 positioning questions, defines content pillars, picks platforms, builds a 4-week calendar, designs a 90-day growth playbook, and writes a brand voice guide
- **Output:** 10-section Strategy Document consumed by all downstream agents
- **Core principle:** "Decide, don't hedge" — makes opinionated, evidence-backed commitments

### Stage 3: Copywriter
- **Trigger:** "Write a [format] about [topic]" or "Write this week's content"
- **What it does:** Produces platform-ready drafts following the voice guide, pillar constraints, and format specifications from the strategy document
- **Output:** Structured content drafts with metadata headers (platform, format, pillar, content type, word count)
- **Core principle:** "Voice fidelity above all" — every word passes the brand voice test

### Stage 4: Brand Guardian
- **Trigger:** "Review this post" or "Check this content"
- **What it does:** Runs 7 automated checks (positioning, audience, pillar, voice, ratio, format, red flags) and produces a pass/fail verdict
- **Output:** APPROVED / REJECTED / APPROVED WITH EDITS with specific feedback per check
- **Core principle:** "Protect the positioning" — nothing ships that contradicts the brand strategy

### Stage 5: Distribution
- **Trigger:** "Schedule this post" or "Set up this week's schedule"
- **What it does:** Schedules approved content via Metricool API with correct posting windows, cadence rules, and repurpose flow
- **Output:** Confirmation table with scheduled times, post IDs, and repurpose queue
- **Core principle:** "Only publish approved content" — requires Brand Guardian APPROVED status

## Skill Structure

Each skill follows the same pattern:

```
skills/{skill-name}/
├── SKILL.md              # Main skill file (<500 lines)
│   ├── YAML frontmatter  # Name, description, triggers, metadata
│   ├── Core Principles   # 5 guiding rules
│   ├── Activation Rules  # When to trigger / when NOT to
│   ├── Workflow Steps     # Sequential numbered steps
│   ├── Output Format      # Exact output template
│   ├── Quality Checklist  # Pre-delivery verification
│   └── Error Handling     # Edge cases and fallbacks
└── references/            # Deep-dive docs loaded on demand
    ├── {methodology}.md   # Detailed how-to
    ├── {frameworks}.md    # Reusable frameworks and templates
    └── {specs}.md         # Platform or API specifications
```

## Example Outputs

The `outputs/examples/` directory contains real outputs generated for the brand of Joshua Bryan Maddox (AI + Creativity Executive Thought Leadership):

- `market-research-brief-2026-03-16.md` — Complete 9-section research brief with 10 competitor profiles, 10 trend analyses, platform scorecards, and 5 high-value content gaps
- `brand-strategy-document-2026-03-16.md` — Complete 10-section strategy with positioning statement, 3 content pillars, LinkedIn/X platform strategy, 4-week content calendar, 90-day growth playbook, and brand voice guide

## Configuration

### Environment Variables

| Variable | Required By | Description |
|----------|-------------|-------------|
| `METRICOOL_USER_TOKEN` | distribution | Metricool API authorization token |
| `METRICOOL_USER_ID` | distribution | Metricool account user ID |
| `METRICOOL_BLOG_ID` | distribution | Metricool brand/blog ID |

### Runtime vs. Repository

- **Source of truth:** This GitHub repository (`skills/` directory)
- **Runtime location:** `~/.claude/skills/` (where Claude Code loads skills from)
- **Update workflow:** Edit in repo → `cp -r skills/{name} ~/.claude/skills/` → commit + push

## Built For

This pipeline was built for **Joshua Bryan Maddox** — CEPO at COTI Group, Founder of Yaru — positioned at the intersection of AI and Creativity with 18 years of creative leadership across 4 continents. The strategy targets speaking engagements via LinkedIn and X thought leadership.

While the skills are designed for this specific brand, the pipeline architecture is reusable. Fork this repo, run `market-research` with your own niche, and the downstream skills adapt to whatever strategy emerges.

## License

MIT
