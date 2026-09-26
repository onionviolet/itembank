# Synthetic typed-answer fixture

Q1. Complete the invented flag description. Give its color and stripe count.
[TYPE: fill]
[OBJECTIVE: sample:description]
[FIELDS: [{"id":"color","label":"Color","kind":"text","accepted":["blue","azure"],"case_sensitive":false,"whitespace":"trim"},{"id":"count","label":"Stripe count","kind":"numeric","answer":"2.5","atol":"0.01"}]]
WHY BEST: The fictional flag is blue and has two and a half stripes.
KEY DISCRIMINATOR: Both fields must match their stated rule.
TRAP: A numeric answer is not a sentence.
CONFIDENCE: high

Q2. Convert the length of the fictional rod to an allowed unit.
[TYPE: fill]
[OBJECTIVE: sample:measurement]
[FIELDS: [{"id":"length","label":"Rod length","kind":"numeric","answer":"1","unit":"m","units":{"m":"1","cm":"0.01"},"atol":"0","rtol":"0"}]]
WHY BEST: The fictional rod is one metre long, equivalent to one hundred centimetres.
KEY DISCRIMINATOR: The authored conversion factors preserve the quantity.
TRAP: Include the unit with the number.
CONFIDENCE: high

Q3. Type the accented name from the fictional glossary.
[TYPE: fill]
[OBJECTIVE: sample:spelling]
[FIELDS: [{"id":"name","label":"Name","kind":"text","accepted":["café"],"case_sensitive":true,"whitespace":"exact"}]]
WHY BEST: The accent is part of the requested spelling.
KEY DISCRIMINATOR: Unicode composition is equivalent, but a missing accent is different.
TRAP: Case, spaces, and accents matter for this field.
CONFIDENCE: high
