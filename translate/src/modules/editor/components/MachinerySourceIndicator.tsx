import { Localized } from '@fluent/react';
import React, { useContext } from 'react';

import { EditorData, EditorResult } from '~/context/Editor';
import { pojoEquals } from '~/utils/pojo';

import './MachinerySourceIndicator.css';

export function MachinerySourceIndicator() {
  const { autofilled } = useContext(EditorData);
  const result = useContext(EditorResult);

  if (!autofilled || !pojoEquals(autofilled, result)) {
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
