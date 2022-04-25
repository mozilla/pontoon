import LinkifyIt from 'linkify-it';
import React, { useEffect, useState } from 'react';
import tlds from 'tlds';

import './Screenshots.css';

// Create and configure a URLs matcher.
const linkify = new LinkifyIt();
linkify.tlds(tlds);

function getImageURLs(source: string, locale: string) {
  const matches = linkify.match(source);
  if (!matches) {
    return [];
  }
  return matches
    .filter((match) => /(https?:\/\/.*\.(?:png|jpg))/im.test(match.url))
    .map((match) => match.url.replace(/en-US\//gi, locale + '/'));
}

type Props = {
  locale: string;
  source: string;
};

/**
 * Shows screenshot miniatures based on the content of a string.
 *
 * This component looks at all URLs to an image (either .png or .jpg) in a
 * source string and then shows a miniature of those images.
 *
 * On image click, shows the image in a fullscreen lightbox with a grey background.
 * Click or press a key to close.
 */
export default function Screenshots({ locale, source }: Props) {
  const [openImage, setOpenImage] = useState<string | null>(null);

  useEffect(() => {
    if (!openImage) {
      return;
    }

    const handleKeyDown = ({ code }: KeyboardEvent) => {
      if (
        code === 'Enter' ||
        code === 'Escape' ||
        code === 'Space' ||
        code === 'Tab'
      ) {
        setOpenImage(null);
      }
    };

    window.document.addEventListener('keydown', handleKeyDown);
    return () => {
      window.document.removeEventListener('keydown', handleKeyDown);
    };
  }, [!openImage]);

  const images = getImageURLs(source, locale);

  return images.length > 0 ? (
    <>
      <div className='screenshots'>
        {images.map((urlWithLocale) => (
          <img
            src={urlWithLocale}
            alt=''
            key={urlWithLocale}
            onClick={() => setOpenImage(urlWithLocale)}
          />
        ))}
      </div>
      {openImage ? (
        <div className='lightbox' onClick={() => setOpenImage(null)}>
          <img src={openImage} alt='' />
        </div>
      ) : null}
    </>
  ) : null;
}
