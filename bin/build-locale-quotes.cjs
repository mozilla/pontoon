#!/usr/bin/env node
/* eslint-env node */
/* eslint-disable no-console */

const { readdirSync, writeFileSync } = require('fs');
const { dirname, join, resolve } = require('path');

/**
 * Builds a record of the primary start and end quotes for each available locale,
 * based on CLDR data.
 *
 * If this file is executed directly,
 * writes the output as JSON to the path provided as an argument, or the console.
 */

function buildLocaleQuotes() {
  const pkgPath = require.resolve('cldr-misc-full/package.json');
  const root = join(dirname(pkgPath), 'main');

  /** @type {Record<string, [string, string]} */
  const res = {};
  for (const lc of readdirSync(root)) {
    try {
      const data = require(`cldr-misc-full/main/${lc}/delimiters.json`);
      const { delimiters } = data.main[lc];
      let q0 = delimiters.quotationStart;
      let q1 = delimiters.quotationEnd;

      // Add narrow no-break space inside guillemets for French, except in Canada & Switzerland
      // https://en.wikipedia.org/wiki/Quotation_mark#French
      if (
        /^fr(-|$)/.test(lc) &&
        lc !== 'fr-CA' &&
        lc !== 'fr-CH' &&
        q0 === '«' &&
        q1 === '»'
      ) {
        q0 = '«\u202f';
        q1 = '\u202f»';
      }

      res[lc] = [q0, q1];
    } catch (err) {
      console.error(`Data read error for ${lc}`, err);
    }
  }

  return res;
}

module.exports = buildLocaleQuotes;

if (require.main === module) {
  const res = buildLocaleQuotes();
  const str = JSON.stringify(res, null, 2);
  const target = process.argv[2];
  if (target && target !== '-') {
    writeFileSync(resolve(target), str);
  } else {
    console.log(str);
  }
}
