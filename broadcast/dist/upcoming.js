'use strict';
// Static pages are built on a schedule, so an event listed as "coming up" can finish before the
// next rebuild. Hide anything that ended before the reader's local date, cap each list, and show
// the list's empty message if nothing is left.
(() => {
  const today = new Date();
  const iso = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
  document.querySelectorAll('[data-upcoming-limit]').forEach((list) => {
    const limit = Number(list.dataset.upcomingLimit) || Infinity;
    let shown = 0;
    list.querySelectorAll('[data-end]').forEach((item) => {
      const keep = item.dataset.end >= iso && shown < limit;
      item.hidden = !keep;
      if (keep) shown += 1;
    });
    const empty = list.querySelector('[data-upcoming-empty]');
    if (empty) empty.hidden = shown > 0;
  });
})();
