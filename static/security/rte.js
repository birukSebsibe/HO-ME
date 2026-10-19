/*
 * HO-ME admin — lightweight rich-text editor for `.js-rte` textareas.
 * No external dependencies: turns each textarea into a contentEditable surface
 * with a small toolbar (bold / italic / underline / lists / link / headings),
 * and syncs the HTML back into the textarea on input.
 */
(function () {
  function initEditor(textarea) {
    if (textarea.dataset.rteReady) return;
    textarea.dataset.rteReady = "1";

    var wrapper = document.createElement("div");
    wrapper.className = "rte-wrapper";

    var toolbar = document.createElement("div");
    toolbar.className = "rte-toolbar";
    var buttons = [
      ["bold", "B", "Bold"],
      ["italic", "I", "Italic"],
      ["underline", "U", "Underline"],
      ["insertUnorderedList", "• List", "Bulleted list"],
      ["insertOrderedList", "1. List", "Numbered list"],
      ["formatBlock:h3", "H3", "Heading 3"],
      ["formatBlock:p", "¶", "Paragraph"],
      ["createLink", "🔗", "Insert link"],
      ["removeFormat", "✕", "Clear formatting"],
    ];
    buttons.forEach(function (btn) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "rte-btn";
      b.innerHTML = btn[1];
      b.title = btn[2];
      b.addEventListener("mousedown", function (e) { e.preventDefault(); });
      b.addEventListener("click", function () {
        var cmd = btn[0].split(":");
        if (cmd[0] === "createLink") {
          var url = prompt("Link URL:");
          if (url) document.execCommand(cmd[0], false, url);
        } else if (cmd[0] === "formatBlock") {
          document.execCommand("formatBlock", false, "<" + cmd[1] + ">");
        } else {
          document.execCommand(cmd[0], false, null);
        }
        sync();
      });
      toolbar.appendChild(b);
    });

    var surface = document.createElement("div");
    surface.className = "rte-surface";
    surface.contentEditable = "true";
    surface.innerHTML = textarea.value || "<p></p>";

    function sync() {
      textarea.value = surface.innerHTML;
    }
    surface.addEventListener("input", sync);

    textarea.parentNode.insertBefore(wrapper, textarea);
    wrapper.appendChild(toolbar);
    wrapper.appendChild(surface);
    wrapper.appendChild(textarea);
    textarea.style.display = "none";
    sync();
  }

  function boot() {
    document.querySelectorAll("textarea.js-rte").forEach(initEditor);
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
  // Django admin inlines added dynamically
  document.addEventListener("formset:added", function () { setTimeout(boot, 50); });
})();
