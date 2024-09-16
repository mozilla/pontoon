import { StreamParser } from '@codemirror/language';

export const fluentMode: StreamParser<Array<'expression' | 'literal' | 'tag'>> =
  {
    name: 'fluent',
    languageData: { closeBrackets: { brackets: ['(', '[', '{', '"', '<'] } },
    startState: () => [],
    token(stream, state) {
      const ch = stream.next();
      switch (state.at(-1)) {
        case 'expression':
          switch (ch) {
            case '"':
              state.push('literal');
              return 'quote';
            case '{':
              state.push('expression');
              return 'brace';
            case '}':
              state.pop();
              return 'brace';
            default:
              stream.eatWhile(/[^"{}]+/);
              return 'name';
          }

        case 'literal':
          switch (ch) {
            case '"':
              state.pop();
              return 'quote';
            case '{':
              state.push('expression');
              return 'brace';
            // These will mis-highlight actual } or > in literals,
            // but that's a rare enough occurrence when balanced
            // with the improved editing experience.
            case '}':
              state.pop();
              state.pop();
              return 'brace';
            case '>':
              state.pop();
              state.pop();
              return 'bracket';
            default:
              stream.eatWhile(/[^"{}>]+/);
              return 'literal';
          }

        case 'tag':
          switch (ch) {
            case '"':
              state.push('literal');
              return 'quote';
            case '{':
              state.push('expression');
              return 'brace';
            case '>':
              state.pop();
              return 'bracket';
            default:
              stream.eatWhile(/[^"{>]+/);
              return 'tagName';
          }

        default:
          switch (ch) {
            case '{':
              state.push('expression');
              return 'brace';
            case '<':
              state.push('tag');
              return 'bracket';
            default:
              stream.eatWhile(/[^<{]+/);
              return 'string';
          }
      }
    },
  };

// Excludes ` ` even if it's a valid Python conversion flag,
// due to false positives.
// https://github.com/mozilla/pontoon/issues/2988
const printf =
  /^%(\d\$|\(.*?\))?[-+0'#]*[\d*]*(\.[\d*])?(hh?|ll?|[jLtz])?[%@AacdEeFfGginopSsuXx]/;

const pythonFormat = /^{[\w.[\]]*(![rsa])?(:.*?)?}/;

// https://www.i18next.com/translation-function/interpolation
const i18nextFormat = /{{.*?}}/;

export const commonMode: StreamParser<Array<'literal' | 'tag'>> = {
  name: 'common',
  languageData: { closeBrackets: { brackets: ['(', '[', '{', '"', '<'] } },
  startState: () => [],
  token(stream, state) {
    if (
      stream.match(printf) ||
      stream.match(pythonFormat) ||
      stream.match(i18nextFormat)
    ) {
      return 'keyword';
    }

    const ch = stream.next();
    switch (state.at(-1)) {
      case 'literal':
        switch (ch) {
          case '"':
            state.pop();
            return 'quote';
          default:
            stream.eatWhile(/[^%{"]+/);
            return 'literal';
        }

      case 'tag':
        switch (ch) {
          case '"':
            state.push('literal');
            return 'quote';
          case '>':
            state.pop();
            return 'bracket';
          default:
            stream.eatWhile(/[^%{">]+/);
            return 'tagName';
        }

      default:
        switch (ch) {
          case '<':
            state.push('tag');
            return 'bracket';
          default:
            stream.eatWhile(/[^%{<]+/);
            return 'string';
        }
    }
  },
};
