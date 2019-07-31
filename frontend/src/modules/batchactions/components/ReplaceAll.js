/* @flow */

import * as React from 'react';
import { Localized } from 'fluent-react';

import type { BatchActionsState } from 'modules/batchactions';


type Props = {|
    replaceAll: () => void,
    batchactions: BatchActionsState,
|};


/**
 * Renders Replace All batch action button.
 */
export default class ReplaceAll extends React.Component<Props> {
    replaceAll = () => {
        this.props.replaceAll();
    }

    renderDefault() {
        return <Localized
            id="batchactions-ReplaceAll--default"
        >
            { 'Replace all' }
        </Localized>;
    }

    renderError() {
        return <Localized
            id="batchactions-ReplaceAll--error"
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
            id="batchactions-ReplaceAll--invalid"
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
            id="batchactions-ReplaceAll--success"
            $changedCount={ response.changedCount }
        >
            { '{ $changedCount } strings replaced' }
        </Localized>;
    }

    renderTitle() {
        const { response } = this.props.batchactions;

        if (response && response.action === 'replace') {
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
            className="replace-all"
            onClick={ this.replaceAll }
        >
            { this.renderTitle() }
            { this.props.batchactions.requestInProgress !== 'replace' ? null :
                <span className="fa fa-2x fa-sync fa-spin"></span>
            }
        </button>;
    }
}
