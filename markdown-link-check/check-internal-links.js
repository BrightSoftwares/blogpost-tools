#!/usr/bin/env node
/**
 * Thin wrapper around the markdown-link-check library (not its CLI, which has
 * a known bug: passing --config without a "reporters" key in the JSON file
 * makes it overwrite opts.reporters with undefined and crash silently with
 * exit 1 and no output — see markdown-link-check#292-style reports).
 *
 * Scope: internal links only. External http(s) links are ignored by the
 * ignorePatterns below — this check exists to catch broken *internal*
 * links (relative file paths + same-file anchors) between blog posts, not
 * to babysit third-party site uptime in CI.
 */
'use strict';
const fs = require('fs');
const path = require('path');
const markdownLinkCheck = require('markdown-link-check');

const dir = process.argv[2];
if (!dir) {
  console.error('Usage: check-internal-links.js <dir>');
  process.exit(2);
}

function collectMarkdownFiles(root) {
  const out = [];
  for (const entry of fs.readdirSync(root, { withFileTypes: true })) {
    const full = path.join(root, entry.name);
    if (entry.isDirectory()) out.push(...collectMarkdownFiles(full));
    else if (entry.isFile() && full.endsWith('.md')) out.push(full);
  }
  return out;
}

const files = collectMarkdownFiles(dir);
let hadBrokenLinks = false;
let checkedFiles = 0;

function checkOne(file) {
  return new Promise((resolve) => {
    const markdown = fs.readFileSync(file, 'utf8');
    const opts = {
      baseUrl: 'file://' + path.dirname(path.resolve(file)),
      projectBaseUrl: 'file://' + process.cwd(),
      ignorePatterns: [
        { pattern: '^https?://' },
        { pattern: '^mailto:' },
      ],
      aliveStatusCodes: [200, 206],
      retryOn429: false,
      timeout: '10s',
    };
    markdownLinkCheck(markdown, opts, (err, results) => {
      checkedFiles += 1;
      if (err) {
        console.error(`[error] ${file}: ${err.message || err}`);
        hadBrokenLinks = true;
        return resolve();
      }
      const dead = (results || []).filter((r) => r.status === 'dead');
      if (dead.length > 0) {
        hadBrokenLinks = true;
        console.log(`\n::group::${file}`);
        for (const d of dead) {
          console.log(`  [broken] ${d.link} (${d.statusCode || d.err})`);
        }
        console.log('::endgroup::');
      }
      resolve();
    });
  });
}

(async () => {
  for (const file of files) {
    await checkOne(file);
  }
  console.log(`\nChecked ${checkedFiles} file(s) for internal link validity.`);
  if (hadBrokenLinks) {
    console.error('One or more internal links are broken. See groups above.');
    process.exit(1);
  }
  console.log('All internal links resolve.');
  process.exit(0);
})();
