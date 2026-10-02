import type { Message } from '@mozilla/l10n';

import { GET } from './utils/base';

export type FluentTermType = {
  readonly value: Message;
  readonly properties: Record<string, Message> | null;
  readonly translation_value: Message | null;
  readonly translation_properties: Record<string, Message> | null;
};

export type FluentTerms = Record<string, FluentTermType>;

export async function fetchFluentTerms(
  project: string,
  locale: string,
): Promise<FluentTerms> {
  const search = new URLSearchParams({ project, locale });
  return await GET('/get-fluent-terms/', search);
}
