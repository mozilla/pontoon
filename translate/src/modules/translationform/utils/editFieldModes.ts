import { StreamParser } from '@codemirror/language';

export const fluentMode: StreamParser<Array<'expression' | 'literal' | 'tag'>> =
  {
    name: 'fluent',
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
            default:
              stream.eatWhile(/[^"{]+/);
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

const printf =
  /^%(\d\$|\(.*?\))?[-+ 0'#]*[\d*]*(\.[\d*])?(hh?|ll?|[jLtz])?[%@AacdEeFfGginopSsuXx]/;

const pythonFormat = /^{[\w.[\]]*(![rsa])?(:.*?)?}/;

export const commonMode: StreamParser<Array<'literal' | 'tag'>> = {
  name: 'common',
  startState: () => [],
  token(stream, state) {
    if (stream.match(printf) || stream.match(pythonFormat)) {
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
