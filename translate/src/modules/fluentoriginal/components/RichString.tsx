import {
  Attribute,
  PatternElement,
  Pattern,
  serializeVariantKey,
} from '@fluent/syntax';
import React from 'react';

import type { Entity } from '~/api/entity';
import { getMarker, TermState } from '~/core/term';
import { flattenMessage, parser } from '~/core/utils/fluent';

import './RichString.css';

type Props = {
  readonly entity: Entity;
  readonly terms: TermState;
  readonly handleClickOnPlaceable: (
    event: React.MouseEvent<HTMLParagraphElement>,
  ) => void;
};

function renderItem(
  value: string,
  label: string,
  key: string,
  terms: TermState,
  className?: string,
  attributeName?: string,
): React.ReactNode {
  const TermsAndPlaceablesMarker = getMarker(terms, true);

  return (
    <tr key={key} className={className}>
      <td>
        {attributeName ? (
          <label>
            <span className='attribute-label'>{attributeName}</span>
            <span className='divider'>&middot;</span>
            <span className='label'>{label}</span>
          </label>
        ) : (
          <label>{label}</label>
        )}
      </td>
      <td>
        <span>
          <TermsAndPlaceablesMarker>{value}</TermsAndPlaceablesMarker>
        </span>
      </td>
    </tr>
  );
}

function renderElements(
  elements: Array<PatternElement>,
  terms: TermState,
  attributeName: string | undefined,
): React.ReactNode {
  let indent = false;
  return elements.map((element, index) => {
    if (
      element.type === 'Placeable' &&
      element.expression &&
      element.expression.type === 'SelectExpression'
    ) {
      const variantItems = element.expression.variants.map((variant, i) => {
        if (typeof variant.value.elements[0].value !== 'string') {
          return null;
        }

        return renderItem(
          variant.value.elements[0].value,
          serializeVariantKey(variant.key),
          [index, i].join('-'),
          terms,
          indent ? 'indented' : undefined,
          attributeName,
        );
      });
      indent = false;
      return variantItems;
    } else {
      if (typeof element.value !== 'string') {
        return null;
      }

      // When rendering Message attribute, set label to attribute name.
      // When rendering Message value, set label to "Value".
      const label = attributeName || 'Value';

      indent = true;
      return renderItem(element.value, label, index.toString(), terms);
    }
  });
}

function renderValue(
  value: Pattern | null | undefined,
  terms: TermState,
  attributeName?: string,
): React.ReactNode {
  if (!value) {
    return null;
  }

  return renderElements(value.elements, terms, attributeName);
}

function renderAttributes(
  attributes: Array<Attribute> | null | undefined,
  terms: TermState,
): React.ReactNode {
  if (!attributes) {
    return null;
  }

  return attributes.map((attribute: Attribute) => {
    return renderValue(attribute.value, terms, attribute.id.name);
  });
}

/**
 * Show the original string of a Fluent entity in a rich interface.
 */
export function RichString(props: Props): React.ReactElement<'table'> {
  const message = flattenMessage(parser.parseEntry(props.entity.original));
  // Safeguard against non-translatable entries
  if (message.type !== 'Message' && message.type !== 'Term') {
    throw new Error(`Unexpected type '${message.type}' in RichString`);
  }

  return (
    <table
      className='original fluent-rich-string'
      onClick={props.handleClickOnPlaceable}
    >
      <tbody>
        {renderValue(message.value, props.terms)}
        {renderAttributes(message.attributes, props.terms)}
      </tbody>
    </table>
  );
}
