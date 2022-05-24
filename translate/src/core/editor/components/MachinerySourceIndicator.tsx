import { Localized } from '@fluent/react';
import React, { useContext } from 'react';

import { EditorData } from '~/context/Editor';

import './MachinerySourceIndicator.css';

export function MachinerySourceIndicator() {
  const { machinery, value, view } = useContext(EditorData);

  if (
    !machinery ||
    machinery.manual ||
    machinery.translation !== value ||
    view !== 'simple'
  ) {
    return null;
  }

  return (
    <Localized id='editor-MachinerySourceIndicator--text'>
      <div className='tm-source'>Perfect match from translation memory</div>
    </Localized>
  );
}
