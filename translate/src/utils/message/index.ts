import type { Message } from 'messageformat';

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
export { getSimplePreview } from './getSimplePreview';
export { editMessageEntry } from './editMessageEntry';
export { findPluralSelectors } from './findPluralSelectors';
export { parseEntry } from './parseEntry';
export { requiresSourceView } from './requiresSourceView';
export { serializeEntry } from './serializeEntry';
