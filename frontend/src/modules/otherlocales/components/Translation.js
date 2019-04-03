/* @flow */

import React from 'react';
import { Localized } from 'fluent-react';

import './Translation.css';

import { WithPlaceables } from 'core/placeable';

import type { Navigation } from 'core/navigation';


type Props = {|
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
        this.props.updateEditorTranslation(this.props.translation.translation);
    }

    render() {
        const { translation, parameters, lastPreferred } = this.props;

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
                        target="_blank"
                        rel="noopener noreferrer"
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
                    <WithPlaceables>
                        { translation.translation }
                    </WithPlaceables>
                </p>
            </li>
        </Localized>;
    }
}
