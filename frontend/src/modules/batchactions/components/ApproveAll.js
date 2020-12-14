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
        return (
            <Localized id='batchactions-ApproveAll--default'>
                {'APPROVE ALL'}
            </Localized>
        );
    }

    renderError() {
        return (
            <Localized id='batchactions-ApproveAll--error'>
                {'OOPS, SOMETHING WENT WRONG'}
            </Localized>
        );
    }

    renderInvalid() {
        const { response } = this.props.batchactions;

        if (!response) {
            return null;
        }

        return (
            <Localized
                id='batchactions-ApproveAll--invalid'
                vars={{ invalidCount: response.invalidCount }}
            >
                {'{ $invalidCount } FAILED'}
            </Localized>
        );
    }

    renderSuccess() {
        const { response } = this.props.batchactions;

        if (!response) {
            return null;
        }

        return (
            <Localized
                id='batchactions-ApproveAll--success'
                vars={{ changedCount: response.changedCount }}
            >
                {'{ $changedCount } STRINGS APPROVED'}
            </Localized>
        );
    }

    renderTitle() {
        const { response } = this.props.batchactions;

        if (response && response.action === 'approve') {
            if (response.error) {
                return this.renderError();
            } else if (response.invalidCount) {
                return (
                    <>
                        {this.renderSuccess()}
                        {' · '}
                        {this.renderInvalid()}
                    </>
                );
            } else {
                return this.renderSuccess();
            }
        } else {
            return this.renderDefault();
        }
    }

    render() {
        return (
            <button className='approve-all' onClick={this.props.approveAll}>
                {this.renderTitle()}
                {this.props.batchactions.requestInProgress !==
                'approve' ? null : (
                    <i className='fa fa-2x fa-circle-notch fa-spin'></i>
                )}
            </button>
        );
    }
}
