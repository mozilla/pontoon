import { Localized } from '@fluent/react';
import React, { useContext } from 'react';

import { EditorData, EditorResult } from '~/context/Editor';

import './MachinerySourceIndicator.css';

export function MachinerySourceIndicator() {
  const { machinery, sourceView } = useContext(EditorData);
  const edit = useContext(EditorResult);

  if (
    !machinery ||
    machinery.manual ||
    sourceView ||
    edit.length !== 1 ||
    machinery.translation !== edit[0].value
  ) {
    return null;
  }

  return (
    <Localized
      id='editor-MachinerySourceIndicator--text'
      elems={{ stress: <span className='stress' /> }}
    >
      <div className='tm-source'>
        {'<stress>100%</stress> MATCH FROM TRANSLATION MEMORY'}
      </div>
    </Localized>
  );
}
