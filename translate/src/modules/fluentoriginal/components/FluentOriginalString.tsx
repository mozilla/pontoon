import React from 'react';

import type { Entity } from '~/api/entity';
import type { TermState } from '~/core/term';
import { getSyntaxType, parseEntry } from '~/utils/message';

import { RichString } from './RichString';
import { SimpleString } from './SimpleString';
import { SourceString } from './SourceString';

type Props = {
  readonly entity: Entity;
  readonly terms: TermState;
  readonly handleClickOnPlaceable: (
    event: React.MouseEvent<HTMLParagraphElement>,
  ) => void;
};

/**
 * Show the original string of a Fluent entity.
 *
 * Based on the syntax type of the string, render it as a simple string preview,
 * as a rich UI or as the original, untouched string.
 */
export function FluentOriginalString(props: Props): React.ReactElement<any> {
  const message = parseEntry(props.entity.original);
  const syntax = getSyntaxType(message);

  if (syntax === 'simple') {
    return (
      <SimpleString
        entity={props.entity}
        terms={props.terms}
        handleClickOnPlaceable={props.handleClickOnPlaceable}
      />
    );
  }

  if (syntax === 'rich') {
    return (
      <RichString
        entity={props.entity}
        terms={props.terms}
        handleClickOnPlaceable={props.handleClickOnPlaceable}
      />
    );
  }

  // Complex, unsupported strings.
  return (
    <SourceString
      entity={props.entity}
      terms={props.terms}
      handleClickOnPlaceable={props.handleClickOnPlaceable}
    />
  );
}
