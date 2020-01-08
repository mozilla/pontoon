/* @flow */

import * as React from 'react';
import ReactTimeAgo from 'react-time-ago';
import { Localized } from '@fluent/react';

import './Translation.css';

import { TranslationProxy } from 'core/translation';
import { CommentsList } from 'core/comments';
import { UserAvatar } from 'core/user';
import * as utils from 'core/utils';

import type { Entity } from 'core/api';
import type { Locale } from 'core/locale';
import type { UserState } from 'core/user';
import type { ChangeOperation } from '..';
import type { HistoryTranslation } from '../reducer';


type Props = {|
    entity: Entity,
    isReadOnlyEditor: boolean,
    isTranslator: boolean,
    translation: HistoryTranslation,
    activeTranslation: HistoryTranslation,
    locale: Locale,
    user: UserState,
    index: number,
    deleteTranslation: (number) => void,
    deleteComment: (number) => void,
    updateEditorTranslation: (string, string) => void,
    updateTranslationStatus: (number, ChangeOperation) => void,
|};

type InternalProps = {|
    ...Props,
    isActionDisabled: boolean,
    disableAction: () => void,
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
export class TranslationBase extends React.Component<InternalProps, State> {
    constructor(props: InternalProps) {
        super(props);

        this.state = {
            isDiffVisible: false,
        };
    }

    handleStatusChange = (event: SyntheticMouseEvent<HTMLButtonElement>) => {
        if (this.props.isActionDisabled) {
            return;
        }
        this.props.disableAction();

        event.stopPropagation();
        // $FLOW_IGNORE: Flow and the DOM… >_<
        const action = event.target.name;

        this.props.updateTranslationStatus(this.props.translation.pk, action);
    }

    delete = (event: SyntheticMouseEvent<HTMLButtonElement>) => {
        if (this.props.isActionDisabled) {
            return;
        }
        this.props.disableAction();

        event.stopPropagation();
        this.props.deleteTranslation(this.props.translation.pk);
    }

    copyTranslationIntoEditor = () => {
        if (this.props.isReadOnlyEditor) {
            return;
        }

        // Ignore if selecting text
        if (window.getSelection().toString()) {
            return;
        }

        this.props.updateEditorTranslation(this.props.translation.string, 'history');
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

        if (translation.approved && translation.approvedUser) {
            return `Approved by ${translation.approvedUser}`;
        }
        if (translation.unapprovedUser) {
            return `Unapproved by ${translation.unapprovedUser}`;
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
                id='history-Translation--hide-diff'
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
                id='history-Translation--show-diff'
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
            isTranslator,
            entity,
            isReadOnlyEditor,
            translation,
            locale,
            user,
            activeTranslation,
            deleteComment,
        } = this.props;

        // Does the currently logged in user own this translation?
        const ownTranslation = (
            user && user.username &&
            user.username === translation.username
        );

        let className = 'translation ' + this.getStatus();

        if (isReadOnlyEditor) {
            // Copying into the editor is not allowed
            className += ' cannot-copy';
        }

        if (isTranslator && !isReadOnlyEditor) {
            // This user is a translator for the current locale, they can
            // perform all review actions.
            className += ' can-approve can-reject';
        }
        else if (ownTranslation && !translation.approved && !isReadOnlyEditor) {
            // This user owns the translation and it's not approved, they
            // can only reject or unreject it.
            className += ' can-reject';
        }

        let canDelete = (isTranslator || ownTranslation) && !isReadOnlyEditor;
        let canReject = (isTranslator || (ownTranslation && !translation.approved)) && !isReadOnlyEditor;

        return <li className='divider'>
            <Localized id='history-Translation--copy' attrs={{ title: true }}>
                <div
                    className={ className }
                    title='Copy Into Translation'
                    onClick={ this.copyTranslationIntoEditor }
                >
                    <UserAvatar
                        user={ translation.user }
                        username={ translation.username }
                        title={ this.getApprovalTitle() }
                        imageUrl={ translation.userGravatarUrlSmall }
                    />
                    <div className='content'>
                        <header className='clearfix'>
                            <div className='info'>
                                { this.renderUser() }
                                <ReactTimeAgo
                                    dir='ltr'
                                    date={ new Date(translation.dateIso) }
                                    title={ `${translation.date} UTC` }
                                />
                            </div>
                            <menu className='toolbar'>

                            { this.renderDiffToggle() }

                            { (!translation.rejected || !canDelete ) ? null :
                                // Delete Button
                                <Localized
                                    id='history-Translation--button-delete'
                                    attrs={{ title: true }}
                                >
                                    <button
                                        className='delete far'
                                        title='Delete'
                                        onClick={ this.delete }
                                        disabled={ this.props.isActionDisabled }
                                    />
                                </Localized>
                            }
                            { translation.approved ?
                                // Unapprove Button
                                ( isTranslator && !isReadOnlyEditor ) ?
                                    <Localized
                                        id='history-Translation--button-unapprove'
                                        attrs={{ title: true }}
                                    >
                                        <button
                                            className='unapprove fa'
                                            title='Unapprove'
                                            name='unapprove'
                                            onClick={ this.handleStatusChange }
                                            disabled={ this.props.isActionDisabled }
                                        />
                                    </Localized>
                                    :
                                    <Localized
                                        id='history-Translation--button-approved'
                                        attrs={{ title: true }}
                                    >
                                        <button
                                            className='unapprove fa'
                                            title='Approved'
                                            disabled
                                        />
                                    </Localized>

                                :
                                // Approve Button
                                ( isTranslator && !isReadOnlyEditor ) ?
                                    <Localized
                                        id='history-Translation--button-approve'
                                        attrs={{ title: true }}
                                    >
                                        <button
                                            className='approve fa'
                                            title='Approve'
                                            name='approve'
                                            onClick={ this.handleStatusChange }
                                            disabled={ this.props.isActionDisabled }
                                        />
                                    </Localized>
                                    :
                                    <Localized
                                        id='history-Translation--button-not-approved'
                                        attrs={{ title: true }}
                                    >
                                        <button
                                            className='approve fa'
                                            title='Not approved'
                                            disabled
                                        />
                                    </Localized>
                            }
                            { translation.rejected ?
                                // Unreject Button
                                canReject ?
                                    <Localized
                                        id='history-Translation--button-unreject'
                                        attrs={{ title: true }}
                                    >
                                        <button
                                            className='unreject fa'
                                            title='Unreject'
                                            name='unreject'
                                            onClick={ this.handleStatusChange }
                                            disabled={ this.props.isActionDisabled }
                                        />
                                    </Localized>
                                    :
                                    <Localized
                                        id='history-Translation--button-rejected'
                                        attrs={{ title: true }}
                                    >
                                        <button
                                            className='unreject fa'
                                            title='Rejected'
                                            disabled
                                        />
                                    </Localized>
                                :
                                // Reject Button
                                canReject ?
                                    <Localized
                                        id='history-Translation--button-reject'
                                        attrs={{ title: true }}
                                    >
                                        <button
                                            className='reject fa'
                                            title='Reject'
                                            name='reject'
                                            onClick={ this.handleStatusChange }
                                            disabled={ this.props.isActionDisabled }
                                        />
                                    </Localized>
                                    :
                                    <Localized
                                        id='history-Translation--button-not-rejected'
                                        attrs={{ title: true }}
                                    >
                                        <button
                                            className='reject fa'
                                            title='Not rejected'
                                            disabled
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
                            <TranslationProxy
                                content={ translation.string }
                                diffTarget={
                                    this.state.isDiffVisible ? activeTranslation.string : null
                                }
                                format={ entity.format }
                            />
                        </p>
                    </div>
                </div>
            </Localized>
            <CommentsList
                comments={ translation.comments }
                user={ user }
                isTranslator={ isTranslator }
                translation={ translation }
                deleteComment={ deleteComment }
            />
        </li>;
    }
}


export default utils.withActionsDisabled(TranslationBase);
