/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';

import './PluralSelector.css';

import * as locale from 'core/locale';
import * as unsavedchanges from 'modules/unsavedchanges';

import { actions, CLDR_PLURALS, selectors } from '..';

import type { Locale } from 'core/locale';
import type { UnsavedChangesState } from 'modules/unsavedchanges';


type Props = {|
    locale: Locale,
    pluralForm: number,
    unsavedchanges: UnsavedChangesState,
|};

type InternalProps = {|
    ...Props,
    dispatch: Function,
|};


/**
 * Plural form picker component.
 *
 * Shows a list of available plural forms for the current locale, and allows
 * to change selected plural form.
 */
export class PluralSelectorBase extends React.Component<InternalProps> {
    selectPluralForm(pluralForm: number) {
        if (this.props.pluralForm === pluralForm) {
            return;
        }

        const { dispatch } = this.props;

        dispatch(
            unsavedchanges.actions.check(
                this.props.unsavedchanges,
                () => {
                    dispatch(
                        actions.select(pluralForm)
                    );
                }
            )
        );
    }

    render() {
        const { pluralForm, locale } = this.props;

        if (pluralForm === -1 || !locale || locale.cldrPlurals.length <= 1) {
            return null;
        }

        const nbPlurals = locale.cldrPlurals.length;
        const examples = {};

        if (nbPlurals === 2) {
            examples[locale.cldrPlurals[0]] = 1;
            examples[locale.cldrPlurals[1]] = 2;
        }
        else {
            // This variable is used in the pluralRule we eval in the while block.
            let n = 0;
            while (Object.keys(examples).length < nbPlurals) {
                // This `eval` is not so much evil. The pluralRule we parse
                // comes from our database and is not a user input.
                // eslint-disable-next-line
                const rule = eval(locale.pluralRule);
                if (!examples[locale.cldrPlurals[rule]]) {
                    examples[locale.cldrPlurals[rule]] = n;
                }
                n++;
            }
        }

        return <nav className="plural-selector">
            <ul>
                { locale.cldrPlurals.map((item, i) => {
                    return <li key={ item } className={ i === pluralForm ? 'active' : '' }>
                        <button onClick={ () => this.selectPluralForm(i) }>
                            <span>{ CLDR_PLURALS[item] }</span>
                            <sup>{ examples[item] }</sup>
                        </button>
                    </li>;
                }) }
            </ul>
        </nav>;
    }
}


const mapStateToProps = (state: Object): Props => {
    return {
        locale: state[locale.NAME],
        pluralForm: selectors.getPluralForm(state),
        unsavedchanges: state[unsavedchanges.NAME],
    };
};

export default connect(mapStateToProps)(PluralSelectorBase);
