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

export { extractAccessKeyCandidates } from './extractAccessKeyCandidates';
export { getEmptyMessageEntry } from './getEmptyMessage';
export { getPlainMessage } from './getPlainMessage';
export { getReconstructedMessage } from './getReconstructedMessage';
export { getSimplePreview } from './getSimplePreview';
export { getSyntaxType } from './getSyntaxType';
export { findPluralSelectors } from './findPluralSelectors';
export { parseEntry } from './parseEntry';
export { serializeEntry, serializePattern } from './serialize';
