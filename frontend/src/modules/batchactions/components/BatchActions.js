/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';
import { Localized } from 'fluent-react';

import './BatchActions.css';

import * as navigation from 'core/navigation';
import * as batchactions from 'modules/batchactions';

import ApproveAll from './ApproveAll';
import RejectAll from './RejectAll';
import ReplaceAll from './ReplaceAll';

import type { BatchActionsState } from 'modules/batchactions';
import type { NavigationParams } from 'core/navigation';


type Props = {|
    batchactions: BatchActionsState,
    parameters: NavigationParams,
|};

type InternalProps = {|
    ...Props,
    dispatch: Function,
|};


/**
 * Renders batch editor, used for performing mass actions on translations.
 */
export class BatchActionsBase extends React.Component<InternalProps> {
    find: { current: ?HTMLInputElement };
    replace: { current: ?HTMLInputElement };

    constructor(props: InternalProps) {
        super(props);

        this.find = React.createRef();
        this.replace = React.createRef();
    }

    componentDidMount() {
        // $FLOW_IGNORE (errors that I don't understand, no help from the Web)
        document.addEventListener('keydown', this.handleShortcuts);
    }

    componentWillUnmount() {
        // $FLOW_IGNORE (errors that I don't understand, no help from the Web)
        document.removeEventListener('keydown', this.handleShortcuts);
    }

    handleShortcuts = (event: SyntheticKeyboardEvent<>) => {
        const key = event.keyCode;

        // On Esc, quit batch actions
        if (key === 27) {
            this.quitBatchActions();
        }
    }

    quitBatchActions = () => {
        this.props.dispatch(batchactions.actions.resetSelection());
    }

    selectAllEntities = () => {
        const { locale, project, resource, search, status } = this.props.parameters;

        this.props.dispatch(
            batchactions.actions.selectAll(
                locale,
                project,
                resource,
                search,
                status,
            )
        );
    }

    approveAll = () => {
        this.props.dispatch(
            batchactions.actions.performAction(
                'approve',
                this.props.parameters.locale,
                this.props.batchactions.entities,
            )
        );
    }

    rejectAll = () => {
        this.props.dispatch(
            batchactions.actions.performAction(
                'reject',
                this.props.parameters.locale,
                this.props.batchactions.entities,
            )
        );
    }

    replaceAll = () => {
        const find = this.find.current;
        const replace = this.replace.current;

        if (!find || !replace) {
            return;
        }

        if (find.value === '') {
            find.focus();
            return;
        }

        if (find.value === replace.value) {
            replace.focus();
            return;
        }

        this.props.dispatch(
            batchactions.actions.performAction(
                'replace',
                this.props.parameters.locale,
                this.props.batchactions.entities,
                find.value,
                replace.value,
            )
        );
    }

    submitReplaceForm = (event: SyntheticKeyboardEvent<>) => {
        event.preventDefault();
        this.replaceAll();
    }

    render() {
        return <div className="batch-actions">
            <div className="topbar clearfix">
                { this.props.batchactions.fetching === 'select-all' ?
                    <div className="selecting fa fa-sync fa-spin"></div>
                    :
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
                }
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
                        onClick={ this.selectAllEntities }
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

                    <ApproveAll
                        approveAll = { this.approveAll }
                        batchactions = { this.props.batchactions }
                    />

                    <RejectAll
                        rejectAll = { this.rejectAll }
                        batchactions = { this.props.batchactions }
                    />
                </div>

                <div className="find-replace">
                    <Localized id="batchactions-BatchActions--find-replace-heading">
                        <h2>Find & Replace in translations</h2>
                    </Localized>

                    <form onSubmit={ this.submitReplaceForm }>
                        <Localized id="batchactions-BatchActions--find" attrs={{ placeholder: true }}>
                            <input
                                className="find"
                                type="search"
                                autoComplete="off"
                                placeholder="Find"
                                ref={ this.find }
                            />
                        </Localized>

                        <Localized id="batchactions-BatchActions--replace-with" attrs={{ placeholder: true }}>
                            <input
                                className="replace"
                                type="search"
                                autoComplete="off"
                                placeholder="Replace with"
                                ref={ this.replace }
                            />
                        </Localized>

                        <ReplaceAll
                            replaceAll = { this.replaceAll }
                            batchactions = { this.props.batchactions }
                        />
                    </form>
                </div>
            </div>
        </div>;
    }
}


const mapStateToProps = (state: Object): Props => {
    return {
        batchactions: state[batchactions.NAME],
        parameters: navigation.selectors.getNavigationParams(state),
    };
};

export default connect(mapStateToProps)(BatchActionsBase);
