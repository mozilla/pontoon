/* @flow */

import * as React from 'react';
import { Localized } from 'fluent-react';

import './FailedChecks.css';

import type { UserState } from 'core/user';
import { withActionsDisabled } from 'core/utils';
import type { ChangeOperation } from 'modules/history';


type Props = {|
    source: '' | 'stored' | 'submitted' | number,
    user: UserState,
    errors: Array<string>,
    warnings: Array<string>,
    resetFailedChecks: () => void,
    sendTranslation: (ignoreWarnings: ?boolean) => void,
    updateTranslationStatus: (
        translationId: number,
        change: ChangeOperation,
        ignoreWarnings: ?boolean,
    ) => void,
|};

type InternalProps = {|
    ...Props,
    isActionDisabled: boolean,
    disableAction: () => void,
|};


/*
 * Renders the failed checks popup.
 */
export class FailedChecksBase extends React.Component<InternalProps> {
    closeFailedChecks = () => {
        this.props.resetFailedChecks();
    }

    approveAnyway = () => {
        if (this.props.isActionDisabled) {
            return;
        }
        this.props.disableAction();

        const translationId = this.props.source;
        if (typeof(translationId) === 'number') {
            this.props.updateTranslationStatus(translationId, 'approve', true);
        }
    }

    submitAnyway = () => {
        if (this.props.isActionDisabled) {
            return;
        }
        this.props.disableAction();

        this.props.sendTranslation(true);
    }

    render() {
        const { source, user, errors, warnings } = this.props;

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
            { (source === 'stored' || errors.length) ? null :
                source !== 'submitted' ?
                <Localized id="editor-FailedChecks--approve-anyway">
                    <button
                        className="approve anyway"
                        disabled={ this.props.isActionDisabled }
                        onClick={ this.approveAnyway }
                    >
                        Approve anyway
                    </button>
                </Localized>
                : user.settings.forceSuggestions ?
                <Localized id="editor-FailedChecks--suggest-anyway">
                    <button
                        className="suggest anyway"
                        disabled={ this.props.isActionDisabled }
                        onClick={ this.submitAnyway }
                    >
                        Suggest anyway
                    </button>
                </Localized>
                :
                <Localized id="editor-FailedChecks--save-anyway">
                    <button
                        className="save anyway"
                        disabled={ this.props.isActionDisabled }
                        onClick={ this.submitAnyway }
                    >
                        Save anyway
                    </button>
                </Localized>
            }
        </div>;
    }
}


export default withActionsDisabled(FailedChecksBase);
