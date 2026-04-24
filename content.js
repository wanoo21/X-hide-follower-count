const INFINITY = "\u221E"; // ∞
const DEBOUNCE_MS = 40;

/** If false, only follower counts are hidden; following counts stay visible. (Future: user setting.) */
const HIDE_FOLLOWING = false;

/** Shown on hover over the stat after the count is replaced. */
const TOOLTIP_FALLBACK = {
  followerTooltip:
    'Follower count hidden by the "X: hide follower count" extension. Disable or remove the extension to see the number.',
  followingTooltip:
    'Following count hidden by the "X: hide follower count" extension. Disable or remove the extension to see the number.',
};

function getTooltipMessage(key) {
  try {
    if (typeof chrome !== "undefined" && chrome.i18n?.getMessage) {
      const t = chrome.i18n.getMessage(key);
      if (t) return t;
    }
  } catch {
    // ignore
  }
  return TOOLTIP_FALLBACK[key] || "";
}

function isFollowerLink(anchor) {
  try {
    const u = new URL(anchor.href);
    if (!/^(x|twitter)\.com$/i.test(u.hostname)) return false;
    const parts = u.pathname.split("/").filter(Boolean);
    if (parts.length !== 2) return false;
    const seg = parts[1].toLowerCase();
    return seg === "followers" || seg === "verified_followers";
  } catch {
    return false;
  }
}

function isFollowingLink(anchor) {
  try {
    const u = new URL(anchor.href);
    if (!/^(x|twitter)\.com$/i.test(u.hostname)) return false;
    const parts = u.pathname.split("/").filter(Boolean);
    if (parts.length !== 2) return false;
    return parts[1].toLowerCase() === "following";
  } catch {
    return false;
  }
}

function isNumericToken(s) {
  if (!s || s === INFINITY) return false;
  const t = s.replace(/\s/g, "").replace(/\u00A0/g, "");
  if (!t) return false;
  if (
    /^\d{1,3}(?:,\d{3})*(\.\d+)?[KkMmBb]?$/.test(t) &&
    (/\d/.test(t) || t.includes(","))
  ) {
    return true;
  }
  if (/^(?:\d+)?\.\d+[KkMmBb]$/.test(t) || /^\d+(?:\.\d+)?[KkMmBb]$/.test(t)) {
    return true;
  }
  if (/^\d+(?:\.\d+)?$/.test(t)) {
    return true;
  }
  return false;
}

function replaceNodeCount(el) {
  if (!el) return false;
  const text = el.textContent;
  if (text == null) return false;
  if (text.trim() === INFINITY) return false;
  const s = text.trim();
  if (!s) return false;
  if (isNumericToken(s)) {
    el.textContent = INFINITY;
    return true;
  }
  const m = s.match(/^(\S+)/);
  if (m && m[1] && isNumericToken(m[1])) {
    const first = m[1];
    const i = text.indexOf(first);
    if (i === -1) return false;
    el.textContent = text.slice(0, i) + INFINITY + text.slice(i + first.length);
    return true;
  }
  return false;
}

function linkShowsInfinity(anchor) {
  return (anchor.textContent || "").includes(INFINITY);
}

function replaceStatCount(anchor, tooltip) {
  let changed = false;
  const spans = anchor.querySelectorAll("span");
  for (const span of spans) {
    if (replaceNodeCount(span)) {
      changed = true;
      break;
    }
  }
  if (!changed) {
    changed = replaceNodeCount(anchor);
  }
  if (changed || linkShowsInfinity(anchor)) {
    anchor.setAttribute("title", tooltip);
  }
}

/**
 * Profile headers, hover cards (#layers), and other surfaces use the same
 * /handle/followers and /handle/following links.
 */
function run() {
  for (const a of document.querySelectorAll(
    'a[href*="/followers"], a[href*="/verified_followers"]'
  )) {
    if (isFollowerLink(a)) replaceStatCount(a, getTooltipMessage("followerTooltip"));
  }
  if (HIDE_FOLLOWING) {
    for (const a of document.querySelectorAll('a[href*="/following"]')) {
      if (isFollowingLink(a)) replaceStatCount(a, getTooltipMessage("followingTooltip"));
    }
  }
}

let obs = null;
let observedEl = null;

function getObserveTarget() {
  // Must be document.body: hover / account / profile popups mount under #layers, outside <main>.
  return document.body;
}

function ensureObserver() {
  const target = getObserveTarget();
  if (!target || target.isConnected === false) return;
  if (target === observedEl && obs) return;
  if (obs) {
    obs.disconnect();
    obs = null;
  }
  observedEl = target;
  obs = new MutationObserver(() => scheduleRun());
  obs.observe(target, { childList: true, subtree: true });
}

let debounceTimer = 0;

function doRun() {
  ensureObserver();
  run();
  // React often paints counts after the first frame; second pass cuts flash.
  if (typeof requestAnimationFrame === "function") {
    requestAnimationFrame(() => {
      run();
    });
  }
}

function flushScheduledRun() {
  debounceTimer = 0;
  doRun();
}

function scheduleRun() {
  if (debounceTimer) clearTimeout(debounceTimer);
  debounceTimer = setTimeout(flushScheduledRun, DEBOUNCE_MS);
}

function onNavigation() {
  doRun();
  scheduleRun();
}

function patchHistory(methodName) {
  const orig = history[methodName];
  if (typeof orig !== "function") return;
  history[methodName] = function patchedHistory(...args) {
    const ret = orig.apply(this, args);
    onNavigation();
    return ret;
  };
}

function startObserver() {
  if (!document.body) return;
  ensureObserver();
  onNavigation();
}

if (document.body) {
  startObserver();
} else {
  document.addEventListener("DOMContentLoaded", startObserver);
}

window.addEventListener("popstate", onNavigation);
patchHistory("pushState");
patchHistory("replaceState");
