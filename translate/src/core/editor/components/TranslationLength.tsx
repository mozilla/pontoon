import * as React from 'react';

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
export default class TranslationLength extends React.Component<Props> {
    getLimit(): null | number {
        const { comment, format } = this.props;

        if (format !== 'lang') {
            return null;
        }

        const parts = comment.split('\n');

        if (parts[0].startsWith('MAX_LENGTH')) {
            try {
                return parseInt(
                    parts[0].split('MAX_LENGTH: ')[1].split(' ')[0],
                    10,
                );
            } catch (e) {
                // Catch unexpected comment structure
            }
        }

        return null;
    }

    // Only used for countdown.
    // Source: https://stackoverflow.com/a/47140708
    stripHTML(translation: string): string {
        const doc = new DOMParser().parseFromString(translation, 'text/html');

        if (!doc.body) {
            return '';
        }

        return doc.body.textContent || '';
    }

    render(): React.ReactElement<'div'> {
        const { original, translation } = this.props;

        const limit = this.getLimit();
        const translationLength = this.stripHTML(translation).length;
        const countdown = limit !== null ? limit - translationLength : null;

        return (
            <div className='translation-length'>
                {countdown !== null ? (
                    <div className='countdown'>
                        <span className={countdown < 0 ? 'overflow' : null}>
                            {countdown}
                        </span>
                    </div>
                ) : (
                    <div className='translation-vs-original'>
                        <span>{translation.length}</span>|
                        <span>{original.length}</span>
                    </div>
                )}
            </div>
        );
    }
}
