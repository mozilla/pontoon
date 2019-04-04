/* @flow */

import React from 'react';
import { Localized } from 'fluent-react';

import './Translation.css';

import api from 'core/api';

import { withDiff } from 'core/diff';
import { WithPlaceables, WithPlaceablesNoLeadingSpace } from 'core/placeable';

import type { DbEntity } from 'modules/entitieslist';
import type { Locale } from 'core/locales';


type Props = {|
    entity: DbEntity,
    isReadOnlyEditor: boolean,
    locale: Locale,
    translation: api.types.MachineryTranslation,
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
        this.props.updateEditorTranslation(this.props.translation.translation);
    }

    render() {
        const { entity, locale, translation } = this.props;

        const TranslationPlaceablesDiff = withDiff(WithPlaceablesNoLeadingSpace);

        return <Localized id="machinery-translation-copy" attrs={{ title: true }}>
            <li
                className="translation"
                title="Copy Into Translation (Tab)"
                onClick={ this.copyTranslationIntoEditor }
            >
                <header>
                    { !translation.quality ? null :
                        <span className="stress">{ translation.quality + '%' }</span>
                    }
                    <ul className="sources">
                        { translation.sources.map((source, i) => <li key={ i }>
                            <a
                                className="translation-source"
                                href={ source.url }
                                title={ source.title }
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                <span>{ source.type }</span>
                                { !source.count ? null :
                                    <Localized
                                        id="machinery-translation-number-occurrences"
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
                    <TranslationPlaceablesDiff
                        diffTarget={ translation.original }
                    >
                        { entity.original }
                    </TranslationPlaceablesDiff>
                </p>
                <p
                    className="suggestion"
                    dir={ locale.direction }
                    data-script={ locale.script }
                    lang={ locale.code }
                >
                    <WithPlaceables>
                        { translation.translation }
                    </WithPlaceables>
                </p>
            </li>
        </Localized>;
    }
}
