/* @flow */

import React from 'react';
import { Localized } from 'fluent-react';

import './Translation.css';

import { GenericTranslation } from 'core/translation';

import type { MachineryTranslation } from 'core/api';
import type { Locale } from 'core/locales';


type Props = {|
    isReadOnlyEditor: boolean,
    locale: Locale,
    sourceString: string,
    translation: MachineryTranslation,
    updateEditorTranslation: (string) => void,
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

        this.props.updateEditorTranslation(this.props.translation.translation);
    }

    render() {
        const { locale, sourceString, translation } = this.props;

        const types = translation.sources.map(source => source.type);

        return <Localized id="machinery-Translation--copy" attrs={{ title: true }}>
            <li
                className="translation"
                title="Copy Into Translation (Tab)"
                onClick={ this.copyTranslationIntoEditor }
            >
                <header>
                    { !translation.quality ? null :
                        <span className="quality">{ translation.quality + '%' }</span>
                    }
                    <ul className="sources">
                        { translation.sources.map((source, i) => <li key={ i }>
                            <a
                                className="translation-source"
                                href={ source.url }
                                title={ source.title }
                                target="_blank"
                                rel="noopener noreferrer"
                                onClick={ (e: SyntheticMouseEvent<>) => e.stopPropagation() }
                            >
                                <span>{ source.type }</span>
                                { !source.count ? null :
                                    <Localized
                                        id="machinery-Translation--number-occurrences"
                                        attrs={{ title: true }}
                                    >
                                        <sup title="Number of translation occurrences">
                                            { source.count }
                                        </sup>
                                    </Localized>
                                }
                            </a>
                        </li>) }
                    </ul>
                </header>
                <p className="original">
                    { types.indexOf('Caighdean') === -1 ?
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
