# Editor's brief

Save your own stories here as `YYYY-MM-DD.md`, named for the **day the episode airs** at 9:30 PM
(Wednesday 14 October's file is `2026-10-14.md`). Save it before the 7:00 PM run.

Use the usual brief format. Every story needs a `Source:` line and a link:

```
# WORLD

### Headline of the story
Source: Outlet name
https://link-to-the-article
Also: Second outlet https://second-link

One or two paragraphs summarising the story.

# USA

### Next headline
...
```

Regions: `WORLD`, `USA`, `CHINA`, `ASIA`, `INDIA`.

Your **first story is the day's lead**, whatever its region: it is the first headline in the opening, the first story told, and the day's Short.

An episode has 8-10 news stories of about 40-55 seconds each, plus a research story (under 10 minutes). Your stories
go first, in the order you list them; if you send more than 10, the extras are left out,
so put the most important first. A collected or crew story about the same event is dropped
and its outlet is added to yours as an `Also:` line. The crew only adds stories if the
total is under 8. About 110-130 words of summary per story gives 50-55 seconds of narration.

**Research Watch (10 + 1):** after the news stories, each episode closes with one AI research
story, the most upvoted paper on Hugging Face Daily Papers that day (30+ upvotes), about 40 seconds.
You don't write it, and it never takes one of your 10 places. There is none on days with no
well-upvoted paper (usually Saturday), or when your brief already cites an arXiv paper.

**Research of the Week (Sundays):** the round-up closes with a longer explainer, about two minutes,
of the week's most upvoted paper that has not aired yet (the most upvoted one if all have aired).
It is told from the paper's abstract, introduction and conclusion: the problem, what the
researchers built, what they found. Papers are left out of the round-up's 10 news places.

Stock-market stories (share prices, indices, trading) are not covered. Neither is election news: anything mentioning elections, voters, ballots or campaigns, even in passing, is left out, because YouTube refuses to promote videos that mention elections.

**Sundays** are the weekly round-up, built on Saturday night from the week's important stories that did *not* air Monday to Saturday (left out for length), so nothing repeats. Stories in your daily files that did not make the cut are included, if they have a link. A Sunday editor file still goes first if you want to choose the week's top stories yourself.

**Check your file after saving:** double-click `check_brief.bat` in the production folder (or run `python check_editor_brief.py`). It lists your stories, the lead, and anything that would be dropped; "OK: ready for tonight's run" means you are done. The link can go on its own line or on the Source line (`Source: Euronews https://...`).
