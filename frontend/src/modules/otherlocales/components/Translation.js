/* @flow */

import React from 'react';
import { Localized } from 'fluent-react';

import './Translation.css';

import { TranslationProxy } from 'core/translation';

import type { Entity } from 'core/api';
import type { Navigation } from 'core/navigation';


type Props = {|
    entity: Entity,
    isReadOnlyEditor: boolean,
    translation: Object,
    parameters: Navigation,
    updateEditorTranslation: (string) => void,
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

        this.props.updateEditorTranslation(this.props.translation.translation);
    }

    render() {
        const { entity, translation, parameters, lastPreferred } = this.props;

        const className = lastPreferred ? 'translation last-preferred' : 'translation';

        return <Localized id='otherlocales-translation-copy' attrs={{ title: true }}>
            <li
                className={ className }
                title='Copy Into Translation (Tab)'
                onClick={ this.copyTranslationIntoEditor }
            >
                <header>
                    <a
                        href={ `/translate/${translation.code}/${parameters.project}/${parameters.resource}/?string=${parameters.entity}` }
                        target='_blank'
                        rel='noopener noreferrer'
                        onClick={ (e: SyntheticMouseEvent<>) => e.stopPropagation() }
                    >
                        { translation.locale }
                        <span>{ translation.code }</span>
                    </a>
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
