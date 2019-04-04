/* @flow */

import React from 'react';
import { Localized } from 'fluent-react';

import './Machinery.css';

import Translation from './Translation';

import type { DbEntity } from 'modules/entitieslist';
import type { Locale } from 'core/locales';
import type { MachineryState } from '..';


type Props = {|
    entity: DbEntity,
    isReadOnlyEditor: boolean,
    locale: ?Locale,
    machinery: MachineryState,
    updateEditorTranslation: (string) => void,
    fetchMachinery: (string) => void,
|};


/**
 * Show translations from machines.
 *
 * Shows a sorted list of translations for the same original string, or similar
 * strings, coming from various sources like Translation Memory or
 * third-party Machine Translation.
 */
export default class Machinery extends React.Component<Props> {
    handleShortcuts = (event: SyntheticKeyboardEvent<>) => {
        const key = event.keyCode;

        // On Enter, trigger custom Machinery search
        if (key === 13) {
            event.preventDefault();
            this.props.fetchMachinery(event.currentTarget.value);
        }
    }

    render() {
        const {
            entity,
            isReadOnlyEditor,
            locale,
            machinery,
            updateEditorTranslation,
        } = this.props;

        if (!locale) {
            return null;
        }

        return <section className="machinery">
            <div className="search-wrapper clearfix">
                <div className="icon fa fa-search"></div>
                <Localized id="machinery-machinery-search-placeholder" attrs={{ placeholder: true }}>
                    <input
                        type="search"
                        autoComplete="off"
                        placeholder="Type to search machinery"
                        onKeyDown={ this.handleShortcuts }
                    />
                </Localized>
            </div>
            <ul>
                { machinery.translations.map((translation, index) => {
                    return <Translation
                        entity={ entity }
                        isReadOnlyEditor={ isReadOnlyEditor }
                        locale={ locale }
                        translation={ translation }
                        updateEditorTranslation={ updateEditorTranslation }
                        key={ index }
                    />;
                }) }
            </ul>
        </section>;
    }
}
