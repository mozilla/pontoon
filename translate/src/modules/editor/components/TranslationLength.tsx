import React, { useContext } from 'react';
import { EditorData, EditorResult } from '~/context/Editor';
import { EntityView } from '~/context/EntityView';
import { getPlainMessage } from '~/utils/message';

import './TranslationLength.css';

/** Shows translation length vs. original string length.  */
export function TranslationLength(): React.ReactElement<'div'> | null {
  const { entity } = useContext(EntityView);
  const { fields, sourceView } = useContext(EditorData);
  // Included to re-render on input changes
  const result = useContext(EditorResult);

  if (sourceView || fields.length !== 1) {
    return null;
  }

  const text = result ? getPlainMessage(result, entity.format) : '';
  const srcText = getPlainMessage(entity.original, entity.format);

  return (
    <div className='translation-length'>
      <div className='translation-vs-original'>
        <span>{text.length}</span>|<span>{srcText.length}</span>
      </div>
    </div>
  );
}
