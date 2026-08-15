import { Localized } from '@fluent/react';
import React, { useContext } from 'react';

import { EditorData, EditorResult } from '~/context/Editor';

import './MachinerySourceIndicator.css';

export function MachinerySourceIndicator() {
  const { fields, machinery, sourceView } = useContext(EditorData);
  // Included to re-render on input changes
  useContext(EditorResult);

  if (
    !machinery ||
    machinery.manual ||
    sourceView ||
    fields.length !== 1 ||
    machinery.translation !== fields[0].handle.current.value
  ) {
    return null;
  }

  return (
    <Localized
      id='editor-MachinerySourceIndicator--match'
      attrs={{ title: true }}
      elems={{ stress: <span className='stress' /> }}
    >
      <div className='tm-source' title='100% Translation Memory match'>
        {'<stress>100%</stress> MATCH'}
      </div>
    </Localized>
  );
}
