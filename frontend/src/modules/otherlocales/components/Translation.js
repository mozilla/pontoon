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
    lastPreferred: boolean,
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

        this.props.updateEditorTranslation(this.props.translation.translation, 'otherlocales');
    }

    render() {
        const { entity, translation, parameters, lastPreferred, isReadOnlyEditor } = this.props;

        let className = lastPreferred ? 'translation last-preferred' : 'translation';

        if (isReadOnlyEditor) {
            // Copying into the editor is not allowed
            className += ' cannot-copy'
        }

        return <Localized id='otherlocales-Translation--copy' attrs={{ title: true }}>
            <li
                className={ className }
                title='Copy Into Translation'
                onClick={ this.copyTranslationIntoEditor }
            >
                <header>
                    <Localized
                        id='otherlocales-Translation--header-link'
                        attrs={{ title: true }}
                        $locale={ translation.locale }
                        $code={ translation.code }
                    >
                        <Link
                            to={ `/${translation.code}/${parameters.project}/${parameters.resource}/?string=${parameters.entity}` }
                            target='_blank'
                            rel='noopener noreferrer'
                            title='Open string in { $locale } ({ $code })'
                            onClick={ (e: SyntheticMouseEvent<>) => e.stopPropagation() }
                        >
                            { translation.locale }
                            <span>{ translation.code }</span>
                        </Link>
                    </Localized>
                </header>
                <p
                    lang={ translation.code }
                    dir={ translation.direction }
                    script={ translation.script }
                >
                    <TranslationProxy
                        content={ translation.translation }
                        format={ entity.format }
                    />
                </p>
            </li>
        </Localized>;
    }
}
