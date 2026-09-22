/* Reine Suchlogik des Namensfilters.
   Ohne DOM, damit sie automatisiert getestet werden kann (tests/test_ui.mjs). */
(function (root, factory) {
  if (typeof module === "object" && module.exports) { module.exports = factory(); }
  else { root.MiniSuche = factory(); }
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  /* Vereinheitlicht Gross-/Kleinschreibung, Umlaute, ss und Akzente.
     Die Normalisierung vergleicht nur Schreibweisen desselben Anzeigenamens;
     sie fuehrt keine unterschiedlichen Personen zusammen. */
  function normalise(value) {
    return String(value == null ? "" : value)
      .toLowerCase()
      .replace(/ä/g, "ae").replace(/ö/g, "oe").replace(/ü/g, "ue")
      .replace(/ß/g, "ss")
      .normalize("NFD").replace(/[̀-ͯ]/g, "")
      .replace(/[^a-z0-9]+/g, " ")
      .trim();
  }

  /* Zweite Variante ohne eingefuegtes "e": erlaubt auch "woss", "muller", "grun". */
  function collapse(value) {
    return normalise(value).replace(/ae|oe|ue/g, function (m) { return m.charAt(0); })
                           .replace(/ss/g, "s");
  }

  /* Trifft die Eingabe genau einen vorhandenen Anzeigenamen, wird ausschliesslich
     diese Person gesucht. Sonst waere "Lena B." auch ein Teiltreffer von
     "Annalena B." - zwei verschiedene Personen duerfen nie zusammenfallen. */
  function isExactName(query, allNames) {
    if (!allNames || !allNames.length) { return false; }
    var q = normalise(query), qc = collapse(query);
    return allNames.some(function (n) {
      return normalise(n) === q || collapse(n) === qc;
    });
  }

  function matches(displayName, query, allNames) {
    var q = normalise(query);
    if (!q) { return true; }
    if (isExactName(query, allNames)) {
      return normalise(displayName) === q || collapse(displayName) === collapse(query);
    }
    if (normalise(displayName).indexOf(q) !== -1) { return true; }
    return collapse(displayName).indexOf(collapse(query)) !== -1;
  }

  /* Liefert die Termine, in denen mindestens eine passende Person dient. */
  function filterPlan(services, query, allNames) {
    if (!normalise(query)) {
      return { active: false, services: services.slice(), matchedNames: [], count: 0 };
    }
    if (!allNames) {
      allNames = [];
      services.forEach(function (svc) {
        svc.servers.forEach(function (n) {
          if (allNames.indexOf(n) === -1) { allNames.push(n); }
        });
      });
    }
    var names = {};
    var hits = services.filter(function (svc) {
      var found = svc.servers.filter(function (n) { return matches(n, query, allNames); });
      found.forEach(function (n) { names[n] = true; });
      return found.length > 0;
    });
    return {
      active: true,
      services: hits,
      matchedNames: Object.keys(names).sort(),
      count: hits.length
    };
  }

  return { normalise: normalise, collapse: collapse, isExactName: isExactName,
           matches: matches, filterPlan: filterPlan };
});
