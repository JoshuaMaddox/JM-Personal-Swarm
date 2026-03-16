# Scheduling Logic Reference

## Posting Windows by Platform

### LinkedIn
- **Optimal window:** 7:00–9:00 AM US Eastern, Monday–Friday
- **Peak engagement days:** Tuesday, Wednesday, Thursday
- **Newsletter:** Wednesday or Thursday, 8:00 AM ET
- **Content shelf life:** ~24 hours (algorithm resurfaces engaging posts)
- **Avoid:** Weekends (50%+ engagement drop for B2B content), after 5 PM ET

### X / Twitter
- **Threads:** 8:00–10:00 AM US Eastern (morning commute engagement)
- **Tweets:** Throughout the day, real-time conversation participation
- **Content shelf life:** ~18 minutes (fast decay, high volume needed)
- **X Spaces:** Thursday 12:00 PM ET (lunch break availability)
- **Avoid:** Late night (11 PM–6 AM ET) unless targeting Asia time zones

### Timezone Handling
- Default: Schedule all posts in US Eastern (primary audience)
- Pillar 2 content (Global Creative AI Divide): Consider secondary window
  at 8:00–10:00 AM Asia/Singapore for APAC audience
- Store all times as UTC in API calls, display as ET in confirmations

## Weekly Cadence Calendar

```
MONDAY
  7:30 AM ET  LinkedIn — Carousel (Teach)
  Throughout  X — 3-5 tweets (observations, replies)

TUESDAY
  7:30 AM ET  LinkedIn — Text Post (Teach)
  8:00 AM ET  X — Thread (repurposed from Monday's carousel)
  Throughout  X — 3-5 tweets

WEDNESDAY
  8:00 AM ET  LinkedIn — Newsletter
  Throughout  X — 3-5 tweets

THURSDAY
  7:30 AM ET  LinkedIn — Text Post (Ask)
  Throughout  X — 3-5 tweets

FRIDAY
  7:30 AM ET  LinkedIn — Text Post (Share)
  8:00 AM ET  X — Thread (repurposed from Wednesday's newsletter)
  Throughout  X — 3-5 tweets

WEEKEND
  Optional    Lightweight engagement only (replies, comments)
```

## Repurpose Flow Decision Tree

```
Source content ready?
├── LinkedIn Carousel → Wait 1 day → Extract key frames → X Thread
├── LinkedIn Text Post → Same day PM → Condense to 280 chars → X Tweet
│   └── If won't fit 280 → Convert to X Thread instead
├── LinkedIn Newsletter → Wait 2 days → Pull 7-12 key points → X Thread
└── X Thread (original) → Wait 1 day → Expand into full narrative → LinkedIn Text Post
```

**Adaptation Rules:**
- NEVER post identical text across platforms
- LinkedIn → X: Shorten, punch up, remove hashtags beyond 2, add thread numbering
- X → LinkedIn: Expand, add context, add paragraphs, add 3-5 hashtags
- Carousel → Thread: One slide ≈ one tweet, add transitions between tweets
- Newsletter → Thread: Extract the most interesting points only, not the full article

## Conflict Resolution

When two posts target the same time slot:

1. **Same platform, same time:** Move the lower-priority post 2 hours later.
   Priority order: Carousel > Newsletter > Text Post > Tweet
2. **Cross-platform, same time:** This is fine — LinkedIn and X audiences
   overlap minimally in real-time. Schedule both.
3. **Three+ posts within 1 hour on same platform:** Space them 2+ hours apart.
   Algorithm may suppress rapid-fire posting.
4. **Scheduled post conflicts with breaking news:** Hold the scheduled post.
   Post real-time reaction instead. Reschedule original for next available slot.

## Engagement Window Protocol

After each LinkedIn post goes live:
- **0–30 min:** Highest priority engagement window. Respond to every comment.
  Early engagement signals boost algorithm distribution.
- **30–60 min:** Continue responding. Like and reply to all comments.
- **1–4 hours:** Check back 2-3 times for new comments.
- **After 4 hours:** Engagement impact drops significantly. Check once more
  at end of day.

After each X thread goes live:
- **0–15 min:** Respond to early replies. Retweet if someone quote-tweets.
- **15–60 min:** Monitor engagement, respond to quality replies.
- **After 1 hour:** Engagement window mostly closed on X.

**Distribution agent should include engagement reminders in the confirmation
output for every high-priority post (carousels, threads, newsletters).**

## Batch Scheduling Protocol

When scheduling a full week of content:

1. Verify all 5+ LinkedIn posts and 2+ X threads have APPROVED status
2. Schedule LinkedIn posts first (Mon → Fri in order)
3. Schedule X threads second (Tue, Fri from repurpose)
4. Add 1-second delay between API calls to avoid rate limits
5. Verify all scheduled times in confirmation output
6. Output cadence check table (target vs. scheduled)
7. Flag any gaps in cadence (missing days, missing platforms)
