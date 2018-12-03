/* @flow */

import React from 'react';
import { connect } from 'react-redux';
import { Localized } from 'fluent-react';

import './Locales.css';

import { selectors as navSelectors } from 'core/navigation';
import * as plural from 'core/plural';
import type { Navigation } from 'core/navigation';

import { actions, NAME } from '..';
import type { LocalesState } from '..';



type Props = {|
    otherlocales: LocalesState,
    parameters: Navigation,
    pluralForm: number,
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
export class LocalesBase extends React.Component<InternalProps> {
    componentDidMount() {
        this.verifyDataValidity();
    }

    componentDidUpdate() {
        this.verifyDataValidity();
    }

    verifyDataValidity() {
        const { otherlocales } = this.props;

        // Invalidation is handled by the `modules.entitydetails.EntityDetails`
        // component whenever there is a change of state. We cannot do it here
        // because this component is not always mounted (because of react-tabs).
        if (otherlocales.didInvalidate) {
            this.fetchOtherLocales();
        }
    }

    fetchOtherLocales() {
        const { parameters, pluralForm, dispatch } = this.props;

        dispatch(actions.get(
            parameters.entity,
            parameters.locale,
            pluralForm,
        ));
    }

    renderNoResults() {
        return <section className="otherlocales">
            <Localized id="history-history-no-translations">
                <p>No translations available.</p>
            </Localized>
        </section>
    }

    render() {
        const { otherlocales, parameters } = this.props;

        if (otherlocales.fetching) {
            return null;
        }

        if (!otherlocales.translations.length) {
            return this.renderNoResults();
        }

        return <section className="otherlocales">
            <ul>
                { otherlocales.translations.map((translation, key) => {
                    return <li key={ key }>
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
                            { translation.translation }
                        </p>
                    </li>;
                }) }
            </ul>
        </section>;
    }
}


const mapStateToProps = (state: Object): Props => {
    return {
        otherlocales: state[NAME],
        parameters: navSelectors.getNavigation(state),
        pluralForm: plural.selectors.getPluralForm(state),
    };
};

export default connect(mapStateToProps)(LocalesBase);
