import { MessageEntry } from '~/utils/message';

export function getMessageEntryFormat(format: string): MessageEntry['format'] {
  switch (format) {
    case 'gettext':
    case 'fluent':
      return format;
    default:
      return 'plain';
  }
}
