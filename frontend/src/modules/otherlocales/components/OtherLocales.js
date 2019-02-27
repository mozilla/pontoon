/* @flow */

import React from 'react';
import { connect } from 'react-redux';
import { Localized } from 'fluent-react';

import './OtherLocales.css';

import api from 'core/api';
import { selectors } from '..';
import Translation from './Translation';

import type { Navigation } from 'core/navigation';
import type { LocalesState } from '..';
import type { UserState } from 'core/user';


type Props = {|
    orderedOtherLocales: Array<api.types.OtherLocaleTranslation>,
    preferredCount: number,
    otherlocales: LocalesState,
    user: UserState,
|};

type InternalProps = {|
    ...Props,
    parameters: Navigation,
    updateEditorTranslation: (string) => void,
|};


/**
 * Shows all translations of an entity in locales other than the current one.
 */
export class OtherLocalesBase extends React.Component<InternalProps> {
    renderNoResults() {
        return <section className="other-locales">
            <Localized id="history-history-no-translations">
                <p>No translations available.</p>
            </Localized>
        </section>
    }

    render() {
        const {
            orderedOtherLocales,
            preferredCount,
            otherlocales,
            parameters,
            updateEditorTranslation,
        } = this.props;

        if (otherlocales.fetching) {
            return null;
        }

        if (!otherlocales.translations.length) {
            return this.renderNoResults();
        }

        return <section className="other-locales">
            <ul>
                { orderedOtherLocales.map((translation, index) => {
                    let lastPreferred = (index === preferredCount - 1);

                    return <Translation
                        translation={ translation }
                        parameters={ parameters }
                        updateEditorTranslation={ updateEditorTranslation }
                        lastPreferred={ lastPreferred }
                        key={ index }
                    />;
                }) }
            </ul>
        </section>;
    }
}


const mapStateToProps = (state: Object): Props => {
    return {
        orderedOtherLocales: selectors.getOrderedOtherLocales(state),
        preferredCount: selectors.getPreferredLocalesCount(state),
        otherlocales: state.otherlocales,
        user: state.user,
    };
};

export default connect(mapStateToProps)(OtherLocalesBase);
