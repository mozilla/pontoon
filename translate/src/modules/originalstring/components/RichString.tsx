import React from 'react';
import type { EditorField } from '~/context/Editor';
import { Highlight } from '~/modules/placeable/components/Highlight';
import type { TermState } from '~/modules/terms';

import './RichString.css';

/**
 * Show the original string of a Fluent entity in a rich interface.
 */
export function RichString({
  message,
  onClick,
  terms,
}: {
  message: EditorField[];
  onClick: (event: React.MouseEvent<HTMLElement>) => void;
  terms: TermState;
}): React.ReactElement<'table'> {
  return (
    <table className='original fluent-rich-string' onClick={onClick}>
      <tbody>
        {message.map(({ handle, id, labels }) => (
          <tr key={id}>
            <td>
              <label>
                {labels.map(({ label }) => (
                  <span key={label}>{label}</span>
                ))}
              </label>
            </td>
            <td>
              <span>
                <Highlight terms={terms}>{handle.current.value}</Highlight>
              </span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
