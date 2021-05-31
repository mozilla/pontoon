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

import type { ChangeOperation, HistoryTranslation } from '..';

type Props = {
    entity: Entity;
    isReadOnlyEditor: boolean;
    isTranslator: boolean;
    translation: HistoryTranslation;
    activeTranslation: HistoryTranslation;
    locale: Locale;
    user: UserState;
    index: number;
    deleteTranslation: (id: number) => void;
    addComment: (comment: string, id: number | null | undefined) => void;
    updateEditorTranslation: (arg0: string, arg1: string) => void;
    updateTranslationStatus: (id: number, operation: ChangeOperation) => void;
};

type InternalProps = Props & {
    isActionDisabled: boolean;
    disableAction: () => void;
};

type State = {
    isDiffVisible: boolean;
    areCommentsVisible: boolean;
};

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
            areCommentsVisible: false,
        };
    }

    handleStatusChange: (event: React.MouseEvent<HTMLButtonElement>) => void = (
        event: React.MouseEvent<HTMLButtonElement>,
    ) => {
        if (this.props.isActionDisabled) {
            return;
        }
        this.props.disableAction();

        event.stopPropagation();
        const action = (event.currentTarget.name as any) as ChangeOperation;

        this.props.updateTranslationStatus(this.props.translation.pk, action);
    };

    delete: (event: React.MouseEvent<HTMLButtonElement>) => void = (
        event: React.MouseEvent<HTMLButtonElement>,
    ) => {
        if (this.props.isActionDisabled) {
            return;
        }
        this.props.disableAction();

        event.stopPropagation();
        this.props.deleteTranslation(this.props.translation.pk);
    };

    copyTranslationIntoEditor: () => void = () => {
        if (this.props.isReadOnlyEditor) {
            return;
        }

        // Ignore if selecting text
        if (window.getSelection().toString()) {
            return;
        }

        this.props.updateEditorTranslation(
            this.props.translation.string,
            'history',
        );
    };

    getStatus(): string {
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

    getApprovalTitle(): string {
        const { translation } = this.props;

        // TODO: To Localize.
        if (translation.approved && translation.approvedUser) {
            return `Approved by ${translation.approvedUser}`;
        }
        if (translation.unapprovedUser) {
            return `Unapproved by ${translation.unapprovedUser}`;
        }
        return 'Not reviewed yet';
    }

    renderUser(): React.ReactElement<'a'> | React.ReactElement<'span'> {
        const { translation } = this.props;

        if (!translation.uid) {
            return <span>{translation.user}</span>;
        }

        return (
            <a
                href={`/contributors/${translation.username}`}
                title={this.getApprovalTitle()}
                target='_blank'
                rel='noopener noreferrer'
                onClick={(e: React.MouseEvent) => e.stopPropagation()}
            >
                {translation.user}
            </a>
        );
    }

    toggleComments: (event: React.MouseEvent) => void = (
        event: React.MouseEvent,
    ) => {
        event.stopPropagation();
        this.setState((state) => {
            return { areCommentsVisible: !state.areCommentsVisible };
        });
    };

    renderCommentToggle(commentCount: number): React.ReactNode {
        const className =
            'toggle comments ' + (this.state.areCommentsVisible ? 'on' : 'off');
        const title = 'Toggle translation comments';

        if (commentCount === 0) {
            return (
                <Localized
                    id='history-Translation--button-comment'
                    attrs={{ title: true }}
                >
                    <button
                        className={className}
                        title={title}
                        onClick={this.toggleComments}
                    >
                        {'COMMENT'}
                    </button>
                </Localized>
            );
        } else {
            return (
                <Localized
                    id='history-Translation--button-comments'
                    attrs={{ title: true }}
                    elems={{ stress: <span className='stress' /> }}
                    vars={{ commentCount }}
                >
                    <button
                        className={className + ' active'}
                        title={title}
                        onClick={this.toggleComments}
                    >
                        {'<stress>{ $commentCount }</stress> COMMENTS'}
                    </button>
                </Localized>
            );
        }
    }

    toggleDiff: (event: React.MouseEvent) => void = (
        event: React.MouseEvent,
    ) => {
        event.stopPropagation();
        this.setState((state) => {
            return { isDiffVisible: !state.isDiffVisible };
        });
    };

    renderDiffToggle(): null | React.ReactNode {
        const { index } = this.props;

        if (index === 0) {
            return null;
        }

        return (
            <Localized
                id='history-Translation--toggle-diff'
                attrs={{ title: true }}
            >
                <button
                    className={
                        'toggle diff ' +
                        (this.state.isDiffVisible ? 'on' : 'off')
                    }
                    title='Toggle diff against the currently active translation'
                    onClick={this.toggleDiff}
                >
                    {'DIFF'}
                </button>
            </Localized>
        );
    }

    render(): React.ReactElement<'li'> {
        const {
            isTranslator,
            entity,
            isReadOnlyEditor,
            translation,
            locale,
            user,
            activeTranslation,
            addComment,
        } = this.props;

        const commentCount = translation.comments.length;

        // Does the currently logged in user own this translation?
        const ownTranslation =
            user && user.username && user.username === translation.username;

        let className = 'translation ' + this.getStatus();

        if (isReadOnlyEditor) {
            // Copying into the editor is not allowed
            className += ' cannot-copy';
        }

        if (isTranslator && !isReadOnlyEditor) {
            // This user is a translator for the current locale, they can
            // perform all review actions.
            className += ' can-approve can-reject';
        } else if (
            ownTranslation &&
            !translation.approved &&
            !isReadOnlyEditor
        ) {
            // This user owns the translation and it's not approved, they
            // can only reject or unreject it.
            className += ' can-reject';
        }

        let canDelete = (isTranslator || ownTranslation) && !isReadOnlyEditor;
        let canReject =
            (isTranslator || (ownTranslation && !translation.approved)) &&
            !isReadOnlyEditor;
        let canComment = user.isAuthenticated;

        return (
            <li className='wrapper'>
                <Localized
                    id='history-Translation--copy'
                    attrs={{ title: true }}
                >
                    <div
                        className={className}
                        title='Copy Into Translation'
                        onClick={this.copyTranslationIntoEditor}
                    >
                        <div className='avatar-container'>
                            <UserAvatar
                                username={translation.username}
                                title={this.getApprovalTitle()}
                                imageUrl={translation.userGravatarUrlSmall}
                            />
                            {!translation.machinerySources ? null : (
                                <Localized
                                    id='history-Translation--span-copied'
                                    attrs={{ title: true }}
                                    vars={{
                                        machinerySources:
                                            translation.machinerySources,
                                    }}
                                >
                                    <span
                                        className='fa machinery-sources'
                                        title={'Copied ({ $machinerySources })'}
                                    ></span>
                                </Localized>
                            )}
                        </div>
                        <div className='content'>
                            <header className='clearfix'>
                                <div className='info'>
                                    {this.renderUser()}
                                    <ReactTimeAgo
                                        dir='ltr'
                                        date={new Date(translation.dateIso)}
                                        title={`${translation.date} UTC`}
                                    />
                                </div>
                                <menu className='toolbar'>
                                    {this.renderDiffToggle()}

                                    {!canComment && commentCount === 0
                                        ? null
                                        : this.renderCommentToggle(
                                              commentCount,
                                          )}

                                    {!translation.rejected ||
                                    !canDelete ? null : (
                                        // Delete Button
                                        <Localized
                                            id='history-Translation--button-delete'
                                            attrs={{ title: true }}
                                        >
                                            <button
                                                className='delete far'
                                                title='Delete'
                                                onClick={this.delete}
                                                disabled={
                                                    this.props.isActionDisabled
                                                }
                                            />
                                        </Localized>
                                    )}
                                    {translation.approved ? (
                                        // Unapprove Button
                                        isTranslator && !isReadOnlyEditor ? (
                                            <Localized
                                                id='history-Translation--button-unapprove'
                                                attrs={{ title: true }}
                                            >
                                                <button
                                                    className='unapprove fa'
                                                    title='Unapprove'
                                                    name='unapprove'
                                                    onClick={
                                                        this.handleStatusChange
                                                    }
                                                    disabled={
                                                        this.props
                                                            .isActionDisabled
                                                    }
                                                />
                                            </Localized>
                                        ) : (
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
                                        )
                                    ) : // Approve Button
                                    isTranslator && !isReadOnlyEditor ? (
                                        <Localized
                                            id='history-Translation--button-approve'
                                            attrs={{ title: true }}
                                        >
                                            <button
                                                className='approve fa'
                                                title='Approve'
                                                name='approve'
                                                onClick={
                                                    this.handleStatusChange
                                                }
                                                disabled={
                                                    this.props.isActionDisabled
                                                }
                                            />
                                        </Localized>
                                    ) : (
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
                                    )}
                                    {translation.rejected ? (
                                        // Unreject Button
                                        canReject ? (
                                            <Localized
                                                id='history-Translation--button-unreject'
                                                attrs={{ title: true }}
                                            >
                                                <button
                                                    className='unreject fa'
                                                    title='Unreject'
                                                    name='unreject'
                                                    onClick={
                                                        this.handleStatusChange
                                                    }
                                                    disabled={
                                                        this.props
                                                            .isActionDisabled
                                                    }
                                                />
                                            </Localized>
                                        ) : (
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
                                        )
                                    ) : // Reject Button
                                    canReject ? (
                                        <Localized
                                            id='history-Translation--button-reject'
                                            attrs={{ title: true }}
                                        >
                                            <button
                                                className='reject fa'
                                                title='Reject'
                                                name='reject'
                                                onClick={
                                                    this.handleStatusChange
                                                }
                                                disabled={
                                                    this.props.isActionDisabled
                                                }
                                            />
                                        </Localized>
                                    ) : (
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
                                    )}
                                </menu>
                            </header>
                            <p
                                className={
                                    this.state.isDiffVisible
                                        ? 'diff-visible'
                                        : 'default'
                                }
                                dir={locale.direction}
                                lang={locale.code}
                                data-script={locale.script}
                            >
                                <TranslationProxy
                                    content={translation.string}
                                    diffTarget={
                                        this.state.isDiffVisible
                                            ? activeTranslation.string
                                            : null
                                    }
                                    format={entity.format}
                                />
                            </p>
                        </div>
                    </div>
                </Localized>
                {!this.state.areCommentsVisible ? null : (
                    <CommentsList
                        comments={translation.comments}
                        translation={translation}
                        user={user}
                        canComment={canComment}
                        addComment={addComment}
                    />
                )}
            </li>
        );
    }
}

export default utils.withActionsDisabled(TranslationBase) as any;
