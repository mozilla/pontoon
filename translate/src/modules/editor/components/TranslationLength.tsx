import React, { useContext } from 'react';
import { EditorData, EditorResult } from '~/context/Editor';
import { useEntityEntry } from '~/context/EntityView';
import { getPlainMessage } from '~/utils/message';

import './TranslationLength.css';

/** Shows translation length vs. original string length.  */
export function TranslationLength(): React.ReactElement<'div'> | null {
  const entry = useEntityEntry();
  const { fields, sourceView } = useContext(EditorData);
  // Included to re-render on input changes
  const result = useContext(EditorResult);

  if (sourceView || fields.length !== 1) {
    return null;
  }

  const text = result ? getPlainMessage(result) : '';
  const srcText = getPlainMessage(entry);

  return (
    <div className='translation-length'>
      <div className='translation-vs-original'>
        <span>{text.length}</span>|<span>{srcText.length}</span>
      </div>
    </div>
  );
}
