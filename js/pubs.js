// Publication rendering shared by index.html (selected) and publications.html (full).
(function () {
  var ME = /^j\w*\s+wang$|jianghao\s+wang|wang,?\s*j/i;

  function esc(s) { var d = document.createElement('div'); d.textContent = s || ''; return d.innerHTML; }

  function fmtAuthors(authors) {
    if (!authors || !authors.length) return '';
    return authors.map(function (a) {
      var isMe = /jianghao\s+wang/i.test(a) || /^wang,?\s*jianghao/i.test(a);
      return isMe ? '<span class="me">' + esc(a) + '</span>' : esc(a);
    }).join(', ');
  }

  function link(p) {
    if (p.doi) return 'https://doi.org/' + p.doi;
    if (p.uri) return p.uri;
    return null;
  }

  function pubCard(p, opts) {
    opts = opts || {};
    var url = link(p);
    var title = url
      ? '<a href="' + esc(url) + '" target="_blank" rel="noopener">' + esc(p.title) + '</a>'
      : esc(p.title);
    var venue = p.journal ? '<span class="badge badge-venue">' + esc(p.journal) + '</span>' : '';
    var year = p.year ? '<span class="badge badge-year">' + esc(p.year) + '</span>' : '';
    var role = (opts.role && p.role) ? '<span class="badge badge-role">' + esc(p.role) + '</span>' : '';
    var blurb = (opts.blurb && p.blurb) ? '<p class="blurb">' + esc(p.blurb) + '</p>' : '';
    var links = [];
    if (url) links.push('<a href="' + esc(url) + '" target="_blank" rel="noopener">DOI ↗</a>');
    var linksHtml = links.length ? '<div class="links">' + links.join('') + '</div>' : '';
    return '<article class="pub' + (opts.compact ? ' pub-compact' : '') +
      (opts.featured ? ' is-featured' : '') + '">' +
      '<div class="venue-row">' + venue + year + role + '</div>' +
      '<h3>' + title + '</h3>' +
      '<p class="authors">' + fmtAuthors(p.authors) + '</p>' +
      blurb + linksHtml + '</article>';
  }

  function load() {
    // Data is loaded inline via data/publications.js (window.PUBLICATIONS) so the site
    // works when opened directly from disk (file://) as well as over HTTP.
    return Promise.resolve(window.PUBLICATIONS || []);
  }

  // ---- selected (home) ----
  var selEl = document.getElementById('selectedPubs');
  if (selEl) {
    load().then(function (data) {
      var sel = data.filter(function (p) { return p.selected; })
        .sort(function (a, b) { return (a.featured_order || 0) - (b.featured_order || 0); });
      selEl.innerHTML = sel.map(function (p) {
        return pubCard(p, { blurb: true, featured: true, role: true });
      }).join('');
    }).catch(function () { selEl.innerHTML = '<p class="muted">Publications are loading — view the full list.</p>'; });
  }

  // ---- full list (publications page) ----
  var fullEl = document.getElementById('fullPubs');
  if (fullEl) {
    var controls = document.getElementById('pubControls');
    var countEl = document.getElementById('pubCount');
    var ALL = [];
    var filter = 'all';

    function typeOf(p) {
      if (p.type === 'journal-article') return 'journal';
      if (p.type === 'book-chapter') return 'book';
      if (p.type === 'conference-paper') return 'conference';
      if (p.type === 'preprint') return 'preprint';
      return 'other';
    }

    function render() {
      var items = ALL.filter(function (p) {
        if (filter === 'all') return true;
        if (filter === 'selected') return p.selected;
        return typeOf(p) === filter;
      });
      countEl.textContent = items.length + ' ' + (items.length === 1 ? 'entry' : 'entries');
      var html = '', curYear = null;
      items.forEach(function (p) {
        var y = p.year || 'Other';
        if (y !== curYear) { html += '<h2 class="year-head">' + esc(y) + '</h2>'; curYear = y; }
        html += pubCard(p, { compact: true, featured: p.selected });
      });
      fullEl.innerHTML = html || '<p class="muted">No entries.</p>';
    }

    load().then(function (data) {
      ALL = data.slice().sort(function (a, b) { return (b.year || '0').localeCompare(a.year || '0'); });
      render();
      if (controls) {
        controls.addEventListener('click', function (e) {
          var b = e.target.closest('.filter-btn'); if (!b) return;
          filter = b.dataset.filter;
          controls.querySelectorAll('.filter-btn').forEach(function (x) { x.classList.remove('active'); });
          b.classList.add('active');
          render();
        });
      }
    }).catch(function () { fullEl.innerHTML = '<p class="muted">Could not load publications.</p>'; });
  }
})();
