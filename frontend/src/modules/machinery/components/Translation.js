/* @flow */

import * as React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Localized } from '@fluent/react';

import './ConcordanceSearch.css';
import './Translation.css';

import * as editor from 'core/editor';
import * as entities from 'core/entities';
import { GenericTranslation } from 'core/translation';

import ConcordanceSearch from './ConcordanceSearch';
import TranslationSource from './TranslationSource';

import type { MachineryTranslation } from 'core/api';

type Props = {|
    sourceString: string,
    translation: MachineryTranslation,
    index: number,
|};

/**
 * Render a Translation in the Machinery tab.
 *
 * Shows the original string and the translation, as well as a list of sources.
 * Similar translations (same original and translation) are shown only once
 * and their sources are merged.
 */
export default function Translation(
    props: Props,
): React.Element<React.ElementType> {
    const { index, sourceString, translation } = props;

    const dispatch = useDispatch();
    const isReadOnlyEditor = useSelector((state) =>
        entities.selectors.isReadOnlyEditor(state),
    );
    const locale = useSelector((state) => state.locale);

    const copyMachineryTranslation = editor.useCopyMachineryTranslation();
    const copyTranslationIntoEditor = React.useCallback(() => {
        dispatch(editor.actions.selectHelperElementIndex(index));
        copyMachineryTranslation(translation);
    }, [dispatch, index, translation, copyMachineryTranslation]);

    let className = 'translation';
    if (isReadOnlyEditor) {
        // Copying into the editor is not allowed
        className += ' cannot-copy';
    }

    const selectedHelperElementIndex = useSelector(
        (state) => state[editor.NAME].selectedHelperElementIndex,
    );
    const changeSource = useSelector(
        (state) => state[editor.NAME].changeSource,
    );
    const isSelected =
        changeSource === 'machinery' && selectedHelperElementIndex === index;
    if (isSelected) {
        // Highlight Machinery entries upon selection
        className += ' selected';
    }

    const translationRef = React.useRef();
    React.useEffect(() => {
        if (selectedHelperElementIndex === index) {
            // @ts-expect-error: What can be undefined here?
            translationRef.current?.scrollIntoView?.({
                behavior: 'smooth',
                block: 'nearest',
            });
        }
    }, [selectedHelperElementIndex, index]);

    return (
        <Localized id='machinery-Translation--copy' attrs={{ title: true }}>
            <li
                className={className}
                title='Copy Into Translation (Ctrl + Shift + Down)'
                onClick={copyTranslationIntoEditor}
                ref={translationRef}
            >
                {translation.sources.includes('concordance-search') ? (
                    <ConcordanceSearch
                        sourceString={sourceString}
                        translation={translation}
                    />
                ) : (
                    <>
                        <header>
                            {translation.quality && (
                                <span className='quality'>
                                    {translation.quality + '%'}
                                </span>
                            )}
                            <TranslationSource
                                translation={translation}
                                locale={locale}
                            />
                        </header>
                        <p className='original'>
                            {translation.sources.indexOf('caighdean') === -1 ? (
                                <GenericTranslation
                                    content={translation.original}
                                    diffTarget={sourceString}
                                />
                            ) : (
                                /*
                                 * Caighdean takes `gd` translations as input, so we shouldn't
                                 * diff it against the `en-US` source string.
                                 */
                                <GenericTranslation
                                    content={translation.original}
                                />
                            )}
                        </p>
                        <p
                            className='suggestion'
                            dir={locale.direction}
                            data-script={locale.script}
                            lang={locale.code}
                        >
                            <GenericTranslation
                                content={translation.translation}
                            />
                        </p>
                    </>
                )}
            </li>
        </Localized>
    );
}
