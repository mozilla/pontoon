import type { Message, Pattern, Variant } from 'messageformat';
import React from 'react';

import { Highlight } from '~/core/placeable/components/Highlight';
import type { TermState } from '~/core/term';
import { MessageEntry, serializePattern } from '~/utils/message';

import './RichString.css';

function RichPattern({
  label,
  pattern,
  terms,
  variant,
}: {
  label?: string;
  pattern: Pattern;
  terms: TermState;
  variant?: string;
}) {
  const value = serializePattern(pattern);
  return (
    <tr>
      <td>
        {label && variant ? (
          <label>
            <span>{label}</span>
            <span className='divider'>&middot;</span>
            <span>{variant}</span>
          </label>
        ) : (
          <label>{label || variant}</label>
        )}
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
  label,
  message,
  terms,
}: {
  label?: string;
  message: Message | null;
  terms: TermState;
}) {
  switch (message?.type) {
    case 'message':
      return (
        <RichPattern label={label} pattern={message.pattern} terms={terms} />
      );
    case 'select':
      return (
        <>
          {message.variants.map(({ keys, value }) => {
            const variant = keys
              .map((key) => ('value' in key ? key.value : 'other'))
              .join(' / ');
            return (
              <RichPattern
                key={variant}
                label={label}
                pattern={value}
                terms={terms}
                variant={variant}
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
      label={attributes ? 'Value' : undefined}
      message={value}
      terms={terms}
    />,
  ];
  if (attributes) {
    for (const [name, attr] of attributes) {
      rows.push(
        <RichMessage key={name} label={name} message={attr} terms={terms} />,
      );
    }
  }
  return (
    <table className='original fluent-rich-string' onClick={onClick}>
      <tbody>{rows}</tbody>
    </table>
  );
}
