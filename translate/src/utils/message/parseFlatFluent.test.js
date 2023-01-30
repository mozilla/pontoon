import ftl from '@fluent/dedent';

import { parseFlatFluent } from './parseFlatFluent';

describe('parseFlatFluent', () => {
  it('does not modify value with single element', () => {
    const res = parseFlatFluent('title = My Title');

    expect(res.value.elements).toHaveLength(1);
    expect(res.value.elements[0].value).toEqual('My Title');
  });

  it('does not modify attributes with single element', () => {
    const res = parseFlatFluent(ftl`
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
    const res = parseFlatFluent(input);

    expect(res.value.elements).toHaveLength(1);
    expect(
      res.value.elements[0].expression.variants[0].value.elements[0].value,
    ).toEqual('Hello!');
    expect(
      res.value.elements[0].expression.variants[1].value.elements[0].value,
    ).toEqual('World!');
  });

  it('flattens a value with several elements', () => {
    const res = parseFlatFluent('title = My { $awesome } Title');

    expect(res.value.elements).toHaveLength(1);
    expect(res.value.elements[0].value).toEqual('My { $awesome } Title');
  });

  it('flattens an attribute with several elements', () => {
    const res = parseFlatFluent(ftl`
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
    const res = parseFlatFluent(input);

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
});
