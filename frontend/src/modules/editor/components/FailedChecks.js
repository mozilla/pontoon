/* @flow */

import * as React from 'react';
import { Localized } from 'fluent-react';

import './FailedChecks.css';


type Props = {|
    errors: Array<string>,
    warnings: Array<string>,
    resetFailedChecks: () => void,
|};


/*
 * Renders the failed checks popup.
 */
export default class FailedChecks extends React.Component<Props> {
    closeFailedChecks = () => {
        this.props.resetFailedChecks();
    }

    render() {
        const { errors, warnings } = this.props;

        if (!errors.length && !warnings.length) {
            return null;
        }

        return <div className="failed-checks">
            <Localized
                id="editor-FailedChecks--close"
                attrs={{ ariaLabel: true }}
            >
                <button
                    aria-label="Close failed checks popup"
                    className="close"
                    onClick={ this.closeFailedChecks }
                >×</button>
            </Localized>
            <Localized
                id="editor-FailedChecks--title"
            >
                <p className="title">The following checks have failed</p>
            </Localized>
            <ul>
                {
                    errors.map((error, key) => {
                        return <li className="error" key={ key }>
                            { error }
                        </li>;
                    })
                }
                {
                    warnings.map((warning, key) => {
                        return <li className="warning" key={ key }>
                            { warning }
                        </li>;
                    })
                }
            </ul>
        </div>;
    }
}
