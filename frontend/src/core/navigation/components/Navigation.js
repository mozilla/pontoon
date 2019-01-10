/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';
import isEmpty from 'lodash.isempty';

import './Navigation.css';

import { NAME as LOCALES_NAME } from 'core/locales';
import type { LocalesState } from 'core/locales';

import { selectors } from '..';
import type { NavigationParams } from '..';


type Props = {|
    parameters: NavigationParams,
    locales: LocalesState,
|};

type InternalProps = {|
    ...Props,
    dispatch: Function,
|};


/**
 * Render a breadcrumb-like navigation bar.
 *
 * Allows to exit the Translate app to go back to team or project dashboards.
 */
export class NavigationBase extends React.Component<InternalProps> {
    render() {
        const { parameters, locales } = this.props;

        if (isEmpty(locales.locales)) {
            return null;
        }

        const locale = locales.locales[parameters.locale];

        return <nav className="navigation">
            <ul>
                <li>
                    <a href="/">
                        <img
                            src="/static/img/logo.svg"
                            width="32"
                            height="32"
                            alt="Pontoon logo"
                        />
                    </a>
                </li>
                <li>
                    <a href={ `/${locale.code}/` }>
                        { locale.name }
                        <span className="locale-code">{ locale.code }</span>
                    </a>
                </li>
                <li>
                    <a href={ `/${locale.code}/${parameters.project}/` }>{ parameters.project }</a>
                </li>
            </ul>
        </nav>;
    }
}


const mapStateToProps = (state: Object): Props => {
    return {
        parameters: selectors.getNavigationParams(state),
        locales: state[LOCALES_NAME],
    };
};

export default connect(mapStateToProps)(NavigationBase);
