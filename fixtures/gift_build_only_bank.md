# GIFT build-only fixture (synthetic)

Ten-plus synthetic `build` (ordering) items and nothing else. Every item lints clean:
a distinct stem, a distinct valid step sequence, and a WHY BEST field. `build` has no
GIFT equivalent (D-02), so exporting this bank exercises the zero-exported case -- a
long run of per-item console rows and a GIFT file with no question in it. Subject
matter is deliberately generic, everyday, and unrelated to any real course; no real
question bank belongs in this repository.

Q1. Put the steps of brewing a pot of tea in order.
[TYPE: build]

STEP) Boil water in a kettle
STEP) Warm the teapot with a splash of the hot water
STEP) Add loose tea to the warmed pot
STEP) Pour the boiling water over the tea
STEP) Steep for the recommended time, then pour

WHY BEST: Warming the pot first keeps the water at brewing temperature instead of losing heat to a cold vessel, and steeping happens only after the leaves and water are together.

TRAP: Adding the tea leaves after pouring the water, which under-extracts the first cup.

CONFIDENCE: high

Q2. Put the steps of planting a seedling in a garden bed in order.
[TYPE: build]

STEP) Dig a hole slightly larger than the root ball
STEP) Loosen the roots gently if they are pot-bound
STEP) Set the seedling in the hole at its original soil depth
STEP) Backfill with soil and press down lightly
STEP) Water thoroughly right after planting

WHY BEST: The hole and loosened roots have to exist before the seedling can be set in them, and the plant needs to be anchored by backfilled soil before the first watering settles it in.

TRAP: Watering before backfilling, which just floods an empty hole.

CONFIDENCE: high

Q3. Put the steps of mailing a letter in order.
[TYPE: build]

STEP) Write the letter
STEP) Fold it and place it in an envelope
STEP) Address the envelope
STEP) Affix postage
STEP) Drop it in a mailbox

WHY BEST: Each step needs the product of the one before it -- there is nothing to fold until the letter is written, nowhere to address until it is in an envelope, and no reason to mail an envelope that carries no postage.

TRAP: Affixing postage before the envelope is addressed, which is easy to do out of habit but does not itself block delivery -- it is still out of the causal order this item is testing.

CONFIDENCE: high

Q4. Put the steps of changing a flat car tire in order.
[TYPE: build]

STEP) Loosen the lug nuts before jacking up the car
STEP) Raise the car with the jack
STEP) Remove the lug nuts and the flat tire
STEP) Mount the spare tire
STEP) Lower the car and fully tighten the lug nuts

WHY BEST: Loosening the lug nuts has to happen while the wheel still has the car's weight on it, or the wheel simply spins; everything else follows the tire's own removal-and-replacement order.

TRAP: Trying to loosen the lug nuts after the car is already jacked up, which is the single most common ordering mistake with this task.

CONFIDENCE: high

Q5. Put the steps of baking a loaf of yeast bread in order.
[TYPE: build]

STEP) Mix flour, water, yeast, and salt into a dough
STEP) Knead the dough until smooth
STEP) Let the dough rise in a covered bowl
STEP) Shape the risen dough into a loaf
STEP) Bake the shaped loaf in a hot oven

WHY BEST: Kneading develops the gluten the rise depends on, the rise has to finish before the dough can be shaped without deflating it, and baking is the last step because heat is what fixes the final shape.

TRAP: Shaping the dough before it has risen, which produces a dense loaf instead of an airy one.

CONFIDENCE: high

Q6. Put the steps of assembling a flat-pack bookshelf in order.
[TYPE: build]

STEP) Lay out all panels and hardware, and check the parts list
STEP) Attach the side panels to the base
STEP) Attach the back panel
STEP) Add the shelves
STEP) Stand the bookshelf upright

WHY BEST: Checking the parts first avoids discovering a missing screw mid-assembly, the frame (sides, base, back) has to exist before shelves can be inserted into it, and standing it up only makes sense once it can hold its own shape.

TRAP: Standing the shelf upright before the back panel is attached, which leaves it too flexible to hold square.

CONFIDENCE: high

Q7. Put the steps of doing a load of laundry in order.
[TYPE: build]

STEP) Sort clothes by color and fabric
STEP) Load the sorted clothes into the washing machine
STEP) Add detergent and start the wash cycle
STEP) Move the wet clothes to the dryer
STEP) Fold the dried clothes

WHY BEST: Sorting happens before loading so the wrong items never go into the machine together, and each later step operates on whatever the previous step produced -- wet clothes, then dried clothes, then folded clothes.

TRAP: Adding detergent before the clothes are loaded, which is a common shortcut that does not actually change the outcome but is still out of the order this item asks for.

CONFIDENCE: high

Q8. Put the steps of a basic tooth-brushing routine in order.
[TYPE: build]

STEP) Wet the toothbrush
STEP) Apply toothpaste to the bristles
STEP) Brush all tooth surfaces for two minutes
STEP) Rinse the mouth with water
STEP) Rinse the toothbrush and set it to dry

WHY BEST: The brush has to carry toothpaste before brushing does any good, and rinsing the mouth is what ends the brushing itself, before the brush is put away.

TRAP: Rinsing the mouth before brushing is finished, which cuts the two minutes short.

CONFIDENCE: high

Q9. Put the steps of filing a paper expense report in order.
[TYPE: build]

STEP) Collect all receipts for the reporting period
STEP) Sort receipts by category
STEP) Total each category on the report form
STEP) Attach the receipts to the completed form
STEP) Submit the form to the approver

WHY BEST: Totals cannot be computed before the receipts are sorted into categories, and nothing can be attached to a form that has not yet been filled in.

TRAP: Submitting the form before receipts are attached, which is the failure this whole ordering is meant to prevent.

CONFIDENCE: high

Q10. Put the steps of watering a container garden in order.
[TYPE: build]

STEP) Check the soil moisture with a finger test
STEP) Fill a watering can
STEP) Water at the base of each plant until it drains from the bottom
STEP) Empty any standing water from the saucer
STEP) Check for wilted or yellowing leaves

WHY BEST: The moisture check decides whether watering is even needed, the can has to be filled before it can be used, and the drainage check has to follow the watering it is checking the result of.

TRAP: Watering on a fixed schedule without the moisture check, which is exactly what this ordering is testing against.

CONFIDENCE: high

Q11. Put the steps of setting up a tent at a campsite in order.
[TYPE: build]

STEP) Clear the ground of rocks and sticks
STEP) Lay out the tent footprint
STEP) Assemble the tent poles
STEP) Thread the poles through the tent body and raise it
STEP) Stake down the corners and guy lines

WHY BEST: A cleared, flat footprint has to exist before anything is laid on it, and the poles have to be assembled and threaded before the tent can be raised into a shape that staking then holds in place.

TRAP: Staking the tent down before it is raised, which anchors nothing because the tent has no shape yet.

CONFIDENCE: high
