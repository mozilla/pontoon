export const placeholder = (() => {
  // HTML/XML <tags>
  const html = '<(?:(?:"[^"]*")|(?:\'[^\']*\')|[^>])*>';
  // Fluent & other similar {placeholders}
  const curly = '{(?:(?:"[^"]*")|[^}])*}}?';
  // All printf-ish formats, including Python's.
  // Excludes Python's ` ` conversion flag, due to false positives -- https://github.com/mozilla/pontoon/issues/2988
  const printf =
    "%(?:\\d\\$|\\(.*?\\))?[-+0'#I]*[\\d*]*(?:\\.[\\d*])?(?:hh?|ll?|[jLtz])?[%@AaCcdEeFfGginopSsuXx]";
  // Qt placeholders -- https://doc.qt.io/qt-5/qstring.html#arg
  const qt = '%L?\\d{1,2}';
  // HTML/XML &entities;
  const entity = '&(?:[\\w.-]+|#(?:\\d{1,5}|x[a-fA-F0-9]{1,5})+);';
  // $foo$ and $bar styles, used e.g. in webextension localization
  const dollar = '\\$\\w+\\$?';

  // all whitespace except for usual single spaces within the message
  const spaces = '[\n\t]|(?:^| )[^\\S\n\t]+|[^\\S\n\t]+$|[^\\S \n\t]+';
  // punctuation
  const punct = '[™©®℃℉°±πθ×÷−√∞∆Σ′″‘’ʼ‚‛“”„‟«»£¥€…—–]+';
  // \ escapes
  const escape = '\\\\(?:[nrt\'"\\\\]|u[0-9A-Fa-f]{4}|(?=\\n))';
  // Command-line --options and -s shorthands
  const cli = '\\B(?:-\\w|--[\\w-]+)\\b';
  // URL
  const url =
    // protocol       host         port          path & query                   end
    '(?:ftp|https?)://\\w[\\w.]*\\w(?::\\d{1,5})?(?:/[\\w$.+!*(),;:@&=?/~#%-]*)?(?=$|[\\s\\]\'"}>),.])';

  return new RegExp(
    [html, curly, printf, qt, entity, dollar, spaces, punct, escape, cli, url]
      .map((x) => `(?:${x})`)
      .join('|'),
    'g',
  );
})();
