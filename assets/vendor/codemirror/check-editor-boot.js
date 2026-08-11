/* check-editor-boot.js -- the ONE place the check item's CodeMirror editor is
   configured (plan 05-05 Task 3). The served page embeds this file after the
   vendored bundle; tests/js/check_editor.test.mjs loads the same two files
   into jsdom, so the interactive contract is executed, not read from source.
   It attaches window.CheckEditorBoot and uses window.CodeMirror from the
   vendored bundle -- no CDN, no second copy of the configuration.
*/
(function (global) {
  "use strict";
  var CM = global.CodeMirror;
  var NL = "\n";

  /* Shift-Tab: dedent the current line only -- remove one leading tab, else
     up to four leading spaces, else do nothing. Never touches a previous
     line and never dedents past column 0 (05-UI-SPEC Editor Interaction
     Contract). A real CM6 transaction, so undo walks it. */
  function dedentLine(view) {
    var head = view.state.selection.main.head;
    var line = view.state.doc.lineAt(head);
    var text = line.text;
    var remove = 0;
    if (text.charAt(0) === "\t") {
      remove = 1;
    } else {
      var sp = 0;
      while (sp < 4 && sp < text.length && text.charAt(sp) === " ") sp++;
      remove = sp;
    }
    if (remove === 0) return false;
    view.dispatch({
      changes: { from: line.from, to: line.from + remove, insert: "" },
      userEvent: "delete"
    });
    return true;
  }

  function create(mount, opts) {
    opts = opts || {};
    var starter = opts.starter || "";
    var readOnly = new CM.Compartment();
    /* CM6's editing commands do not consult state.readOnly themselves, so
       the editing key bindings are guarded here: once submitted, Tab/Enter/
       Shift-Tab no longer change the document (the submitted source stays
       visible, read-only, matching every other type's lock-then-reveal). */
    function guard(view, cmd) {
      return view.state.readOnly ? false : cmd(view);
    }
    var exts = [
      CM.lineNumbers(),            /* 1-based, grows with the document */
      CM.history(),
      CM.keymap.of([
        { key: "Tab", run: function (v) { return guard(v, CM.insertTab); } },
        { key: "Shift-Tab", run: function (v) { return guard(v, dedentLine); } },
        { key: "Enter", run: function (v) { return guard(v, CM.insertNewline); } },
        { key: "Mod-z", run: CM.undo },
        { key: "Mod-y", run: CM.redo },
        { key: "Mod-Shift-z", run: CM.redo }
      ]),
      readOnly.of(CM.EditorState.readOnly.of(false))
      /* deliberately no CM.lineWrapping: a long line scrolls horizontally
         so gutter row N is editor line N at any content width (CODE-03) */
    ];
    if (!starter) {
      exts.push(CM.placeholder("# Write your code here."));
    }
    var view = new CM.EditorView({
      doc: starter,
      parent: mount,
      extensions: exts
    });
    var submitted = false;
    view.checkEditor = {
      getSource: function () { return view.state.doc.toString(); },
      isEmpty: function () { return view.state.doc.length === 0; },
      wraps: function () {
        /* structural no-wrap assertion: EditorView.lineWrapping getter */
        return view.lineWrapping;
      },
      setReadOnly: function (ro) {
        submitted = ro;
        view.dispatch({
          effects: readOnly.reconfigure(
            CM.EditorState.readOnly.of(ro))
        });
        if (ro) mount.setAttribute("data-readonly", "true");
      },
      isReadOnly: function () { return submitted; },
      focus: function () { view.focus(); },
      /* expose the current line count for the 1-based-gutter assertion */
      lineCount: function () { return view.state.doc.lines; },
      getView: function () { return view; }
    };
    return view.checkEditor;
  }

  global.CheckEditorBoot = { create: create, dedentLine: dedentLine };
})(typeof window !== "undefined" ? window : globalThis);
