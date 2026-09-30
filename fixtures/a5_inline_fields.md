# Synthetic inline fields

Q1. The invented flag is {{color}} and has {{count}} stripes.
[ID: a448715ccfec408a]
[HASH: sha256:0549fd67d75a706c]
[TYPE: fill]
[OBJECTIVE: synthetic:inline-fields]
[FILL-LAYOUT: inline]
[FIELDS: [{"id":"count","label":"Stripe count","kind":"numeric","answer":"2.5"},{"id":"color","label":"Flag color","kind":"text","accepted":["blue"],"case_sensitive":false,"whitespace":"trim"}]]
WHY BEST: The invented description names blue and two and a half stripes.
KEY DISCRIMINATOR: Match each field to its own label and sentence position.
TRAP: Do not exchange the color and numeric field.
CONFIDENCE: high
