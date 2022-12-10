import React from 'react';

import { FluentTranslation } from './FluentTranslation';
import { GenericTranslation } from './GenericTranslation';

type Props = {
  content: string;
  format: string;
  diffTarget?: string;
  search?: string | null;
};

export function Translation({
  format,
  ...props
}: Props): null | React.ReactElement<React.ElementType> {
  if (!props.content) {
    return null;
  }

  const Translation = format === 'ftl' ? FluentTranslation : GenericTranslation;
  return <Translation {...props} />;
}
