/* @flow */

import * as React from 'react';
import TimeAgo from 'react-timeago';
import { Localized } from 'fluent-react';

import './Translation.css';

import { withDiff } from 'core/diff';
import { WithPlaceables, WithPlaceablesNoLeadingSpace } from 'core/placeable';

import type { Locale } from 'core/locales';
import type { UserState } from 'core/user';
import type { DBTranslation } from '../reducer';


type Props = {|
    isReadOnlyEditor: boolean,
    canReview: boolean,
    translation: DBTranslation,
    activeTranslation: DBTranslation,
    locale: Locale,
    user: UserState,
    index: number,
    deleteTranslation: (number) => void,
    updateEditorTranslation: (string) => void,
    updateTranslationStatus: (number, string) => void,
|};


type State = {|
    isDiffVisible: boolean,
|};


/**
 * Render a translation in the History tab.
 *
 * Shows the translation's status, date, author and reviewer, as well as
 * the content of the translation.
 *
 * The status can be interact with if the user has sufficient permissions to
 * change said status.
 */
export default class Translation extends React.Component<Props, State> {
    constructor() {
        super();
        this.state = {
            isDiffVisible: false,
        };
    }

    handleStatusChange = (event: SyntheticMouseEvent<HTMLButtonElement>) => {
        event.stopPropagation();
        // $FLOW_IGNORE: Flow and the DOM… >_<
        const action = event.target.name;
        this.props.updateTranslationStatus(this.props.translation.pk, action);
    }

    delete = (event: SyntheticMouseEvent<HTMLButtonElement>) => {
        event.stopPropagation();
        this.props.deleteTranslation(this.props.translation.pk);
    }

    copyTranslationIntoEditor = () => {
        if (this.props.isReadOnlyEditor) {
            return;
        }
        this.props.updateEditorTranslation(this.props.translation.string);
    }

    getStatus() {
        const { translation } = this.props;

        if (translation.approved) {
            return 'approved';
        }
        if (translation.fuzzy) {
            return 'fuzzy';
        }
        if (translation.rejected) {
            return 'rejected';
        }
        return 'unreviewed';
    }

    getApprovalTitle() {
        const { translation } = this.props;

        if (translation.approved && translation.approved_user) {
            return `Approved by ${translation.approved_user}`;
        }
        if (translation.unapproved_user) {
            return `Unapproved by ${translation.unapproved_user}`;
        }
        return 'Not reviewed yet';
    }

    renderUser() {
        const { translation } = this.props;

        if (!translation.uid) {
            return <span>{ translation.user }</span>;
        }

        return <a
            href={ `/contributors/${translation.username}` }
            title={ this.getApprovalTitle() }
            target='_blank'
            rel='noopener noreferrer'
            onClick={ (e: SyntheticMouseEvent<>) => e.stopPropagation() }
        >
            { translation.user }
        </a>
    }

    toggleDiff = (event: SyntheticMouseEvent<>) => {
        event.stopPropagation();
        this.setState((state) => {
            return { isDiffVisible: !state.isDiffVisible };
        });
    }

    renderDiffToggle() {
        const { index } = this.props;

        if (index === 0) {
            return null;
        }

        // Hide Diff
        if (this.state.isDiffVisible) {
            return <Localized
                id='history-translation-hide-diff'
                attrs={{ title: true }}
            >
                <button
                    className='toggle-diff hide'
                    title='Hide diff against the currently active translation'
                    onClick={ this.toggleDiff }
                >
                    { 'Hide diff' }
                </button>
            </Localized>;
        }

        // Show Diff
        else {
            return <Localized
                id='history-translation-show-diff'
                attrs={{ title: true }}
            >
                <button
                    className='toggle-diff show'
                    title='Show diff against the currently active translation'
                    onClick={ this.toggleDiff }
                >
                    { 'Show diff' }
                </button>
            </Localized>;
        }
    }

    render() {
        const {
            canReview,
            isReadOnlyEditor,
            translation,
            locale,
            user,
            activeTranslation,
        } = this.props;

        // Does the currently logged in user own this translation?
        const ownTranslation = (
            user && user.username &&
            user.username === translation.username
        );

        let className = 'translation ' + this.getStatus();
        if (canReview && !isReadOnlyEditor) {
            // This user is a translator for the current locale, they can
            // perform all review actions.
            className += ' can-approve can-reject';
        }
        else if (ownTranslation && !translation.approved && !isReadOnlyEditor) {
            // This user owns the translation and it's not approved, they
            // can only reject or unreject it.
            className += ' can-reject';
        }

        let canDelete = (canReview || ownTranslation) && !isReadOnlyEditor;

        const TranslationPlaceablesDiff = withDiff(WithPlaceablesNoLeadingSpace);

        return <Localized id='history-translation-copy' attrs={{ title: true }}>
            <li
                className={ className }
                title='Copy Into Translation (Tab)'
                onClick={ this.copyTranslationIntoEditor }
            >
                <header className='clearfix'>
                    <div className='info'>
                        { this.renderUser() }
                        <TimeAgo
                            dir='ltr'
                            date={ translation.date_iso }
                            title={ `${translation.date} UTC` }
                        />
                    </div>
                    <menu className='toolbar'>

                    { this.renderDiffToggle() }

                    { (!translation.rejected || !canDelete ) ? null :
                        // Delete Button
                        <Localized
                            id='history-translation-button-delete'
                            attrs={{ title: true }}
                        >
                            <button
                                className='delete far'
                                title='Delete'
                                onClick={ this.delete }
                            />
                        </Localized>
                    }
                    { translation.approved ?
                        // Unapprove Button
                        <Localized
                            id='history-translation-button-unapprove'
                            attrs={{ title: true }}
                        >
                            <button
                                className='unapprove fa'
                                title='Unapprove'
                                name='unapprove'
                                onClick={ this.handleStatusChange }
                            />
                        </Localized>
                        :
                        // Approve Button
                        <Localized
                            id='history-translation-button-approve'
                            attrs={{ title: true }}
                        >
                            <button
                                className='approve fa'
                                title='Approve'
                                name='approve'
                                onClick={ this.handleStatusChange }
                            />
                        </Localized>
                    }
                    { translation.rejected ?
                        // Unreject Button
                        <Localized
                            id='history-translation-button-unreject'
                            attrs={{ title: true }}
                        >
                            <button
                                className='unreject fa'
                                title='Unreject'
                                name='unreject'
                                onClick={ this.handleStatusChange }
                            />
                        </Localized>
                        :
                        // Reject Button
                        <Localized
                            id='history-translation-button-reject'
                            attrs={{ title: true }}
                        >
                            <button
                                className='reject fa'
                                title='Reject'
                                name='reject'
                                onClick={ this.handleStatusChange }
                            />
                        </Localized>
                    }
                    </menu>
                </header>
                <p
                    className={ this.state.isDiffVisible ? 'diff' : 'default' }
                    dir={ locale.direction }
                    lang={ locale.code }
                    data-script={ locale.script }
                >
                    { this.state.isDiffVisible ?
                        <TranslationPlaceablesDiff
                            diffTarget={ activeTranslation.string }
                        >
                            { translation.string }
                        </TranslationPlaceablesDiff>
                    :
                        <WithPlaceables>
                            { translation.string }
                        </WithPlaceables>
                    }
                </p>
            </li>
        </Localized>;
    }
}
