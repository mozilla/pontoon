/* @flow */

import * as React from 'react';
import { Localized } from 'fluent-react';

import './BatchEditor.css';


type Props = {
    count: number,
};


/**
 * Renders batch editor, used for performing mass actions on translations.
 */
export default class BatchEditor extends React.Component<Props> {
    render() {
        const { count } = this.props;

        return <div className="batch-editor">
            <div className="topbar clearfix">
                <div className="selecting fa fa-sync fa-spin"></div>
                <Localized
                    id="batcheditor-BatchEditor--header-selected-count"
                    attrs={{ title: true }}
                    glyph={
                        <i className="fa fa-times fa-lg"></i>
                    }
                    stress={ <span className="stress" /> }
                    $count={ count }
                >
                    <button
                        className="selected-count"
                        title="Quit Batch Editing (Esc)"
                    >
                        { '<glyph></glyph> <stress>{ $count }</stress> strings selected' }
                    </button>
                </Localized>
                <Localized
                    id="batcheditor-BatchEditor--header-select-all"
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
                    <p>
                        <Localized id="batcheditor-BatchEditor--warning-title">
                            <span className="warning">Warning:</span>
                        </Localized>
                        { ' ' }
                        <Localized id="batcheditor-BatchEditor--warning-content">
                            <span className="content">These actions will be applied to all selected strings and cannot be undone.</span>
                        </Localized>
                    </p>
                </div>

                <div className="review">
                    <Localized id="batcheditor-BatchEditor--review-heading">
                        <h2>Review translations</h2>
                    </Localized>

                    <button className="approve-all">
                        <Localized id="batcheditor-BatchEditor--approve-all-button">
                            <span className="title">Approve all</span>
                        </Localized>
                        <span className="fa fa-2x fa-sync fa-spin"></span>
                    </button>

                    <button className="reject-all">
                        <Localized id="batcheditor-BatchEditor--reject-all-button">
                            <span className="title">Reject all unreviewed suggestions</span>
                        </Localized>
                        <span className="fa fa-2x fa-sync fa-spin"></span>
                    </button>
                </div>

                <div className="find-replace">
                    <Localized id="batcheditor-BatchEditor--find-replace-heading">
                        <h2>Find & Replace in translations</h2>
                    </Localized>

                    <Localized id="batcheditor-BatchEditor--find" attrs={{ placeholder: true }}>
                        <input
                            className="find"
                            type="search"
                            autoComplete="off"
                            placeholder="Find"
                        />
                    </Localized>
                    <Localized id="batcheditor-BatchEditor--replace-with" attrs={{ placeholder: true }}>
                        <input
                            className="replace"
                            type="search"
                            autoComplete="off"
                            placeholder="Replace with"
                        />
                    </Localized>

                    <button className="replace-all">
                        <Localized id="batcheditor-BatchEditor--replace-all-button">
                            <span className="title">Replace all</span>
                        </Localized>
                        <span className="fa fa-2x fa-sync fa-spin"></span>
                    </button>
                </div>
            </div>
        </div>;
    }
}
