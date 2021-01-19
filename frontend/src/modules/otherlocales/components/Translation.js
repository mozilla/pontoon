/* @flow */

import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Localized } from '@fluent/react';
import { Link } from 'react-router-dom';

import './Translation.css';

import { TranslationProxy } from 'core/translation';

import * as editor from 'core/editor';
import * as entities from 'core/entities';
import type { Entity } from 'core/api';
import type { NavigationParams } from 'core/navigation';

type Props = {|
    entity: Entity,
    translation: Object,
    parameters: NavigationParams,
    index: number,
|};

/**
 * Render a Translation in the Locales tab.
 *
 * Show the translation of a given entity in a different locale, as well as the
 * locale and its code.
 */
export default function Translation(props: Props) {
    const { entity, translation, parameters, index } = props;

    const dispatch = useDispatch();
    const isReadOnlyEditor = useSelector((state) =>
        entities.selectors.isReadOnlyEditor(state),
    );

    let className = 'translation';
    if (isReadOnlyEditor) {
        // Copying into the editor is not allowed
        className += ' cannot-copy';
    }

    const editorState = useSelector((state) => state[editor.NAME]);
    const isSelected =
        editorState.changeSource === 'otherlocales' &&
        editorState.selectedHelperElementIndex === index;
    if (isSelected) {
        // Highlight other locale entries upon selection
        className += ' selected';
    }

    const copyOtherLocaleTranslation = editor.useCopyOtherLocaleTranslation();
    const copyTranslationIntoEditor = React.useCallback(() => {
        dispatch(editor.actions.selectHelperElementIndex(index));
        copyOtherLocaleTranslation(translation);
    }, [dispatch, index, translation, copyOtherLocaleTranslation]);

    const translationRef = React.useRef();
    React.useEffect(() => {
        if (
            editorState.selectedHelperElementIndex === index &&
            translationRef.current
        ) {
            translationRef.current.scrollIntoView({
                behavior: 'smooth',
                block: 'nearest',
            });
        }
    }, [editorState.selectedHelperElementIndex, index]);

    return (
        <Localized id='otherlocales-Translation--copy' attrs={{ title: true }}>
            <li
                className={className}
                title='Copy Into Translation (Ctrl + Shift + Down)'
                onClick={copyTranslationIntoEditor}
                ref={translationRef}
            >
                <header>
                    {translation.locale.code === 'en-US' ? (
                        <div>
                            {translation.locale.name}
                            <span>{translation.locale.code}</span>
                        </div>
                    ) : (
                        <Localized
                            id='otherlocales-Translation--header-link'
                            attrs={{ title: true }}
                            vars={{
                                locale: translation.locale.name,
                                code: translation.locale.code,
                            }}
                        >
                            <Link
                                to={`/${translation.locale.code}/${parameters.project}/${parameters.resource}/?string=${parameters.entity}`}
                                target='_blank'
                                rel='noopener noreferrer'
                                title='Open string in { $locale } ({ $code })'
                                onClick={(e: SyntheticMouseEvent<>) =>
                                    e.stopPropagation()
                                }
                            >
                                {translation.locale.name}
                                <span>{translation.locale.code}</span>
                            </Link>
                        </Localized>
                    )}
                </header>
                <p
                    lang={translation.locale.code}
                    dir={translation.locale.direction}
                    script={translation.locale.script}
                >
                    <TranslationProxy
                        content={translation.translation}
                        format={entity.format}
                    />
                </p>
            </li>
        </Localized>
    );
}
