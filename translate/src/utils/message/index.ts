import type { Model } from 'messageformat';

export type MessageEntry =
  | {
      id: string;
      value: Model.Message;
      attributes?: never;
    }
  | {
      id: string;
      value: Model.Message | null;
      attributes: Map<string, Model.Message>;
    };

export { buildMessageEntry } from './buildMessageEntry';
export { extractAccessKeyCandidates } from './extractAccessKeyCandidates';
export { getEmptyMessageEntry } from './getEmptyMessage';
export { getPlainMessage } from './getPlainMessage';
export { editMessageEntry, editSource } from './editMessageEntry';
export { findPluralSelectors } from './findPluralSelectors';
export { parseEntry } from './parseEntry';
export { requiresSourceView } from './requiresSourceView';
export { serializeEntry } from './serializeEntry';
