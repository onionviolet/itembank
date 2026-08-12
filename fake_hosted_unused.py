import json, sys, os
req = json.load(sys.stdin)
if len(sys.argv) > 1:
    json.dump(req, open(sys.argv[1], 'w'))
out = {'kind': 'hint_plan', 'interaction_id': req['interaction_id'],
       'focus_span': 'the wrong answer', 'fact_ids': ['tier2.trap'],
       'move': 'anchor_error'}
json.dump(out, sys.stdout)
