/* @flow */

import * as React from 'react';
import { Localized } from 'fluent-react';

import './UnsavedChanges.css';


type Props = {|
    callback: ?Function,
    hide: () => void,
    ignore: () => void,
    hasChanges: boolean,
|};


/*
 * Renders the unsaved changes popup.
 */
export default class UnsavedChanges extends React.Component<Props> {
    hideUnsavedChanges = () => {
        this.props.hide();
    }

    leaveAnyway = () => {
        const { callback, hide, ignore } = this.props;
        if (callback) {
            ignore();

            setTimeout(() => {
                callback();
                hide();
            }, 10);
        }
    }

    render() {
        const { hasChanges } = this.props;

        if (!hasChanges) {
            return null;
        }

        return <div className="unsaved-changes">
            <Localized
                id="editor-UnsavedChanges--close"
                attrs={{ ariaLabel: true }}
            >
                <button
                    aria-label="Close unsaved changes popup"
                    className="close"
                    onClick={ this.hideUnsavedChanges }
                >
                    ×
                </button>
            </Localized>

            <Localized id="editor-UnsavedChanges--title">
                <p className="title">You have unsaved changes</p>
            </Localized>

            <Localized id="editor-UnsavedChanges--title">
                <p className="body">Sure you want to leave?</p>
            </Localized>

            <Localized id="editor-UnsavedChanges--leave-anyway">
                <button
                    className="leave anyway"
                    onClick={ this.leaveAnyway }
                >
                    Leave anyway
                </button>
            </Localized>
        </div>;
    }
}
