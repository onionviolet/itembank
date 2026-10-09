"""Course context presentation over the existing admitted read models."""

import urllib.parse

from surfaces import presentation


def _link(href, title, css=""):
    return '<a%s href="%s">%s</a>' % (
        ' class="%s"' % presentation.esc(css) if css else '',
        presentation.esc(href), presentation.esc(title))


def prerequisite_return(path, objectives, prerequisites, course_id):
    """Only an exact currently projected prerequisite can have a return link."""
    query = urllib.parse.parse_qs(urllib.parse.urlsplit(path).query)
    origin, target = query.get('from_objective', []), query.get('to_objective', [])
    if len(origin) != 1 or len(target) != 1:
        return None
    indexes = {row['id']: i for i, row in enumerate(objectives)}
    if origin[0] not in indexes or target[0] not in indexes:
        return None
    if not any(edge['source'] == target[0]
               for edge in prerequisites.get(origin[0], [])):
        return None
    row = objectives[indexes[origin[0]]]
    return {'origin': origin[0], 'target': target[0], 'title': row.get('statement') or row['id'],
            'href': '/course/%s/map#objective-%d' % (
                urllib.parse.quote(course_id, safe=''), indexes[origin[0]])}


def objective_return(path, objectives, course_id):
    """Resolve source detours to a current objective, never a supplied URL."""
    values = urllib.parse.parse_qs(urllib.parse.urlsplit(path).query).get('return_objective', [])
    if len(values) != 1:
        return ''
    for index, row in enumerate(objectives):
        if row['id'] == values[0]:
            href = '/course/%s/map#objective-%d' % (
                urllib.parse.quote(course_id, safe=''), index)
            return '<p class="course-context-return">%s</p>' % _link(
                href, 'Return to ' + (row.get('statement') or row['id']))
    return ''


def objective_section(index, row, prerequisites, alignment, activities, back,
                      return_context=None):
    """Keep authored rationale and learning actions ahead of secondary metadata.

    Alignment, activities and back are already escaped native markup. All
    projected relation text is escaped here, and no evidence is reinterpreted.
    """
    oid = row['id']
    title = row.get('statement') or oid
    relations = []
    for edge in prerequisites:
        url = urllib.parse.urlsplit(edge['href'])
        query = urllib.parse.parse_qsl(url.query)
        query.extend((('from_objective', oid), ('to_objective', edge['source'])))
        href = urllib.parse.urlunsplit((url.scheme, url.netloc, url.path,
                                       urllib.parse.urlencode(query), url.fragment))
        relations.append(
            '<li class="course-prerequisite">%s<p class="course-prerequisite-rationale">%s</p>'
            '<p class="course-context-evidence">%s</p>'
            '<details><summary>About this prerequisite</summary>'
            '<dl><dt>Relation</dt><dd>%s</dd><dt>Confidence</dt><dd>%s</dd>'
            '<dt>Authored policy</dt><dd>%s</dd></dl>'
            '<p>This view does not restrict access.</p></details></li>' % (
                _link(href, edge['title'], 'course-prerequisite-link'),
                presentation.esc(edge['rationale'] or 'No prerequisite rationale is recorded.'),
                presentation.esc(edge['evidence']), presentation.esc(edge['authority']),
                presentation.esc(edge['confidence']), presentation.esc(edge['override'])))
    prerequisite_html = (
        '<div class="course-prerequisites"><h4>Builds on</h4><ul>%s</ul></div>' % ''.join(relations)
        if relations else '')
    returning = ''
    if return_context and return_context['target'] == oid:
        returning = '<p class="course-context-return">%s</p>' % _link(
            return_context['href'], 'Return to ' + return_context['title'])
    return (
        '<section id="objective-%d" class="course-objective" tabindex="-1" '
        'aria-labelledby="objective-title-%d">'
        '<header class="course-objective-heading"><span class="course-objective-number" '
        'aria-hidden="true">%02d</span><h3 id="objective-title-%d">%s</h3></header>%s'
        '<div class="course-objective-workspace"><div class="course-objective-context">%s'
        '<details class="course-objective-alignment"><summary>Sources and treatments</summary>%s</details>'
        '</div><div class="course-objective-activities">%s</div></div>'
        '<div class="course-objective-back">%s</div></section>' % (
            index, index, index + 1, index, presentation.esc(title), returning,
            prerequisite_html, alignment, activities, back))


def source_impact(impact, affected, readings='', treatments=''):
    """Exact current tasks are inspectable without adopting changed source bytes."""
    issues = ''.join('<li>%s</li>' % presentation.esc(issue)
                     for issue in impact.get('issues', []))
    return (
        '<aside class="course-source-impact" aria-label="Changed source impact">'
        '<h4>Source revision needs review</h4>'
        '<p>State: %s. Existing bindings and evidence remain on their recorded revisions.</p>'
        '<h4>Affected objectives</h4><ul>%s</ul>'
        '<h4>Affected current reading assignments</h4><ul>%s</ul>'
        '<h4>Affected current treatments</h4><ul>%s</ul>'
        '<p>Historical records excluded from current impact: %d reading revisions, %d binding revisions. '
        'Prior reading declarations stay on their recorded revisions and do not imply mastery.</p>'
        '%s'
        '<details><summary>Revision details</summary>'
        '<dl><dt>Accepted fingerprint</dt><dd class="mono">%s</dd>'
        '<dt>Current fingerprint</dt><dd class="mono">%s</dd></dl></details>'
        '<p>Reconcile the source revision before changing its bindings. No content was regenerated.</p>'
        '</aside>' % (
            presentation.esc(impact['state']),
            affected or '<li>No exact objective binding is recorded.</li>',
            readings or '<li>No exact current reading assignment is available.</li>',
            treatments or '<li>No current treatment binding is recorded.</li>',
            impact.get('historical_readings', 0), impact.get('historical_bindings', 0),
            '<ul aria-label="Unavailable impact links">%s</ul>' % issues if issues else '',
            presentation.esc(impact['accepted'] or 'Unavailable'),
            presentation.esc(impact['current'] or 'Unavailable within the read limit')))


def checks_details(state, markup):
    """Keep check status visible while leaving full repair detail available."""
    summary = {'clean': 'Course checks: no issues found',
               'needs-review': 'Course checks: review needed',
               'error': 'Course checks: some checks failed'}.get(state, 'Course checks: unavailable')
    return '<details class="course-map-checks"><summary>%s</summary>%s</details>' % (
        presentation.esc(summary), markup)
