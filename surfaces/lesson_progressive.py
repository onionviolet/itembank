"""Progressive enhancement of runtime-approved guided lesson content."""
import resources
from surfaces.lesson_interaction import EXPLORATION_JS

CSS = resources.read_text("surfaces/assets/lesson_progressive/progressive.css")

JS = "<script>" + EXPLORATION_JS + resources.read_text("surfaces/assets/lesson_progressive/progressive.js")
