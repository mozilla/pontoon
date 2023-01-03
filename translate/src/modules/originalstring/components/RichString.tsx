import type { Message, Pattern } from 'messageformat';
import React from 'react';

import { Highlight } from '~/core/placeable/components/Highlight';
import type { TermState } from '~/core/term';
import { MessageEntry, serializePattern } from '~/utils/message';

import './RichString.css';

function RichPattern({
  labels,
  pattern,
  terms,
}: {
  labels: string[];
  pattern: Pattern;
  terms: TermState;
}) {
  const value = serializePattern(pattern);
  return (
    <tr>
      <td>
        <label>
          {labels.map((label) => (
            <span key={label}>{label}</span>
          ))}
        </label>
      </td>
      <td>
        <span>
          <Highlight fluent terms={terms}>
            {value}
          </Highlight>
        </span>
      </td>
    </tr>
  );
}

function RichMessage({
  labels,
  message,
  terms,
}: {
  labels: string[];
  message: Message | null;
  terms: TermState;
}) {
  switch (message?.type) {
    case 'message':
      return (
        <RichPattern labels={labels} pattern={message.pattern} terms={terms} />
      );
    case 'select':
      return (
        <>
          {message.variants.map(({ keys, value }) => {
            const variant = keys.map((key) =>
              'value' in key ? key.value : 'other',
            );
            return (
              <RichPattern
                key={variant.join()}
                labels={labels.concat(variant)}
                pattern={value}
                terms={terms}
              />
            );
          })}
        </>
      );
  }
  return null;
}

/**
 * Show the original string of a Fluent entity in a rich interface.
 */
export function RichString({
  entry: { value, attributes },
  onClick,
  terms,
}: {
  entry: MessageEntry;
  onClick: (event: React.MouseEvent<HTMLElement>) => void;
  terms: TermState;
}): React.ReactElement<'table'> {
  const rows = [
    <RichMessage
      key='-'
      labels={attributes ? ['Value'] : []}
      message={value}
      terms={terms}
    />,
  ];
  if (attributes) {
    for (const [name, attr] of attributes) {
      rows.push(
        <RichMessage key={name} labels={[name]} message={attr} terms={terms} />,
      );
    }
  }
  return (
    <table className='original fluent-rich-string' onClick={onClick}>
      <tbody>{rows}</tbody>
    </table>
  );
}
