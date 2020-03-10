/* @flow */

import * as React from 'react';
import ReactTimeAgo from 'react-time-ago';
import { Localized } from '@fluent/react';

import './Entry.css';

import CommentsSummary from './CommentsSummary';

import { CommentsList } from 'core/comments';
import { UserAvatar } from 'core/user';

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
    addComment: (string, ?number) => void,
    updateEditorTranslation: (string, string) => void,
    updateTranslationStatus: (number, ChangeOperation) => void,
|};


function getApprovalTitle(translation: HistoryTranslation) {
    if (translation.approved && translation.approvedUser) {
        return `Approved by ${translation.approvedUser}`;
    }
    if (translation.unapprovedUser) {
        return `Unapproved by ${translation.unapprovedUser}`;
    }
    return 'Not reviewed yet';
}


function getStatus(translation: HistoryTranslation) {
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


function Author(props: Props) {
    const { translation } = props;

    if (!translation.uid) {
        return <span>{ translation.user }</span>;
    }

    return <a
        href={ `/contributors/${translation.username}` }
        title={ getApprovalTitle(translation) }
        target='_blank'
        rel='noopener noreferrer'
        onClick={ (e: SyntheticMouseEvent<>) => e.stopPropagation() }
    >
        { translation.user }
    </a>;
}


function TranslationStatus(props: Props) {
    const { translation } = props;
    if (translation.approved) {
        return <i className='fas fa-check-circle' title='Approved' />;
    }
    if (translation.rejected) {
        return <i className='fas fa-times-circle' title='Rejected' />;
    }
    return <i className='fas fa-lightbulb' title='Unreviewed' />;
}


function TranslationControls(props: Props) {
    const {
        isTranslator,
        user,
        translation,
        deleteTranslation,
        updateTranslationStatus,
    } = props;

    function handleDelete(event: SyntheticMouseEvent<HTMLButtonElement>) {
        event.stopPropagation();
        deleteTranslation(translation.pk);
    }

    function handleStatusChange(event: SyntheticMouseEvent<HTMLButtonElement>) {
        event.stopPropagation();
        const action = event.currentTarget.name;
        // $FLOW_IGNORE
        updateTranslationStatus(translation.pk, action);
    }

    // Does the currently logged in user own this translation?
    const ownTranslation = (
        user && user.username &&
        user.username === translation.username
    );

    const canApprove = isTranslator;
    const canDelete = translation.rejected && (isTranslator || ownTranslation);
    const canReject = isTranslator || (ownTranslation && !translation.approved);

    let approveControl = null;
    let deleteControl = null;
    let rejectControl = null;
    let unapproveControl = null;
    let unrejectControl = null;

    if (canDelete) {
        deleteControl = <Localized
            id='history-TranslationControls--button-delete'
            attrs={{ title: true }}
        >
            <button
                title='Delete this translation'
                className='delete'
                onClick={ handleDelete }
            ><i className='fas fa-trash-alt' /></button>
        </Localized>;
    }

    if (canApprove) {
        if (!translation.approved) {
            approveControl = <Localized
                id='history-TranslationControls--button-approve'
                attrs={{ title: true }}
            >
                <button
                    title='Approve this translation'
                    name='approve'
                    className='approve'
                    onClick={ handleStatusChange }
                ><i className='fas fa-check' /></button>
            </Localized>;
        }
        else {
            unapproveControl = <Localized
                id='history-TranslationControls--button-unapprove'
                attrs={{ title: true }}
            >
                <button
                    title='Unapprove this translation'
                    name='unapprove'
                    className='unapprove'
                    onClick={ handleStatusChange }
                >Unapprove</button>
            </Localized>;
        }
    }

    if (canReject) {
        if (!translation.rejected) {
            rejectControl = <Localized
                id='history-TranslationControls--button-reject'
                attrs={{ title: true }}
            >
                <button
                    title='Reject this translation'
                    name='reject'
                    className='reject'
                    onClick={ handleStatusChange }
                ><i className='fas fa-times' /></button>
            </Localized>;
        }
        else {
            unrejectControl = <Localized
                id='history-TranslationControls--button-unreject'
                attrs={{ title: true }}
            >
                <button
                    title='Unreject this translation'
                    name='unreject'
                    className='unreject'
                    onClick={ handleStatusChange }
                >Unreject</button>
            </Localized>;
        }
    }

    return <div className='controls'>
        { unapproveControl }
        { unrejectControl }
        { deleteControl }
        { rejectControl }
        { approveControl }
    </div>;
}


/**
 * Render a translation in the History tab.
 *
 * Shows the translation's status, date, author and reviewer, as well as
 * the content of the translation.
 *
 * The status can be interacted with if the user has sufficient permissions to
 * change said status.
 */
export default function Entry(props: Props) {
    const {
        isReadOnlyEditor,
        translation,
        user,
        addComment,
    } = props;

    const [ areCommentsVisible, setCommentsVisibility ] = React.useState(false);

    return <li className='history-entry'>
        <div className={ 'translation ' + getStatus(translation) }>
            <UserAvatar
                username={ translation.username }
                title={ getApprovalTitle(translation) }
                imageUrl={ translation.userGravatarUrlSmall }
            />
            <div className='content'>
                <header className='clearfix'>
                    <div className='info'>
                        <Author { ...props } />
                        <ReactTimeAgo
                            dir='ltr'
                            date={ new Date(translation.dateIso) }
                            title={ `${translation.date} UTC` }
                        />
                    </div>
                    <div className='status'>
                        <TranslationStatus { ...props } />
                    </div>
                </header>
                <p>{ translation.string }</p>
            </div>
        </div>
        <div className='actions'>
            <CommentsSummary
                comments={ translation.comments }
                areCommentsVisible={ areCommentsVisible }
                setCommentsVisibility={ setCommentsVisibility }
            />
            { isReadOnlyEditor ? null : <TranslationControls { ...props } /> }
        </div>
        { !areCommentsVisible ? null :
            <CommentsList
                comments={ translation.comments }
                translation={ translation }
                user={ user }
                canComment={ user.isAuthenticated }
                addComment={ addComment }
            />
        }
    </li>;
}
