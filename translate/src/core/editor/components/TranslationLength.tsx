import React, { useContext } from 'react';
import { EditorData } from '~/context/Editor';
import { EntityView, useEntitySource } from '~/context/EntityView';
import { getSimplePreview } from '~/core/utils/fluent';

import './TranslationLength.css';

/**
 * Shows translation length vs. original string length, or countdown.
 *
 * Countdown is currently only supported for LANG strings, which use special
 * syntax in the comment to define maximum translation length. MAX_LENGTH
 * is provided for strings without HTML tags, so they need to be stripped.
 */
export function TranslationLength(): React.ReactElement<'div'> | null {
  const { entity } = useContext(EntityView);
  const source = useEntitySource();
  const { value, view } = useContext(EditorData);

  if (view !== 'simple') {
    return null;
  }

  const text = typeof value === 'string' ? value : getSimplePreview(value);

  const maxLength =
    entity.format === 'lang' && entity.comment.match(/^MAX_LENGTH: (\d+)/);
  if (maxLength) {
    const limit = parseInt(maxLength[1]);

    // Source: https://stackoverflow.com/a/47140708
    const doc = new DOMParser().parseFromString(text, 'text/html');
    const length = doc.body?.textContent?.length ?? 0;
    return (
      <div className='translation-length'>
        <div className='countdown'>
          <span className={length > limit ? 'overflow' : undefined}>
            {limit - length}
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className='translation-length'>
      <div className='translation-vs-original'>
        <span>{text.length}</span>|<span>{source.length}</span>
      </div>
    </div>
  );
}
