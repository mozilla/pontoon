import { Localized } from '@fluent/react';
import React, { useContext } from 'react';

import { EditorData, EditorResult } from '~/context/Editor';
import { Locale } from '~/context/Locale';
import { hasAddedRtlMark, needsRtlMark } from '~/utils/message/rtlMark';
import { pojoEquals } from '~/utils/pojo';

import './RtlMarkIndicator.css';

/**
 * Shows when a right-to-left mark will be added to the start of the translation.
 * Unchanged translations are not saved again, so it's not shown for them.
 * https://github.com/mozilla/pontoon/issues/3236
 */
export function RtlMarkIndicator() {
  const { direction } = useContext(Locale);
  const { fields, initial, sourceView } = useContext(EditorData);
  const result = useContext(EditorResult);

  // In the source view, the mark is visible in the result
  const show =
    direction === 'rtl' &&
    !(result && pojoEquals(initial, result)) &&
    (sourceView
      ? !!result && hasAddedRtlMark(result)
      : fields.some((field) => needsRtlMark(field.handle.current.value)));
  if (!show) {
    return null;
  }

  return (
    <Localized id='editor-RtlMarkIndicator--rlm' attrs={{ title: true }}>
      <div
        className='rtl-mark'
        title='A right-to-left mark (RLM) will be added at the start of this translation, so that it is displayed right-to-left. To prevent this, start the translation with a left-to-right mark (LRM).'
      >
        RLM
      </div>
    </Localized>
  );
}
