/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';
import { Localized } from '@fluent/react';

import './UnsavedChanges.css';

import { actions, NAME } from '..';

import type { UnsavedChangesState } from 'modules/unsavedchanges';

type Props = {|
    unsavedchanges: UnsavedChangesState,
|};

type InternalProps = {|
    ...Props,
    dispatch: Function,
|};

/*
 * Renders the unsaved changes popup.
 */
export class UnsavedChangesBase extends React.Component<InternalProps> {
    componentDidUpdate(prevProps: InternalProps) {
        if (
            !prevProps.unsavedchanges.ignored &&
            this.props.unsavedchanges.ignored
        ) {
            if (this.props.unsavedchanges.callback) {
                this.props.unsavedchanges.callback();
                this.props.dispatch(actions.hide());
            }
        }
    }

    hideUnsavedChanges = () => {
        this.props.dispatch(actions.hide());
    };

    ignoreUnsavedChanges = () => {
        this.props.dispatch(actions.ignore());
    };

    render() {
        if (!this.props.unsavedchanges.shown) {
            return null;
        }

        return (
            <div className='unsaved-changes'>
                <Localized
                    id='editor-UnsavedChanges--close'
                    attrs={{ ariaLabel: true }}
                >
                    <button
                        aria-label='Close unsaved changes popup'
                        className='close'
                        onClick={this.hideUnsavedChanges}
                    >
                        ×
                    </button>
                </Localized>

                <Localized id='editor-UnsavedChanges--title'>
                    <p className='title'>You have unsaved changes</p>
                </Localized>

                <Localized id='editor-UnsavedChanges--body'>
                    <p className='body'>Are you sure you want to proceed?</p>
                </Localized>

                <Localized id='editor-UnsavedChanges--proceed'>
                    <button
                        className='proceed anyway'
                        onClick={this.ignoreUnsavedChanges}
                    >
                        Proceed
                    </button>
                </Localized>
            </div>
        );
    }
}

const mapStateToProps = (state: Object): Props => {
    return {
        unsavedchanges: state[NAME],
    };
};

export default connect(mapStateToProps)(UnsavedChangesBase);
