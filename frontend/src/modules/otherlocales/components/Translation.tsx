import * as React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Localized } from '@fluent/react';
import { Link } from 'react-router-dom';

import './Translation.css';

import { TranslationProxy } from 'core/translation';

import * as editor from 'core/editor';
import * as entities from 'core/entities';
import type { Entity, OtherLocaleTranslation } from 'core/api';
import type { NavigationParams } from 'core/navigation';

type Props = {
    entity: Entity;
    translation: OtherLocaleTranslation;
    parameters: NavigationParams;
    index: number;
};

/**
 * Render a Translation in the Locales tab.
 *
 * Show the translation of a given entity in a different locale, as well as the
 * locale and its code.
 */
export default function Translation(
    props: Props,
): React.ReactElement<React.ElementType> {
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

    const selectedHelperElementIndex = useSelector(
        (state) => state[editor.NAME].selectedHelperElementIndex,
    );
    const changeSource = useSelector(
        (state) => state[editor.NAME].changeSource,
    );
    const isSelected =
        changeSource === 'otherlocales' && selectedHelperElementIndex === index;

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
        if (selectedHelperElementIndex === index) {
            const mediaQuery = window.matchMedia(
                '(prefers-reduced-motion: reduce)',
            );
            const behavior = mediaQuery.matches ? 'auto' : 'smooth';
            // @ts-expect-error: What can be undefined here?
            translationRef.current?.scrollIntoView?.({
                behavior: behavior,
                block: 'nearest',
            });
        }
    }, [selectedHelperElementIndex, index]);

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
                                onClick={(e: React.MouseEvent) =>
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
                    data-script={translation.locale.script}
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
