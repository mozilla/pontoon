/* @flow */

import React from 'react';
import { connect } from 'react-redux';
import { Localized } from 'fluent-react';

import './History.css';

import * as locales from 'core/locales';
import * as navigation from 'core/navigation';
import * as plural from 'core/plural';
import * as entitieslist from 'modules/entitieslist';
import { NAME as USER_NAME } from 'core/user';

import Translation from './Translation';
import { actions, NAME } from '..';

import type { Locale } from 'core/locales';
import type { NavigationParams } from 'core/navigation';
import type { UserState } from 'core/user';
import type { DbEntity } from 'modules/entitieslist';
import type { DBTranslation, HistoryState } from '../reducer';


type Props = {|
    history: HistoryState,
    locale: Locale,
    nextEntity: ?DbEntity,
    parameters: NavigationParams,
    pluralForm: number,
    router: Object,
    user: UserState,
|};

type InternalProps = {|
    ...Props,
    dispatch: Function,
|};


/**
 * Shows all existing translations of an entity.
 *
 * For each translation, show its author, date and status (approved, rejected).
 */
export class HistoryBase extends React.Component<InternalProps> {
    updateTranslationStatus = (translation: DBTranslation, change: string) => {
        const { nextEntity, parameters, pluralForm, router, dispatch } = this.props;
        dispatch(actions.updateStatus(
            change,
            parameters.entity,
            parameters.locale,
            parameters.resource,
            pluralForm,
            translation.pk,
            nextEntity,
            router,
        ));
    }

    renderNoResults() {
        return <section className="history">
            <Localized id="history-history-no-translations">
                <p>No translations available.</p>
            </Localized>
        </section>
    }

    render() {
        const { history, locale, parameters, user } = this.props;

        if (!history.translations.length) {
            if (history.fetching) {
                return null;
            }

            return this.renderNoResults();
        }

        const canReview = (
            user.translatorForLocales &&
            user.translatorForLocales.includes(parameters.locale)
        );

        return <section className="history">
            <ul>
                { history.translations.map((translation, key) => {
                    return <Translation
                        translation={ translation }
                        canReview={ canReview }
                        locale={ locale }
                        user={ user }
                        updateTranslationStatus={ this.updateTranslationStatus }
                        key={ key }
                    />;
                }) }
            </ul>
        </section>;
    }
}


const mapStateToProps = (state: Object): Props => {
    return {
        history: state[NAME],
        locale: locales.selectors.getCurrentLocaleData(state),
        nextEntity: entitieslist.selectors.getNextEntity(state),
        parameters: navigation.selectors.getNavigationParams(state),
        pluralForm: plural.selectors.getPluralForm(state),
        router: state.router,
        user: state[USER_NAME],
    };
};

export default connect(mapStateToProps)(HistoryBase);
