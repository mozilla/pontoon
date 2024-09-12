import React from 'react';
import { mount } from 'enzyme';
import { MockLocalizationProvider } from '~/test/utils';
import { Highlight } from './Highlight';

const mountMarker = (content, terms = [], search = null) =>
  mount(
    <MockLocalizationProvider>
      <Highlight search={search} terms={terms}>
        {content}
      </Highlight>
    </MockLocalizationProvider>,
  );

describe('Test parser order', () => {
  it('matches JSON placeholder', () => {
    const content = 'You have created $COUNT$ aliases';
    const wrapper = mountMarker(content);

    expect(wrapper.find('mark')).toHaveLength(1);
    expect(wrapper.find('mark').text()).toContain('$COUNT$');
  });
});

describe('mark terms', () => {
  it('marks terms properly', () => {
    const string = 'foo bar baz';
    const terms = {
      terms: [{ text: 'bar' }, { text: 'baz' }],
    };

    const wrapper = mountMarker(string, terms);

    expect(wrapper.find('mark')).toHaveLength(2);
    expect(wrapper.find('mark').at(0).text()).toEqual('bar');
    expect(wrapper.find('mark').at(1).text()).toEqual('baz');
  });

  it('marks entire words on partial match', () => {
    const string = 'Download Add-Ons from the web.';
    const terms = {
      terms: [{ text: 'add-on' }],
    };

    const wrapper = mountMarker(string, terms);

    const mark = wrapper.find('mark');
    expect(mark).toHaveLength(1);
    expect(mark.text()).toEqual('Add-Ons');
    expect(mark.prop('data-match')).toEqual('add-on');
  });

  it('only marks terms at the beginning of the word', () => {
    const string = 'Consider using one of the alternatives.';
    const terms = {
      terms: [{ text: 'native' }],
    };

    const wrapper = mountMarker(string, terms);

    expect(wrapper.find('mark')).toHaveLength(0);
  });

  it('marks longer terms first', () => {
    const string = 'This is a translation tool.';
    const terms = {
      terms: [{ text: 'translation' }, { text: 'translation tool' }],
    };

    const wrapper = mountMarker(string, terms);

    expect(wrapper.find('mark')).toHaveLength(1);
    expect(wrapper.find('mark').text()).toEqual('translation tool');
  });

  it('does not mark terms within placeables', () => {
    const string =
      'This browser { $version } does not support { $bits }-bit systems.';
    const terms = {
      terms: [{ text: 'browser' }, { text: 'version' }],
    };

    const wrapper = mountMarker(string, terms);

    expect(wrapper.find('mark')).toHaveLength(3);
    expect(wrapper.find('mark').at(0).text()).toEqual('browser');
    expect(wrapper.find('mark').at(0).hasClass('term'));
    expect(wrapper.find('mark').at(1).text()).toEqual('{ $version }');
    expect(wrapper.find('mark').at(1).hasClass('placeable'));
    expect(wrapper.find('mark').at(2).text()).toEqual('{ $bits }');
    expect(wrapper.find('mark').at(2).hasClass('placeable'));
  });
});

describe('<Highlight search>', () => {
  it('does not break on regexp special characters', () => {
    const wrapper = mountMarker('foo (bar)', [], '(bar');
    expect(wrapper.find('mark.search').text()).toEqual('(bar');
  });

  it('does not mark search if empty', () => {
    const wrapper = mountMarker('123456', [], '');
    const marks = wrapper.find('mark');
    expect(marks).toHaveLength(1);
    expect(marks.at(0).hasClass('placeable'));
    expect(marks.at(0).text()).toEqual('123456');
  });

  it('prefers search marks over placeholders at start of mark', () => {
    const wrapper = mountMarker('123456', [], '123');
    const marks = wrapper.find('mark');
    expect(marks).toHaveLength(1);
    expect(marks.at(0).hasClass('search'));
    expect(marks.at(0).text()).toEqual('123');
  });

  it('prefers search marks over placeholders at end of mark', () => {
    const wrapper = mountMarker('123456', [], '456');
    const marks = wrapper.find('mark');
    expect(marks).toHaveLength(1);
    expect(marks.at(0).hasClass('search'));
    expect(marks.at(0).text()).toEqual('456');
  });

  it('does not break for lone " quotes', () => {
    const wrapper = mountMarker('123456"', [], '"');
    const marks = wrapper.find('mark');
    expect(marks).toHaveLength(2);
    expect(marks.at(1).text()).toEqual('"');
  });

  it('does not break for doubled "" quotes', () => {
    const wrapper = mountMarker('123456""', [], '""');
    const marks = wrapper.find('mark');
    expect(marks).toHaveLength(2);
    expect(marks.at(1).text()).toEqual('""');
  });

  it("does not alter source text's capitalization", () => {
    const wrapper = mountMarker('hello world', [], 'HELLO');
    const marks = wrapper.find('mark');
    expect(marks).toHaveLength(1);
    expect(marks.at(0).text()).toEqual('hello');
  });
});

describe('specific marker', () => {
  const tests = [
    // email
    ['Hello lisa@example.org', 'lisa@example.org'],
    ['Hello mailto:lisa@name.me', 'mailto:lisa@name.me'],
    // escapes
    ['hello,\\tworld', '\\t'],
    ['\\n', '\\n'],
    // Fluent
    ['Hello {COPY()}', '{COPY()}'],
    ['Hello { DATETIME($date) }', '{ DATETIME($date) }'],
    [
      'Hello { NUMBER($ratio, minimumFractionDigits: 2) }',
      '{ NUMBER($ratio, minimumFractionDigits: 2) }',
    ],
    [
      'Hello { DATETIME($date) } and { COPY() }',
      '{ DATETIME($date) }',
      '{ COPY() }',
    ],
    ['Hello {-brand(case: "test")}', '{-brand(case: "test")}'],
    ['Hello { -brand(case: "what ever") }', '{ -brand(case: "what ever") }'],
    [
      'Hello { -brand-name(foo-bar: "now that\'s a value!") }',
      '{ -brand-name(foo-bar: "now that\'s a value!") }',
    ],
    [
      'Hello {-brand(case: "test")} and {-vendor(case: "right")}',
      '{-brand(case: "test")}',
      '{-vendor(case: "right")}',
    ],
    ['Hello {""}', '{""}'],
    ['Hello { "" }', '{ "" }'],
    ['Hello { "world!" }', '{ "world!" }'],
    ['Hello { "hello!" } from { "world!" }', '{ "hello!" }', '{ "world!" }'],
    ['Hello {-brand}', '{-brand}'],
    ['Hello { -brand }', '{ -brand }'],
    ['Hello { -brand-name }', '{ -brand-name }'],
    ['Hello {-brand} from {-vendor}', '{-brand}', '{-vendor}'],
    // ICU MessageFormat
    [
      'At {1,time} on {1,date}, there was {2} on planet {0,number,integer}.',
      '{1,time}',
      '{1,date}',
      '{2}',
      '{0,number,integer}',
    ],
    // Web extensions
    ['Hello $USER$', '$USER$'],
    ['Hello $USER1$', '$USER1$'],
    ['Hello $FIRST_NAME$', '$FIRST_NAME$'],
    ['Hello USER$'],
    // spaces
    [' hello world', ' '],
    ['hello world ', ' '],
    ['hello  world', '  '],
    ['hello,   world', '   '],
    ['hello,\u00A0world', '\u00A0'],
    ['hello,\u2009world', '\u2009'],
    ['hello,\u202Fworld', '\u202F'],
    [`hello,\n  world`, '¶\n', '  '],
    ['hello,\tworld', ' \u2192\t'],
    // NSIS
    ['$Brand', '$Brand'],
    ['Welcome to $BrandName', '$BrandName'],
    ['I am $MyVar13', '$MyVar13'],
    // numbers
    ['Here is a 25 number', '25'],
    ['Here is a -25 number', '-25'],
    ['Here is a +25 number', '+25'],
    ['Here is a 25.00 number', '25.00'],
    ['Here is a 2,500.00 number', '2,500.00'],
    ['Here is a 1\u00A0000,99 number', '1\u00A0000,99'],
    ['3D game'],
    // CLI options
    ['Type --help for this help', '--help'],
    ['Short -S ones also', '-S'],
    // punctuation
    ['Pontoon™', '™'],
    ['9℉ OMG so cold', '9', '℉'],
    ['She had π cats', 'π'],
    ['Please use the correct quote: ʼ', 'ʼ'],
    ['Here comes the French: «', '«'],
    ['Gimme the €', '€'],
    ['Downloading…', '…'],
    ['Hello — Lisa', '—'],
    ['Hello – Lisa', '–'],
    ['Hello\u202Fworld', ' '],
    ['These, are not. Special: punctuation; marks! Or are "they"?'],
    // printf
    ['Hello %(name)s', '%(name)s'],
    ['Rolling %(number)d dices', '%(number)d'],
    ['Hello %(name)S', '%(name)S'],
    ['hello, {0}', '{0}'],
    ['hello, {name}', '{name}'],
    ['hello, {name!s}', '{name!s}'],
    ['hello, {someone.name}', '{someone.name}'],
    ['hello, {name[0]}', '{name[0]}'],
    ['100%% correct', '100', '%%'],
    ['There were %s', '%s'],
    ['There were %(number)d cows', '%(number)d'],
    ['There were %(cows.number)d cows', '%(cows.number)d'],
    ['There were %(number of cows)d cows', '%(number of cows)d'],
    ['There were %(number)03d cows', '%(number)03d'],
    ['There were %(number)*d cows', '%(number)*d'],
    ['There were %(number)3.1d cows', '%(number)3.1d'],
    ['There were %(number)Ld cows', '%(number)Ld'],
    ['path/to/file_%s.png', '%s'],
    ['path/to/%sfile.png', '%s'],
    ['There were %d cows', '%d'],
    ['There were %Id cows', '%Id'],
    ['There were %d %s', '%d', '%s'],
    ['%1$s was kicked by %2$s', '%1$s', '%2$s'],
    ['There were %Id cows', '%Id'],
    ["There were %'f cows", "%'f"],
    ['There were %#x cows', '%#x'],
    ['There were %3d cows', '%3d'],
    ['There were %33d cows', '%33d'],
    ['There were %*d cows', '%*d'],
    ['There were %1$d cows', '%1$d'],
    ['There were %\u00a0d cows', '\u00a0'],
    ['10 % complete', '10'],
    ['There were % d cows'],
    ['There were %(number) 3d cows'],
    ['Verified by %@', '%@'],
    ['Update login %1$@ for %2$@?', '%1$@', '%2$@'],
    // Qt
    ['Hello, %1', '%1'],
    ['Hello, %99', '%99'],
    ['Hello, %L1', '%L1'],
    // XML entities
    ['Welcome to &brandShortName;', '&brandShortName;'],
    ['hello, &#1234;', '&#1234;'],
    ['hello, &xDEAD;', '&xDEAD;'],
    // XML tags
    ['hello, <user>John', '<user>'],
    ['hello, </user>', '</user>'],
    ['hello, <user name="John">', '<user name="John">'],
    ["hello, <user name='John'>", "<user name='John'>"],
    ["hello, <user data-name='John'>", "<user data-name='John'>"],
    ['Happy <User.Birthday>!', '<User.Birthday>'],
    // i18next interpolations
    ['Hello, {{firstName}}', '{{firstName}}'],
    [
      'You currently have {{balance, money}} on your account!',
      '{{balance, money}}',
    ],
    ['Hi {{0}}. You will now be connected to {{1}}', '{{0}}', '{{1}}'],
  ];
  for (const [source, ...exp] of tests) {
    test(source, () => {
      const wrapper = mountMarker(source);
      const marks = wrapper.find('mark');
      expect(marks).toHaveLength(exp.length);
      for (let i = 0; i < exp.length; ++i) {
        expect(marks.at(i).hasClass('placeable'));
        expect(marks.at(i).text()).toEqual(exp[i]);
      }
    });
  }
});
