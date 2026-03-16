# Platform Specifications Reference

## LinkedIn via Metricool

### Text Content
- **Character limit:** 3,000 characters per post
- **Preview truncation:** First ~210 characters visible before "see more"
- **Line breaks:** Supported. Use empty lines between paragraphs.
- **Bold/Italic:** Not supported via API text. Use **asterisks** as visual
  emphasis (they render as plain text but create visual pattern).
- **Mentions:** Use `@[Name](urn:li:person:ID)` format if tagging via API.
  Simpler to @mention in plain text and let LinkedIn resolve.

### Carousels / Images
- **Image count:** Up to 20 images per carousel post
- **Recommended dimensions:** 1080x1080px (square) or 1080x1350px (portrait)
- **File formats:** JPEG, PNG, GIF
- **File size:** Max 10 MB per image
- **PDF upload:** Supported for document carousels (preferred method — single
  file, consistent formatting). Max file size varies.
- **Image normalization:** Always run images through Metricool's normalize
  endpoint before scheduling: `POST /api/actions/normalize/image/url`

### Video
- **One video per post** (cannot mix video and images)
- **Max duration:** 10 minutes (recommended under 3 minutes)
- **File size:** Up to 5 GB
- **Formats:** MP4 preferred

### Documents
- **Supported types:** PDF, PPT, PPTX, DOC, DOCX
- **Use case:** Carousel-style content with consistent formatting
- **Advantage over images:** Better text rendering, no quality loss

### Hashtags
- **Recommended:** 3-5 per post
- **Placement:** Final line of post, separated from body by empty line
- **Mix:** 1-2 branded (#AICreativeGovernance) + 2-3 discovery (#AIStrategy,
  #CreativeLeadership, #FutureOfWork)
- **Avoid:** More than 5 (looks spammy), hashtags in body text

### Algorithm Notes
- Carousels get 6.6% average engagement (highest of any format)
- AI-generated content penalized ~47% in reach
- Posts with images get 2x engagement vs. text-only
- First 60 minutes of engagement determine distribution reach
- LinkedIn Newsletter subscribers get push notifications

## X / Twitter via Metricool

### Tweet Content
- **Character limit:** 280 characters (X Premium allows longer, but 280
  is recommended for maximum reach and retweet-ability)
- **Thread mechanics:** First tweet hooks, subsequent tweets chain as replies
- **Thread numbering:** "1/" "2/" etc. at start of each tweet
- **Link handling:** External links in main tweets reduce reach by ~50%.
  Put links in a reply to the thread instead.

### Thread Best Practices
- **Length:** 7-12 tweets optimal for engagement
- **First tweet:** Must be self-contained and hook-worthy (this is what
  gets shared). End with "🧵" or "A thread:"
- **Each tweet:** One complete thought under 280 characters
- **Final tweet:** Summary + CTA. "Follow @handle for more on [topic].
  RT tweet 1 to share."
- **Scheduling:** Schedule first tweet, then chain replies via thread API

### Images
- **Per tweet:** Up to 4 images
- **Dimensions:** Minimum 600x335px, recommended 1200x675px (16:9)
- **File formats:** JPEG, PNG, GIF (auto-play on timeline)
- **File size:** Images max 5 MB, GIFs max 15 MB
- **Alt text:** Recommended for accessibility

### Hashtags
- **Recommended:** 1-2 per tweet maximum
- **Placement:** End of tweet
- **Discovery tags only:** #AI, #Creativity, #Leadership
- **Avoid:** More than 2 (reduces engagement), branded hashtags on X
  (they work on LinkedIn, not here)

### Algorithm Notes
- Threads get 3x engagement vs. single tweets
- X Premium gives ~10x reach boost (near-mandatory)
- Content half-life is ~18 minutes
- Replies to accounts with 1K-50K followers drive follower acquisition
- X Spaces cannot be scheduled via API (manual only)

## Cross-Platform Rules

### What Changes Between Platforms

| Element | LinkedIn | X |
|---------|----------|---|
| Tone register | Professional, structured | Conversational, punchy |
| Post length | 150-300 words | 280 chars (or 7-12 tweet thread) |
| Hashtags | 3-5, branded + discovery | 1-2, discovery only |
| Emojis | 1-2 max, never in analysis | Sparingly, OK in hooks |
| Links | OK in post body | In reply only (algorithm penalty) |
| Tagging | 1-3 people max | @mention freely in replies |
| CTA style | Question or professional prompt | "RT to share" / "Follow for more" |
| Format | Paragraphs, bullet points | Short bursts, numbered threads |

### What Stays the Same
- Voice: Direct, authoritative, warm (same person, different register)
- Data attribution: Always cite sources on both platforms
- First-person POV: "I've seen...", "In my experience..."
- Pillar alignment: Same pillar, different format
- Signature phrases: Same phrases work on both platforms
