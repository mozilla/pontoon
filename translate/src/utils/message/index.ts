import type { Message } from '@mozilla/l10n';

export type MessageEntry =
  | {
      id: string;
      value: Message;
      attributes?: never;
    }
  | {
      id: string;
      value: Message | null;
      attributes: Map<string, Message>;
    };

export { buildMessageEntry } from './buildMessageEntry';
export { extractAccessKeyCandidates } from './extractAccessKeyCandidates';
export { getEmptyMessageEntry } from './getEmptyMessage';
export { getPlainMessage } from './getPlainMessage';
export { editMessageEntry, editSource } from './editMessageEntry';
export { parseEntry } from './parseEntry';
export { requiresSourceView } from './requiresSourceView';
export { serializeEntry } from './serializeEntry';
