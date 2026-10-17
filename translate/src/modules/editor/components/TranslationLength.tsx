import React, { useContext } from 'react';
import { EditorData, EditorResult } from '~/context/Editor';
import { useEntityEntry } from '~/context/EntityView';
import { Locale } from '~/context/Locale';
import { getPlainMessage } from '~/utils/message';
import { removeRtlMark } from '~/utils/message/rtlMark';

import './TranslationLength.css';

/** Shows translation length vs. original string length.  */
export function TranslationLength(): React.ReactElement<'div'> | null {
  const entry = useEntityEntry();
  const { direction } = useContext(Locale);
  const { fields, sourceView } = useContext(EditorData);
  // Included to re-render on input changes
  const result = useContext(EditorResult);

  if (sourceView || fields.length !== 1) {
    return null;
  }

  let text = result ? getPlainMessage(result) : '';
  if (direction === 'rtl') {
    // Not counting the invisible RLM that's added on save
    text = removeRtlMark(text);
  }
  const srcText = getPlainMessage(entry);

  return (
    <div className='translation-length'>
      <div className='translation-vs-original'>
        <span>{text.length}</span>|<span>{srcText.length}</span>
      </div>
    </div>
  );
}
