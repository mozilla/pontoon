import { MessageEntry } from '~/utils/message';

export function getMessageEntryFormat(format: string): MessageEntry['format'] {
  switch (format) {
    case 'android':
    case 'gettext':
    case 'fluent':
    case 'webext':
    case 'xcode':
    case 'xliff':
      return format;
    default:
      return 'plain';
  }
}
