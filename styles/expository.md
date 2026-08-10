# Style: Expository (the content parent)

The classic textbook chapter: headed sections, definitions, prose
exposition, worked examples, and end-of-section practice. It is the base
every other shipped style is a delta from (ROADMAP 3a), it costs zero new
blocks, and it is the honest fallback for an unstyled bank. Machine
inheritance is exactly one level: house applies by default, so this file
declares no `[STYLE-PARENT:]` directive (D-10).

## Voice

Write for rereading and print: headed sections, definitions before their
uses, prose that survives being skimmed. One idea per section; something
checks what was read -- at least one `[!KEY]` per section, and items that
test the objective. Do not gate the prose: an expository lesson is a lookup
and a reread surface, not a lock-step loop.

## Rules

| id | kind | params | severity | lock | prompt |
|----|------|--------|----------|------|--------|
| section.idea | density.max | idea, 1 | warn | | no |
| keyed.practice | style.require | [!KEY], 1 | warn | | yes |
| example.then.key | order.before | [!EXAMPLE], [!KEY] | warn | | no |
| open.calm | open.with | prose | warn | | no |

## Exemplar

### Reading a rhythm strip

A rhythm strip is a timed record of the heart's electrical activity. It
shows one idea: how to identify the pacemaker. Read the example below,
then test yourself with the keyed practice item that follows.

> [!KEY] The pacemaker is the structure that initiates each beat; its
> site names the rhythm (sinus, atrial, junctional, ventricular).
