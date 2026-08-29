// Publication rendering shared by index.html (selected TOC) and publications.html (full index).
(function () {
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

  var MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  function fmtDate(p) {
    var d = p.date;
    if (d && d.length === 10) {
      var parts = d.split('-');
      return parseInt(parts[2], 10) + ' ' + MONTHS[parseInt(parts[1], 10) - 1] + ' ' + parts[0];
    }
    if (d && d.length === 7) {
      var mp = d.split('-');
      return MONTHS[parseInt(mp[1], 10) - 1] + ' ' + mp[0];
    }
    return p.year || '';
  }

  function sortKey(p) { return p.date || p.year || '0'; }

  function load() {
    // Data is loaded inline via data/publications.js (window.PUBLICATIONS) so the site
    // works when opened directly from disk (file://) as well as over HTTP.
    return Promise.resolve(window.PUBLICATIONS || []);
  }

  // ---- home: magazine table-of-contents row ----
  function tocRow(p, i) {
    var url = link(p);
    var title = url
      ? '<a href="' + esc(url) + '" target="_blank" rel="noopener">' + esc(p.title) + '</a>'
      : esc(p.title);
    var venue = p.journal ? '<span class="venue">' + esc(p.journal) + '</span>' : '';
    var year = p.year ? '<span>' + esc(p.year) + '</span>' : '';
    var role = p.role ? '<span class="role">' + esc(p.role) + '</span>' : '';
    var authors = fmtAuthors(p.authors);
    return '<article class="toc-row">' +
      '<span class="toc-num">' + String(i + 1).padStart(2, '0') + '</span>' +
      '<div class="toc-thumb"><picture>' +
        '<source srcset="img/' + esc(p.image) + '.webp" type="image/webp">' +
        '<img src="img/' + esc(p.image) + '.png" alt="" loading="lazy" width="180" height="113">' +
      '</picture></div>' +
      '<div class="toc-body">' +
        '<h3>' + title + '</h3>' +
        (authors ? '<p class="authors">' + authors + '</p>' : '') +
        '<div class="toc-meta">' + venue + year + role + '</div>' +
      '</div></article>';
  }

  var featEl = document.getElementById('featuredPubs');
  if (featEl) {
    load().then(function (data) {
      var sel = data.filter(function (p) { return p.selected && p.image; })
        .sort(function (a, b) { return (a.featured_order || 0) - (b.featured_order || 0); });
      featEl.innerHTML = sel.map(tocRow).join('');
    }).catch(function () { featEl.innerHTML = '<p class="muted">Publications are loading — view the full list.</p>'; });
  }

  // ---- full list: dense editorial index row ----
  function idxRow(p) {
    var url = link(p);
    var title = url
      ? '<a href="' + esc(url) + '" target="_blank" rel="noopener">' + esc(p.title) + '</a>'
      : esc(p.title);
    var venue = p.journal ? '<span class="venue">' + esc(p.journal) + '</span>' : '';
    var authors = fmtAuthors(p.authors);
    return '<article class="idx-row">' +
      '<div>' +
        '<h3>' + title + '</h3>' +
        (authors ? '<p class="authors">' + authors + '</p>' : '') +
        (venue ? '<p class="idx-meta">' + venue + '</p>' : '') +
      '</div>' +
      '<span class="idx-year">' + esc(fmtDate(p)) + '</span>' +
      '</article>';
  }

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
        html += idxRow(p);
      });
      fullEl.innerHTML = html || '<p class="muted">No entries.</p>';
    }

    load().then(function (data) {
      ALL = data.slice().sort(function (a, b) { return sortKey(b).localeCompare(sortKey(a)); });
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
