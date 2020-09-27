/* @flow */

import React from 'react';
import { Localized } from '@fluent/react';
import { Link } from 'react-router-dom';

import './Translation.css';

import { TranslationProxy } from 'core/translation';

import type { Entity } from 'core/api';
import type { NavigationParams } from 'core/navigation';

type Props = {|
    entity: Entity,
    isReadOnlyEditor: boolean,
    translation: Object,
    parameters: NavigationParams,
    updateEditorTranslation: (string, string) => void,
|};

/**
 * Render a Translation in the Locales tab.
 *
 * Show the translation of a given entity in a different locale, as well as the
 * locale and its code.
 */
export default class Translation extends React.Component<Props> {
    copyTranslationIntoEditor = () => {
        if (this.props.isReadOnlyEditor) {
            return;
        }

        // Ignore if selecting text
        if (window.getSelection().toString()) {
            return;
        }

        this.props.updateEditorTranslation(
            this.props.translation.translation,
            'otherlocales',
        );
    };

    render() {
        const {
            entity,
            translation,
            parameters,
            isReadOnlyEditor,
        } = this.props;

        let className = 'translation';

        if (isReadOnlyEditor) {
            // Copying into the editor is not allowed
            className += ' cannot-copy';
        }

        return (
            <Localized
                id='otherlocales-Translation--copy'
                attrs={{ title: true }}
            >
                <li
                    className={className}
                    title='Copy Into Translation'
                    onClick={this.copyTranslationIntoEditor}
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
}
