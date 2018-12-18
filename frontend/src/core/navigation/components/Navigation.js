/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';

import './Navigation.css';

import { selectors } from '..';
import type { NavigationParams } from '..';


type Props = {|
    parameters: NavigationParams,
|};

type InternalProps = {|
    ...Props,
    dispatch: Function,
|};


export class NavigationBase extends React.Component<InternalProps> {
    render() {
        const { parameters } = this.props;

        return <nav className="navigation">
            <ul>
                <li>
                    <a href="/"><span className="fa fa-home" /></a>
                </li>
                <li>
                    <a href={ `/${parameters.locale}/` }>{ parameters.locale }</a>
                </li>
                <li>
                    <a href={ `/${parameters.locale}/${parameters.project}/` }>{ parameters.project }</a>
                </li>
            </ul>
        </nav>;
    }
}


const mapStateToProps = (state: Object): Props => {
    return {
        parameters: selectors.getNavigationParams(state),
    };
};

export default connect(mapStateToProps)(NavigationBase);
