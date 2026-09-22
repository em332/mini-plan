/* Namensfilter fuer den Ministrantenplan.
   Der Gesamtplan steht bereits im HTML und ist ohne JavaScript lesbar.
   Dieses Skript ergaenzt ausschliesslich die Filterfunktion. */
(function () {
  "use strict";

  var S = window.MiniSuche;
  var form = document.getElementById("filter");
  if (!form || !S) { return; }

  var input = document.getElementById("name-search");
  var select = document.getElementById("name-select");
  var reset = document.getElementById("filter-reset");
  var printBtn = document.getElementById("print-btn");
  var status = document.getElementById("filter-status");
  var scope = document.getElementById("print-scope");

  /* Plan aus dem gerenderten HTML auslesen - keine zusaetzliche Datenquelle. */
  var masses = [].slice.call(document.querySelectorAll(".mass")).map(function (el) {
    return {
      el: el,
      day: el.closest(".day"),
      servers: [].slice.call(el.querySelectorAll(".servers li")).map(function (li) {
        return { el: li, name: li.getAttribute("data-name") || li.textContent.trim() };
      })
    };
  });

  var allNames = [];
  masses.forEach(function (m) {
    m.servers.forEach(function (s) {
      if (allNames.indexOf(s.name) === -1) { allNames.push(s.name); }
    });
  });
  allNames.sort(function (a, b) { return a.localeCompare(b, "de"); });

  allNames.forEach(function (name) {
    var opt = document.createElement("option");
    opt.value = name;
    opt.textContent = name;
    select.appendChild(opt);
    var dl = document.getElementById("name-list");
    if (dl) {
      var o2 = document.createElement("option");
      o2.value = name;
      dl.appendChild(o2);
    }
  });

  form.hidden = false;          /* Bedienelemente erst einblenden, wenn JS laeuft */

  function apply(query) {
    var q = (query || "").trim();
    var shown = 0;
    var matchedNames = [];

    masses.forEach(function (m) {
      var hit = false;
      m.servers.forEach(function (s) {
        var isMatch = q !== "" && S.matches(s.name, q, allNames);
        s.el.classList.toggle("is-match", isMatch);
        var flag = s.el.querySelector(".match-flag");
        if (flag) { flag.textContent = isMatch ? " ✓ gesucht" : ""; }
        if (isMatch) {
          hit = true;
          if (matchedNames.indexOf(s.name) === -1) { matchedNames.push(s.name); }
        }
      });
      var visible = q === "" || hit;
      m.el.hidden = !visible;
      if (visible) { shown++; }
    });

    [].slice.call(document.querySelectorAll(".day")).forEach(function (day) {
      var any = [].slice.call(day.querySelectorAll(".mass")).some(function (el) { return !el.hidden; });
      day.hidden = !any;
    });

    if (q === "") {
      status.textContent = "Gesamtplan: alle " + masses.length + " Gottesdienste werden angezeigt.";
      status.classList.remove("is-empty");
      scope.textContent = "Gesamtplan (ungefiltert)";
    } else if (shown === 0) {
      status.textContent = "Keine Treffer für „" + q + "“. Bitte Schreibweise prüfen " +
                           "oder den Filter zurücksetzen.";
      status.classList.add("is-empty");
      scope.textContent = "Gefilterte Ansicht: keine Treffer für „" + q + "“";
    } else {
      status.textContent = shown + (shown === 1 ? " Termin" : " Termine") + " für " +
                           matchedNames.join(", ") + " – jeweils mit der vollständigen Besetzung.";
      status.classList.remove("is-empty");
      scope.textContent = "Gefilterte Ansicht: " + matchedNames.join(", ") +
                          " (" + shown + (shown === 1 ? " Termin" : " Termine") + ")";
    }
  }

  input.addEventListener("input", function () {
    if (select.value && select.value !== input.value) { select.value = ""; }
    apply(input.value);
  });
  select.addEventListener("change", function () {
    input.value = select.value;
    apply(select.value);
  });
  form.addEventListener("submit", function (ev) { ev.preventDefault(); apply(input.value); });
  reset.addEventListener("click", function () {
    input.value = "";
    select.value = "";
    apply("");
    input.focus();
  });
  if (printBtn) {
    printBtn.addEventListener("click", function () { window.print(); });
  }

  apply("");
})();
