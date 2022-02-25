import React from 'react';

import type { Entity } from '~/core/api';
import type { Locale } from '~/core/locale';
import type { TermState } from '~/core/term';
import { FluentOriginalString } from '~/modules/fluentoriginal';

import GenericOriginalString from './GenericOriginalString';

type Props = {
  entity: Entity;
  locale: Locale;
  pluralForm: number;
  terms: TermState;
  handleClickOnPlaceable: (
    event: React.MouseEvent<HTMLParagraphElement>,
  ) => void;
};

/**
 * Proxy for an OriginalString component based on the format of the entity.
 *
 * For Fluent strings ('ftl'), returns a Fluent-specific OriginalString
 * component. For everything else, return a generic OriginalString component.
 */
export const OriginalStringProxy = ({
  entity,
  locale,
  pluralForm,
  terms,
  handleClickOnPlaceable,
}: Props): React.ReactElement<any> =>
  entity.format === 'ftl' ? (
    <FluentOriginalString
      entity={entity}
      terms={terms}
      handleClickOnPlaceable={handleClickOnPlaceable}
    />
  ) : (
    <GenericOriginalString
      entity={entity}
      locale={locale}
      pluralForm={pluralForm}
      terms={terms}
      handleClickOnPlaceable={handleClickOnPlaceable}
    />
  );
