# Editor's brief

Save your own stories here as `YYYY-MM-DD.md`, named for the **morning the episode airs**
(tonight's file for Wednesday 14 October is `2026-10-14.md`). Save it before the 10:15 PM run.

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

Your **first story is the day's lead**, whatever its region: the episode opens with it ("Breaking this morning: ...") and it becomes the day's Short.

An episode has 8-9 stories of about 50-60 seconds each (under 10 minutes). Your stories
go first, in the order you list them; if you send more than 9, the extras are left out,
so put the most important first. A collected or crew story about the same event is dropped
and its outlet is added to yours as an `Also:` line. The crew only adds stories if the
total is under 8. About 120-140 words of summary per story gives 50-60 seconds of narration.

Stock-market stories (share prices, indices, trading) are not covered. Neither is election news: anything mentioning elections, voters, ballots or campaigns, even in passing, is left out, because YouTube refuses to promote videos that mention elections.

**Sundays** are the weekly round-up, built on Saturday night from the week's important stories that did *not* air Monday to Saturday (left out for length), so nothing repeats. Stories in your daily files that did not make the cut are included, if they have a link. A Sunday editor file still goes first if you want to choose the week's top stories yourself.

**Check your file after saving:** double-click `check_brief.bat` in the production folder (or run `python check_editor_brief.py`). It lists your stories, the lead, and anything that would be dropped; "OK: ready for tonight's run" means you are done. The link can go on its own line or on the Source line (`Source: Euronews https://...`).
