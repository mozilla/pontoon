import { Localized } from '@fluent/react';
import React, { useContext } from 'react';

import { EditorData } from '~/context/Editor';

import './MachinerySourceIndicator.css';

export function MachinerySourceIndicator() {
  const { machinery, sourceView, value } = useContext(EditorData);

  if (
    !machinery ||
    machinery.manual ||
    sourceView ||
    value.length !== 1 ||
    machinery.translation !== value[0].value
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
