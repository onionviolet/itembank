# Course preparation occurrence prototype

This reversible prototype projects two activities over one real synthetic
course source and direct-reading binding. It uses Itembank's accepted personal
study-desk direction: persistent navigation, an objective-led path, editorial
source reading, local notes, Resources, evidence boundaries, recovery states,
and a focused narrow layout. Its occurrence metadata, notes, and Mark read state
exist only in browser memory. Reloading the page resets them. Nothing here is an
accepted graph or evidence format.

Build it with:

```bash
python3 prototypes/course-preparation/build_prototype.py /tmp/itembank-course-preparation
```

Then open `/tmp/itembank-course-preparation/index.html`. The generated directory
also contains the plain Markdown source. Run the focused gate with:

```bash
python3 tests/course_preparation_prototype_roundtrip.py
```

The prototype does not invoke scoring, completion evidence, imports, network
fetches, or production routes. Human touch, screen-reader, 200 percent text,
400 percent zoom, and aesthetic acceptance remain separate checks.
