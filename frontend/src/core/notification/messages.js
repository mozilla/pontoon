import * as React from 'react';
import { Localized } from '@fluent/react';
import type { NotificationMessage } from './actions';

const messages: { [key: string]: NotificationMessage } = {
    TRANSLATION_APPROVED: {
        content: (
            <Localized id='notification--translation-approved'>
                Translation approved
            </Localized>
        ),
        type: 'info',
    },
    TRANSLATION_UNAPPROVED: {
        content: (
            <Localized id='notification--translation-unaproved'>
                Translation unaproved
            </Localized>
        ),
        type: 'info',
    },
    TRANSLATION_REJECTED: {
        content: (
            <Localized id='notification--translation-rejected'>
                Translation rejected
            </Localized>
        ),
        type: 'info',
    },
    TRANSLATION_UNREJECTED: {
        content: (
            <Localized id='notification--translation-unrejected'>
                Translation unrejected
            </Localized>
        ),
        type: 'info',
    },
    TRANSLATION_DELETED: {
        content: (
            <Localized id='notification--translation-deleted'>
                Translation deleted
            </Localized>
        ),
        type: 'info',
    },
    TRANSLATION_SAVED: {
        content: (
            <Localized id='notification--translation-saved'>
                Translation saved
            </Localized>
        ),
        type: 'info',
    },
    UNABLE_TO_APPROVE_TRANSLATION: {
        content: (
            <Localized id='notification--unable-to-approve-translation'>
                Unable to approve translation
            </Localized>
        ),
        type: 'error',
    },
    UNABLE_TO_UNAPPROVE_TRANSLATION: {
        content: (
            <Localized id='notification--unable-to-unapprove-translation'>
                Unable to unapprove translation
            </Localized>
        ),
        type: 'error',
    },
    UNABLE_TO_REJECT_TRANSLATION: {
        content: (
            <Localized id='notification--unable-to-reject-translation'>
                Unable to reject translation
            </Localized>
        ),
        type: 'error',
    },
    UNABLE_TO_UNREJECT_TRANSLATION: {
        content: (
            <Localized id='notification--unable-to-unreject-translation'>
                Unable to unreject translation
            </Localized>
        ),
        type: 'error',
    },
    UNABLE_TO_DELETE_TRANSLATION: {
        content: (
            <Localized id='notification--unable-to-delete-translation'>
                Unable to delete translation
            </Localized>
        ),
        type: 'error',
    },
    SAME_TRANSLATION: {
        content: (
            <Localized id='notification--same-translation'>
                Same translation already exists
            </Localized>
        ),
        type: 'error',
    },
    CHECKS_ENABLED: {
        content: (
            <Localized id='notification--tt-checks-enabled'>
                Translate Toolkit Checks enabled
            </Localized>
        ),
        type: 'info',
    },
    CHECKS_DISABLED: {
        content: (
            <Localized id='notification--tt-checks-disabled'>
                Translate Toolkit Checks disabled
            </Localized>
        ),
        type: 'info',
    },
    SUGGESTIONS_ENABLED: {
        content: (
            <Localized id='notification--make-suggestions-enabled'>
                Make Suggestions enabled
            </Localized>
        ),
        type: 'info',
    },
    SUGGESTIONS_DISABLED: {
        content: (
            <Localized id='notification--make-suggestions-disabled'>
                Make Suggestions disabled
            </Localized>
        ),
        type: 'info',
    },
    FTL_NOT_SUPPORTED_RICH_EDITOR: {
        content: (
            <Localized id='notification--ftl-not-supported-rich-editor'>
                Translation not supported in rich editor
            </Localized>
        ),
        type: 'error',
    },
    ENTITY_NOT_FOUND: {
        content: (
            <Localized id='notification--entity-not-found'>
                Can’t load specified string
            </Localized>
        ),
        type: 'error',
    },
    STRING_LINK_COPIED: {
        content: (
            <Localized id='notification--string-link-copied'>
                Link copied to clipboard
            </Localized>
        ),
        type: 'info',
    },
    COMMENT_ADDED: {
        content: (
            <Localized id='notification--comment-added'>
                Comment added
            </Localized>
        ),
        type: 'info',
    },
};

export default messages;
