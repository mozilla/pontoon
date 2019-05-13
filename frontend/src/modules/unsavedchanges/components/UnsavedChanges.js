/* @flow */

import * as React from 'react';
import { Localized } from 'fluent-react';

import './UnsavedChanges.css';


type Props = {|
    ignored: boolean,
    exist: boolean,
    callback: ?Function,
    hide: () => void,
    ignore: () => void,
|};


/*
 * Renders the unsaved changes popup.
 */
export default class UnsavedChanges extends React.Component<Props> {
    componentDidUpdate(prevProps: Props) {
        const { callback, hide } = this.props;

        if (!prevProps.ignored && this.props.ignored) {
            if (callback) {
                callback();
                hide();
            }
        }
    }

    hideUnsavedChanges = () => {
        this.props.hide();
    }

    leaveAnyway = () => {
        this.props.ignore();
    }

    render() {
        if (!this.props.exist) {
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
