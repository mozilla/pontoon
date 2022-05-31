import ftl from '@fluent/dedent';

import { parseEntry } from './parser';

describe('parser', () => {
  it('does not modify value with single element', () => {
    const res = parseEntry('title = My Title');

    expect(res.value.elements).toHaveLength(1);
    expect(res.value.elements[0].value).toEqual('My Title');
  });

  it('does not modify attributes with single element', () => {
    const res = parseEntry(ftl`
      title =
          .foo = Bar
      `);

    expect(res.attributes).toHaveLength(1);
    expect(res.attributes[0].value.elements).toHaveLength(1);
    expect(res.attributes[0].value.elements[0].value).toEqual('Bar');
  });

  it('does not modify value with a single select expression', () => {
    const input = ftl`
      my-entry =
          { PLATFORM() ->
              [variant] Hello!
             *[another-variant] World!
          }
      `;
    const res = parseEntry(input);

    expect(res.value.elements).toHaveLength(1);
    expect(
      res.value.elements[0].expression.variants[0].value.elements[0].value,
    ).toEqual('Hello!');
    expect(
      res.value.elements[0].expression.variants[1].value.elements[0].value,
    ).toEqual('World!');
  });

  it('flattens a value with several elements', () => {
    const res = parseEntry('title = My { $awesome } Title');

    expect(res.value.elements).toHaveLength(1);
    expect(res.value.elements[0].value).toEqual('My { $awesome } Title');
  });

  it('flattens an attribute with several elements', () => {
    const res = parseEntry(ftl`
      title =
          .foo = Bar { -foo } Baz
      `);

    expect(res.attributes).toHaveLength(1);
    expect(res.attributes[0].value.elements).toHaveLength(1);
    expect(res.attributes[0].value.elements[0].value).toEqual(
      'Bar { -foo } Baz',
    );
  });

  it('flattens value and attributes', () => {
    const input = ftl`
      batman = The { $dark } Knight
          .weapon = Brain and { -wayne-enterprise }
          .history = Lost { 2 } parents, has { 1 } "$alfred"
      `;
    const res = parseEntry(input);

    expect(res.value.elements).toHaveLength(1);
    expect(res.value.elements[0].value).toEqual('The { $dark } Knight');

    expect(res.attributes).toHaveLength(2);

    expect(res.attributes[0].value.elements).toHaveLength(1);
    expect(res.attributes[0].value.elements[0].value).toEqual(
      'Brain and { -wayne-enterprise }',
    );

    expect(res.attributes[1].value.elements).toHaveLength(1);
    expect(res.attributes[1].value.elements[0].value).toEqual(
      'Lost { 2 } parents, has { 1 } "$alfred"',
    );
  });

  it('flattens values surrounding a select expression and select expression variants', () => {
    const input = ftl`
      my-entry =
          There { $num ->
              [one] is one email
             *[other] are { $num } emails
          } for { $awesome } { $gender ->
             *[masculine] him
              [feminine] her
          }
      `;
    const res = parseEntry(input);

    expect(res.value.elements).toHaveLength(3);

    const selEmail = res.value.elements[0].expression;
    expect(selEmail.variants[0].value.elements[0].value).toEqual(
      'There is one email for { $awesome }',
    );
    expect(selEmail.variants[1].value.elements[0].value).toEqual(
      'There are { $num } emails for { $awesome }',
    );

    expect(res.value.elements[1].value).toEqual(' ');

    const selGender = res.value.elements[2].expression;
    expect(selGender.variants[0].value.elements[0].value).toEqual('him');
    expect(selGender.variants[1].value.elements[0].value).toEqual('her');
  });
});
