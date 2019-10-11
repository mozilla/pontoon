/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import type { BatchActionsState } from 'modules/batchactions';


type Props = {|
    approveAll: () => void,
    batchactions: BatchActionsState,
|};


/**
 * Renders Approve All batch action button.
 */
export default class ApproveAll extends React.Component<Props> {
    renderDefault() {
        return <Localized
            id="batchactions-ApproveAll--default"
        >
            { 'Approve all' }
        </Localized>;
    }

    renderError() {
        return <Localized
            id="batchactions-ApproveAll--error"
        >
            { 'Oops, something went wrong' }
        </Localized>;
    }

    renderInvalid() {
        const { response } = this.props.batchactions;

        if (!response) {
            return null;
        }

        return <Localized
            id="batchactions-ApproveAll--invalid"
            $invalidCount={ response.invalidCount }
        >
            { '{ $invalidCount } failed' }
        </Localized>;
    }

    renderSuccess() {
        const { response } = this.props.batchactions;

        if (!response) {
            return null;
        }

        return <Localized
            id="batchactions-ApproveAll--success"
            $changedCount={ response.changedCount }
        >
            { '{ $changedCount } strings approved' }
        </Localized>;
    }

    renderTitle() {
        const { response } = this.props.batchactions;

        if (response && response.action === 'approve') {
            if (response.error) {
                return this.renderError();
            }
            else if (response.invalidCount) {
                return <>
                    { this.renderSuccess() }
                    { ' · ' }
                    { this.renderInvalid() }
                </>;
            }
            else {
                return this.renderSuccess();
            }
        }
        else {
            return this.renderDefault();
        }
    }

    render() {
        return <button
            className="approve-all"
            onClick={ this.props.approveAll }
        >
            { this.renderTitle() }
            { this.props.batchactions.requestInProgress !== 'approve' ? null :
                <span className="fa fa-2x fa-sync fa-spin"></span>
            }
        </button>;
    }
}
