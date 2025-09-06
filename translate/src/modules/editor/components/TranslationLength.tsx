import React, { useContext } from 'react';
import { EditorData, EditorResult } from '../../../../src/context/Editor';
import { EntityView } from '../../../../src/context/EntityView';
import { getPlainMessage } from '../../../../src/utils/message';

import './TranslationLength.css';

/** Shows translation length vs. original string length.  */
export function TranslationLength(): React.ReactElement<'div'> | null {
  const { entity } = useContext(EntityView);
  const { sourceView } = useContext(EditorData);
  const edit = useContext(EditorResult);

  if (sourceView || edit.length !== 1) {
    return null;
  }

  const text = edit[0].value;
  const srcText = getPlainMessage(entity.original, entity.format);

  return (
    <div className='translation-length'>
      <div className='translation-vs-original'>
        <span>{text.length}</span>|<span>{srcText.length}</span>
      </div>
    </div>
  );
}
