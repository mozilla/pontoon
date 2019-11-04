/* @flow */

import React from 'react';
import { Localized } from '@fluent/react';

import './Translation.css';

import { GenericTranslation } from 'core/translation';

import type { MachineryTranslation } from 'core/api';
import type { Locale } from 'core/locale';

import TranslationSource from './TranslationSource';


type Props = {|
    isReadOnlyEditor: boolean,
    locale: Locale,
    sourceString: string,
    translation: MachineryTranslation,
    updateEditorTranslation: (string, string) => void,
|};


/**
 * Render a Translation in the Machinery tab.
 *
 * Shows the original string and the translation, as well as a list of sources.
 * Similar translations (same original and translation) are shown only once
 * and their sources are merged.
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

        this.props.updateEditorTranslation(this.props.translation.translation, 'machinery');
    };

    render() {
        const { locale, sourceString, translation, isReadOnlyEditor } = this.props;

        const types = translation.sources;

        let className = 'translation';

        if (isReadOnlyEditor) {
            // Copying into the editor is not allowed
            className += ' cannot-copy';
        }

        return <Localized id="machinery-Translation--copy" attrs={{ title: true }}>
            <li
                className={ className }
                title="Copy Into Translation"
                onClick={ this.copyTranslationIntoEditor }
            >
                <header>
                    { !translation.quality ? null :
                        <span className="quality">{ translation.quality + '%' }</span>
                    }
                    <TranslationSource
                        translation={ translation }
                        locale={ locale }
                    />
                </header>
                <p className="original">
                    { types.indexOf('caighdean') === -1 ?
                        <GenericTranslation
                            content={ sourceString }
                            diffTarget={ translation.original }
                        />
                    :
                        /*
                         * Caighdean takes `gd` translations as input, so we shouldn't
                         * diff it against the `en-US` source string.
                         */
                         <GenericTranslation
                             content= { translation.original }
                         />
                    }
                </p>
                <p
                    className="suggestion"
                    dir={ locale.direction }
                    data-script={ locale.script }
                    lang={ locale.code }
                >
                    <GenericTranslation
                        content={ translation.translation }
                    />
                </p>
            </li>
        </Localized>;
    }
}
