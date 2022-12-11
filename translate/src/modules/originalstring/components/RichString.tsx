import {
  Attribute,
  PatternElement,
  Pattern,
  serializeVariantKey,
  Entry,
} from '@fluent/syntax';
import React from 'react';

import { Marked } from '~/core/placeable/components/Marked';
import type { TermState } from '~/core/term';

import './RichString.css';

function renderItem(
  value: string,
  label: string,
  key: string,
  terms: TermState,
  className?: string,
  attributeName?: string,
): React.ReactNode {
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
          <Marked fluent terms={terms}>
            {value}
          </Marked>
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

type Props = {
  message: Entry;
  onClick: (event: React.MouseEvent<HTMLElement>) => void;
  terms: TermState;
};

/**
 * Show the original string of a Fluent entity in a rich interface.
 */
export function RichString({
  message,
  onClick,
  terms,
}: Props): React.ReactElement<'table'> {
  // Safeguard against non-translatable entries
  if (message.type !== 'Message' && message.type !== 'Term') {
    throw new Error(`Unexpected type '${message.type}' in RichString`);
  }

  return (
    <table className='original fluent-rich-string' onClick={onClick}>
      <tbody>
        {renderValue(message.value, terms)}
        {renderAttributes(message.attributes, terms)}
      </tbody>
    </table>
  );
}
