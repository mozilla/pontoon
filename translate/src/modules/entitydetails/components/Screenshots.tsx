import * as React from 'react';

import './Screenshots.css';
import { getImageURLs } from '~/core/linkify';
import { actions } from '~/core/lightbox';
import { useAppDispatch } from '~/hooks';

type Props = {
  locale: string;
  source: string;
};

/**
 * Shows screenshot miniatures based on the content of a string.
 *
 * This component looks at all URLs to an image (either .png or .jpg) in a
 * source string and then shows a miniature of those images.
 */
export default function Screenshots(props: Props) {
  const { locale, source } = props;
  const dispatch = useAppDispatch();

  const images = getImageURLs(source, locale);

  if (images.length === 0) {
    return null;
  }

  return (
    <div className='screenshots'>
      {images.map((urlWithLocale) => (
        <img
          src={urlWithLocale}
          alt=''
          key={urlWithLocale}
          onClick={() => dispatch(actions.open(urlWithLocale))}
        />
      ))}
    </div>
  );
}
