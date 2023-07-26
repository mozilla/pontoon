import { StreamParser } from '@codemirror/language';

export const fluentMode: StreamParser<{ expression: boolean; tag: boolean }> = {
  name: 'fluent',
  startState: () => ({ expression: false, tag: false }),
  token(stream, state) {
    const ch = stream.next();
    if (state.expression) {
      if (ch === '}') {
        state.expression = false;
        return 'brace';
      }
      stream.skipTo('}');
      return 'name';
    } else {
      if (ch === '{') {
        state.expression = true;
        return 'brace';
      }
      if (ch === '<') {
        state.tag = true;
      }
      if (state.tag) {
        if (ch === '>') {
          state.tag = false;
        } else {
          stream.eatWhile(/[^>{]+/);
        }
        return 'tagName';
      }
      stream.eatWhile(/[^<{]+/);
      return 'string';
    }
  },
};

const printf =
  /^%(\d\$|\(.*?\))?[-+ 0'#]*[\d*]*(\.[\d*])?(hh?|ll?|[jLtz])?[%@AacdEeFfGginopSsuXx]/;

const pythonFormat = /^{[\w.[\]]*(![rsa])?(:.*?)?}/;

export const commonMode: StreamParser<{ tag: boolean }> = {
  name: 'common',
  startState: () => ({ tag: false }),
  token(stream, state) {
    if (stream.match(printf) || stream.match(pythonFormat)) {
      return 'keyword';
    }
    const ch = stream.next();
    if (ch === '<') {
      state.tag = true;
    }
    if (state.tag) {
      if (ch === '>') {
        state.tag = false;
      } else {
        stream.eatWhile(/[^>%{]+/);
      }
      return 'tagName';
    }
    stream.eatWhile(/[^%{<]+/);
    return 'string';
  },
};
