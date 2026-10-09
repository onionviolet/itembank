"""Native ordinary-package union-copy forms with explicit scope consent.

The daemon supplies loopback/origin admission and renders this fragment in
its shared shell. Existing package, workspace, journal and evidence owners
remain authoritative. No published JSON grammar or root enrollment is added.
"""
import shlex

from surfaces import course_ops, presentation


def _one(fields, name):
    value = fields.get(name, "")
    if isinstance(value, list):
        if len(value) != 1:
            raise ValueError("Choose one value for each restore field.")
        value = value[0]
    if not isinstance(value, str):
        raise ValueError("Restore fields must contain text.")
    return value


def apply(root, fields, actor_kind="human", actor_name="local learner"):
    """Apply a native preview, explicit restore or cancellation form."""
    operation = _one(fields, "operation")
    selection = {"package_id", "source_choice", "destination_root", "destination_name"}
    permitted = {
        "preview": selection,
        "restore": selection | {"expected_package_fingerprint", "expected_source_fingerprint",
                                "expected_scope_fingerprint", "confirm_copy", "confirm_private"},
        "cancel": set(),
    }
    if operation not in permitted or set(fields) - permitted[operation] - {"operation"}:
        raise ValueError("Unsupported restore action or form field.")
    if operation == "cancel":
        return {"status": "canceled", "next_action": "Nothing was copied. The source and package remain intact."}
    args = [root] + [_one(fields, name) for name in
                     ("package_id", "source_choice", "destination_root", "destination_name")]
    if operation == "preview":
        return course_ops.preview_merged_restore(*args)
    return course_ops.apply_merged_restore(
        *args, *[_one(fields, name) for name in
                 ("expected_package_fingerprint", "expected_source_fingerprint", "expected_scope_fingerprint")],
        confirm_copy=_one(fields, "confirm_copy") == "yes",
        confirm_private=_one(fields, "confirm_private") == "yes",
        actor_kind=actor_kind, actor_name=actor_name)


def panel(root, result=None, retained=None, action_url="/restore"):
    """Script-free controls and exact scope, loss, privacy and recovery copy."""
    esc = presentation.esc
    retained = retained or {}
    choices = course_ops.restore_choices(root)

    def hidden(name, value):
        return '<input type="hidden" name="%s" value="%s">' % (esc(name), esc(str(value)))

    def retained_value(name):
        value = retained.get(name, "")
        if isinstance(value, list):
            value = value[0] if value else ""
        return value if isinstance(value, str) else ""

    def selected(name, value):
        return ' selected' if retained_value(name) == str(value) else ''

    def form(operation, body, label, url=None):
        return '<form method="post" action="%s">%s%s<button class="go">%s</button></form>' % (
            esc(url or action_url), hidden("operation", operation) if operation else "", body, esc(label))

    def separate_workspace_help(result):
        if result.get("direct_course_reopen"):
            return ('<p>Open this exact ordinary course folder in a separate local process:</p><pre>%s</pre>' %
                    esc("itembank daemon " + shlex.quote(result["destination"]) + " --port 0"))
        return ('<p>This copy carries a machine-local workspace record. Review its '
                'approved-root references before broader navigation, since they can '
                'still point at the originals. Use the exact read-only snapshot below.</p>')

    def reopen_form(result):
        body = ''.join(hidden(name, result[name]) for name in
                       ("destination_root", "destination_name", "course_object_id", "course_fingerprint"))
        body += hidden("destination_device", result["destination_identity"][0])
        body += hidden("destination_inode", result["destination_identity"][1])
        return form(None, body, "Open this exact recovered course snapshot", "/restore/open")

    out = ['<style>.restore-workspace{min-width:0}.restore-workspace code,'
           '.restore-workspace dd{overflow-wrap:anywhere}.restore-workspace pre{'
           'white-space:pre-wrap;overflow-wrap:anywhere}.restore-workspace label{'
           'display:block;margin:12px 0}.restore-workspace select,'
           '.restore-workspace input:not([type=checkbox]){max-width:100%;width:100%;box-sizing:border-box}'
           '.restore-workspace button{max-width:100%;white-space:normal}</style>',
           '<section class="restore-workspace" aria-labelledby="restore-title">',
           '<h2 id="restore-title">Restore scope</h2>',
           '<p>Copy an ordinary package and one approved source into a fresh folder. '
           'The original stays intact. All files in the source are copied, including '
           'private notes, local history and unregistered files. Nothing leaves this device.</p>']
    if result:
        if result.get("status") == "error":
            out.append('<p role="alert">%s: %s</p><p>%s</p>' % (
                esc(result.get("code", "Restore refused")), esc(result.get("message", "")),
                esc(result.get("next_action", "Preserve the original and destination, resolve the named problem and preview again."))))
        else:
            out.append('<p role="status">%s. %s</p>' % (
                esc("Recovery copy ready" if result["status"] == "recovery_ready" else result["status"]),
                esc(result.get("next_action", ""))))
    if result and result.get("status") == "recovery_ready":
        out.append('<h2>Validated recovery copy</h2><p>Exact destination: <code>%s</code></p>'
                   '<p>Preserved course identity: <code>%s</code></p>' % (
                       esc(result["destination"]), esc(result["course_object_id"])))
        out.append(separate_workspace_help(result))
        out.append(reopen_form(result))
        out.append('<p>This snapshot reads the recovered course without enrolling a duplicate. '
                   'Full learning and review navigation require a separately opened recovered workspace.</p>'
                   '<p>After checking that no later work depends on it, move only the named new '
                   'destination to trash. Keep the original and package.</p>')
    if result and result.get("status") in ("preview", "restored"):
        out.append('<dl><dt>Exact package</dt><dd><code>%s</code></dd>'
                   '<dt>Course identity</dt><dd><code>%s</code></dd>'
                   '<dt>Entire copied source</dt><dd><code>%s</code></dd>'
                   '<dt>Exact new destination</dt><dd><code>%s</code></dd>'
                   '<dt>Copied source scope</dt><dd>%s entries, %s bytes</dd></dl>' % (
                       esc(result["package_path"]), esc(result["course_object_id"]),
                       esc(result["source"]), esc(result["destination"]),
                       result["source_entries"], result["source_bytes"]))
        out.append('<details open><summary>Copied private and unregistered files (%d)</summary>'
                   '<p>Every unregistered file is treated as private for this copy. '
                   'This includes local control and history files.</p><ul>%s</ul></details>' % (
                       len(result["private_files"]), ''.join('<li><code>%s</code></li>' % esc(path)
                                                            for path in result["private_files"])))
        out.append('<details><summary>All copied source files (%d)</summary><ul>%s</ul></details>' % (
            len(result["source_files"]), ''.join('<li><code>%s</code></li>' % esc(path)
                                                 for path in result["source_files"])))
        out.append('<h2>Package losses</h2><pre>%s</pre><p>%s</p>' % (
            esc(result["loss_report_text"]), esc(result["rights_basis"])))
        references = result.get('workspace_references') or {}
        if references.get('state') == 'preview':
            out.append('<details open><summary>Workspace reference proposal</summary>'
                       '<p>This preview grants no new access and changes no references.</p><ul>')
            for row in references['roots']:
                proposed = ('Proposed copy location: <code>%s</code>' % esc(row['proposed'])
                            if row['state'] == 'remap' else 'External root would remain disabled until explicitly reapproved.')
                out.append('<li>Current root: <code>%s</code>. %s</li>' % (esc(row['original']), proposed))
            out.append('</ul><p>%d course reference(s) would need external-root reapproval.</p>'
                       '<p>%s</p></details>' % (len(references['disabled_courses']), esc(references['next_action'])))
        if result["status"] == "preview":
            body = ''.join(hidden(name, result[name]) for name in
                           ("package_id", "source_choice", "destination_root", "destination_name"))
            body += ''.join(hidden("expected_" + name, result[name]) for name in
                            ("package_fingerprint", "source_fingerprint", "scope_fingerprint"))
            body += ('<label><input type="checkbox" name="confirm_copy" value="yes" required> '
                     'Copy this entire named source and package into this exact fresh destination.</label>'
                     '<label><input type="checkbox" name="confirm_private" value="yes" required> '
                     'Include every listed private and unregistered file in this local copy.</label>')
            out.append(form("restore", body, "Create validated copy"))
            out.append(form("cancel", "", "Cancel restore"))
        else:
            out.append('<p>Validated course file: <code>%s</code></p>' % esc(result["course_path"]))
            out.append('<p>The copied course keeps its identity. It has not been enrolled '
                       'alongside the original.</p>')
            out.append(separate_workspace_help(result))
            out.append('<p>%s</p>' % esc(result["undo"]))
            out.append(reopen_form(result))
            out.append('<p>The snapshot below opens without enrolling a duplicate. Full interactive '
                       'navigation in a separate recovered workspace remains unavailable here.</p>')
    if result and result.get("status") == "reopened":
        doc = result["course_view"]
        out.append('<h2>Recovered course</h2><p>%s</p><p>Exact destination: <code>%s</code></p>'
                   '<p>Preserved course identity: <code>%s</code></p><ul>%s</ul>' % (
                       esc(doc["header"].get("title", result["course_object_id"])), esc(result["destination"]),
                       esc(result["course_object_id"]), ''.join('<li>%s</li>' % esc(row.get("statement", row["id"]))
                                                               for row in doc.get("objectives", []))))
    package_options = ''.join('<option value="%s"%s>%s</option>' % (
        esc(pid), selected("package_id", pid), esc(pid)) for pid in choices["packages"])
    source_options = ''.join('<option value="%s"%s>%s</option>' % (
        esc(row["value"]), selected("source_choice", row["value"]), esc(row["label"]))
                             for row in choices["sources"])
    root_options = ''.join('<option value="%d"%s>%s</option>' % (
        index, selected("destination_root", index), esc(path))
                           for index, path in enumerate(choices["roots"]))
    if not package_options:
        out.append('<p>No packages in the existing approved package namespace. '
                   'Export an ordinary course package first. This form cannot authorize another path.</p>')
    else:
        body = ('<label>Existing package<select name="package_id" required>%s</select></label>'
                '<label>Entire source to copy<select name="source_choice" required>%s</select></label>'
                '<label>Approved destination root<select name="destination_root" required>%s</select></label>'
                '<label>Fresh folder name<input name="destination_name" value="%s" '
                'pattern="[A-Za-z0-9][A-Za-z0-9_.-]{0,63}" maxlength="64" required></label>' % (
                    package_options, source_options, root_options, esc(retained_value("destination_name"))))
        out.append(form("preview", body, "Preview exact restore scope"))
    out.append('<p>Conflicting identities or evidence refuse the copy. Review those revisions '
               'before retrying. Reading-history packages use their dedicated fresh-root restore.</p>'
               '<a href="/courses">Return to courses</a></section>')
    return ''.join(out)
