import React from 'react';
import { Localized } from '@fluent/react';

import type { NotificationMessage } from '~/context/Notification';

export const TRANSLATION_APPROVED: NotificationMessage = {
  content: (
    <Localized id='notification--translation-approved'>
      Translation approved
    </Localized>
  ),
  type: 'info',
};

export const TRANSLATION_UNAPPROVED: NotificationMessage = {
  content: (
    <Localized id='notification--translation-unapproved'>
      Translation unapproved
    </Localized>
  ),
  type: 'info',
};

export const TRANSLATION_REJECTED: NotificationMessage = {
  content: (
    <Localized id='notification--translation-rejected'>
      Translation rejected
    </Localized>
  ),
  type: 'info',
};

export const TRANSLATION_UNREJECTED: NotificationMessage = {
  content: (
    <Localized id='notification--translation-unrejected'>
      Translation unrejected
    </Localized>
  ),
  type: 'info',
};

export const TRANSLATION_DELETED: NotificationMessage = {
  content: (
    <Localized id='notification--translation-deleted'>
      Translation deleted
    </Localized>
  ),
  type: 'info',
};

export const TRANSLATION_SAVED: NotificationMessage = {
  content: (
    <Localized id='notification--translation-saved'>
      Translation saved
    </Localized>
  ),
  type: 'info',
};

export const UNABLE_TO_APPROVE_TRANSLATION: NotificationMessage = {
  content: (
    <Localized id='notification--unable-to-approve-translation'>
      Unable to approve translation
    </Localized>
  ),
  type: 'error',
};

export const UNABLE_TO_UNAPPROVE_TRANSLATION: NotificationMessage = {
  content: (
    <Localized id='notification--unable-to-unapprove-translation'>
      Unable to unapprove translation
    </Localized>
  ),
  type: 'error',
};

export const UNABLE_TO_REJECT_TRANSLATION: NotificationMessage = {
  content: (
    <Localized id='notification--unable-to-reject-translation'>
      Unable to reject translation
    </Localized>
  ),
  type: 'error',
};

export const UNABLE_TO_UNREJECT_TRANSLATION: NotificationMessage = {
  content: (
    <Localized id='notification--unable-to-unreject-translation'>
      Unable to unreject translation
    </Localized>
  ),
  type: 'error',
};

export const UNABLE_TO_DELETE_TRANSLATION: NotificationMessage = {
  content: (
    <Localized id='notification--unable-to-delete-translation'>
      Unable to delete translation
    </Localized>
  ),
  type: 'error',
};

export const SAME_TRANSLATION: NotificationMessage = {
  content: (
    <Localized id='notification--same-translation'>
      Same translation already exists
    </Localized>
  ),
  type: 'error',
};

export const CHECKS_ENABLED: NotificationMessage = {
  content: (
    <Localized id='notification--tt-checks-enabled'>
      Translate Toolkit Checks enabled
    </Localized>
  ),
  type: 'info',
};

export const CHECKS_DISABLED: NotificationMessage = {
  content: (
    <Localized id='notification--tt-checks-disabled'>
      Translate Toolkit Checks disabled
    </Localized>
  ),
  type: 'info',
};

export const SUGGESTIONS_ENABLED: NotificationMessage = {
  content: (
    <Localized id='notification--make-suggestions-enabled'>
      Make Suggestions enabled
    </Localized>
  ),
  type: 'info',
};

export const SUGGESTIONS_DISABLED: NotificationMessage = {
  content: (
    <Localized id='notification--make-suggestions-disabled'>
      Make Suggestions disabled
    </Localized>
  ),
  type: 'info',
};

export const FTL_NOT_SUPPORTED_RICH_EDITOR: NotificationMessage = {
  content: (
    <Localized id='notification--ftl-not-supported-rich-editor'>
      Translation not supported in rich editor
    </Localized>
  ),
  type: 'error',
};

export const ENTITY_NOT_FOUND: NotificationMessage = {
  content: (
    <Localized id='notification--entity-not-found'>
      Can’t load specified string
    </Localized>
  ),
  type: 'error',
};

export const STRING_LINK_COPIED: NotificationMessage = {
  content: (
    <Localized id='notification--string-link-copied'>
      Link copied to clipboard
    </Localized>
  ),
  type: 'info',
};

export const COMMENT_ADDED: NotificationMessage = {
  content: (
    <Localized id='notification--comment-added'>Comment added</Localized>
  ),
  type: 'info',
};
