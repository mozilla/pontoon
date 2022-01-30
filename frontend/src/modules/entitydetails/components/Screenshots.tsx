import * as React from 'react';

import './Screenshots.css';
import { getImageURLs } from 'core/linkify';

type Props = {
    locale: string;
    source: string;
    openLightbox: (image: string) => void;
};

/**
 * Shows screenshot miniatures based on the content of a string.
 *
 * This component looks at all URLs to an image (either .png or .jpg) in a
 * source string and then shows a miniature of those images.
 */
export default function Screenshots(props: Props) {
    const { locale, openLightbox, source } = props;

    const images = getImageURLs(source, locale);

    if (images.length === 0) {
        return null;
    }

    return (
        <div className='screenshots'>
            {images.map((urlWithLocale, i) => (
                <img
                    src={urlWithLocale}
                    alt=''
                    key={i}
                    onClick={() => openLightbox(urlWithLocale)}
                />
            ))}
        </div>
    );
}
