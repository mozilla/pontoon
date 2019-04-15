/* @flow */

import * as React from 'react';
import { Localized } from 'fluent-react';

import './FailedChecks.css';

import type { DbEntity } from 'modules/entitieslist';


type Props = {|
    errors: Array<string>,
    warnings: Array<string>,
|};


type State = {|
    visible: boolean,
|};


/*
 * Renders an appropriate Editor for an entity, based on its file format.
 */
export default class FailedChecks extends React.Component<Props, State> {
    constructor() {
        super();
        this.state = {
            visible: true,
        };
    }

    componentDidUpdate(prevProps: Props, prevState: State) {
        if (!prevState.visible) {
            this.setState(() => {
                return { visible: true };
            });
        }
    }

    closeFailedChecks = () => {
        this.setState(() => {
            return { visible: false };
        });
    }

    render() {
        if (!this.state.visible) {
            return null;
        }

        const { errors, warnings } = this.props;

        if (!errors.length && !warnings.length) {
            return null;
        }

        return <div className="failed-checks">
            <button className="cancel" onClick={ this.closeFailedChecks }>&times;</button>
            <Localized
                id="editor-FailedChecks--title"
            >
                <p className="title">The following checks have failed</p>
            </Localized>
            <ul>
                {
                    errors.map((error, key) => {
                        return <li className="error" key={ key }>
                            <i className="fa fa-times-circle"></i>
                            { error }
                        </li>;
                    })
                }
                {
                    warnings.map((warning, key) => {
                        return <li className="warning" key={ key }>
                            <i className="fa fa-times-circle"></i>
                            { warning }
                        </li>;
                    })
                }
            </ul>
        </div>;
    }
}
