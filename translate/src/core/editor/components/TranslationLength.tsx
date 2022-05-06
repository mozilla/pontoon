import React from 'react';

import './TranslationLength.css';

type Props = {
  comment: string;
  format: string;
  original: string;
  translation: string;
};

/**
 * Shows translation length vs. original string length, or countdown.
 *
 * Countdown is currently only supported for LANG strings, which use special
 * syntax in the comment to define maximum translation length. MAX_LENGTH
 * is provided for strings without HTML tags, so they need to be stripped.
 */
export function TranslationLength({
  comment,
  format,
  original,
  translation,
}: Props): React.ReactElement<'div'> {
  const match = format === 'lang' && comment.match(/^MAX_LENGTH: (\S+)/);
  if (match) {
    const limit = parseInt(match[1], 10);

    // Source: https://stackoverflow.com/a/47140708
    const doc = new DOMParser().parseFromString(translation, 'text/html');
    const translationLength = doc.body?.textContent?.length ?? 0;
    const countdown = limit - translationLength;

    return (
      <div className='translation-length'>
        <div className='countdown'>
          <span className={countdown < 0 ? 'overflow' : undefined}>
            {countdown}
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className='translation-length'>
      <div className='translation-vs-original'>
        <span>{translation.length}</span>|<span>{original.length}</span>
      </div>
    </div>
  );
}
