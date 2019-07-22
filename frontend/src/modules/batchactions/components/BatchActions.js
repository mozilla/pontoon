/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';
import { Localized } from 'fluent-react';

import './BatchActions.css';

import * as batchactions from 'modules/batchactions';

import type { BatchActionsState } from 'modules/batchactions';


type Props = {
    batchactions: BatchActionsState,
};

type InternalProps = {|
    ...Props,
    dispatch: Function,
|};


/**
 * Renders batch editor, used for performing mass actions on translations.
 */
export class BatchActionsBase extends React.Component<InternalProps> {
    quitBatchActions = () => {
        this.props.dispatch(batchactions.actions.reset());
    }

    render() {
        return <div className="batch-actions">
            <div className="topbar clearfix">
                <div className="selecting fa fa-sync fa-spin"></div>
                <Localized
                    id="batchactions-BatchActions--header-selected-count"
                    attrs={{ title: true }}
                    glyph={
                        <i className="fa fa-times fa-lg"></i>
                    }
                    stress={ <span className="stress" /> }
                    $count={ this.props.batchactions.entities.length }
                >
                    <button
                        className="selected-count"
                        title="Quit Batch Editing (Esc)"
                        onClick={ this.quitBatchActions }
                    >
                        { '<glyph></glyph> <stress>{ $count }</stress> strings selected' }
                    </button>
                </Localized>
                <Localized
                    id="batchactions-BatchActions--header-select-all"
                    attrs={{ title: true }}
                    glyph={
                        <i className="fa fa-check fa-lg"></i>
                    }
                >
                    <button
                        className="select-all"
                        title="Select All Strings (Ctrl + Shift + A)"
                    >
                        { '<glyph></glyph> Select All' }
                    </button>
                </Localized>
            </div>

            <div className="main-content">
                <div className="intro">
                    <Localized
                        id="batchactions-BatchActions--warning"
                        stress={ <span className="stress" /> }
                    >
                        <p><stress>Warning:</stress> These actions will be applied to all selected strings and cannot be undone.</p>
                    </Localized>
                </div>

                <div className="review">
                    <Localized id="batchactions-BatchActions--review-heading">
                        <h2>Review translations</h2>
                    </Localized>

                    <button className="approve-all">
                        <Localized id="batchactions-BatchActions--approve-all-button">
                            <span className="title">Approve all</span>
                        </Localized>
                        <span className="fa fa-2x fa-sync fa-spin"></span>
                    </button>

                    <button className="reject-all">
                        <Localized id="batchactions-BatchActions--reject-all-button">
                            <span className="title">Reject all unreviewed suggestions</span>
                        </Localized>
                        <span className="fa fa-2x fa-sync fa-spin"></span>
                    </button>
                </div>

                <div className="find-replace">
                    <Localized id="batchactions-BatchActions--find-replace-heading">
                        <h2>Find & Replace in translations</h2>
                    </Localized>

                    <Localized id="batchactions-BatchActions--find" attrs={{ placeholder: true }}>
                        <input
                            className="find"
                            type="search"
                            autoComplete="off"
                            placeholder="Find"
                        />
                    </Localized>
                    <Localized id="batchactions-BatchActions--replace-with" attrs={{ placeholder: true }}>
                        <input
                            className="replace"
                            type="search"
                            autoComplete="off"
                            placeholder="Replace with"
                        />
                    </Localized>

                    <button className="replace-all">
                        <Localized id="batchactions-BatchActions--replace-all-button">
                            <span className="title">Replace all</span>
                        </Localized>
                        <span className="fa fa-2x fa-sync fa-spin"></span>
                    </button>
                </div>
            </div>
        </div>;
    }
}


const mapStateToProps = (state: Object): Props => {
    return {
        batchactions: state[batchactions.NAME],
    };
};

export default connect(mapStateToProps)(BatchActionsBase);
