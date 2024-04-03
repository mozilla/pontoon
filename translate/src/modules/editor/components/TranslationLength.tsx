import React, { useContext } from 'react';
import { EditorData, EditorResult } from '~/context/Editor';
import { EntityView, useEntitySource } from '~/context/EntityView';
import { getPlainMessage } from '~/utils/message';

import './TranslationLength.css';

/** Shows translation length vs. original string length.  */
export function TranslationLength(): React.ReactElement<'div'> | null {
  const { entity } = useContext(EntityView);
  const source = useEntitySource();
  const { sourceView } = useContext(EditorData);
  const edit = useContext(EditorResult);

  if (sourceView || edit.length !== 1) {
    return null;
  }

  const text = edit[0].value;
  const srcText = getPlainMessage(source, entity.format);

  return (
    <div className='translation-length'>
      <div className='translation-vs-original'>
        <span>{text.length}</span>|<span>{srcText.length}</span>
      </div>
    </div>
  );
}
