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
    customMachinerySearch: (string) => void,
|};


/**
 * Show translations from machines.
 *
 * Shows a sorted list of translations for the same original string, or similar
 * strings, coming from various sources like Translation Memory or
 * third-party Machine Translation.
 */
export default class Machinery extends React.Component<Props> {
    submitForm = (event: SyntheticKeyboardEvent<>) => {
        event.preventDefault();
        this.props.customMachinerySearch(event.currentTarget[0].value);
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
                <form onSubmit={ this.submitForm }>
                    <Localized id="machinery-machinery-search-placeholder" attrs={{ placeholder: true }}>
                        <input
                            type="search"
                            autoComplete="off"
                            placeholder="Type to search machinery"
                        />
                    </Localized>
                </form>
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
