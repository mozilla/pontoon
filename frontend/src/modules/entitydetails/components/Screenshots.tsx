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
export default class Screenshots extends React.Component<Props> {
    openLightbox: (image: string) => () => any = (image: string) => {
        return () => this.props.openLightbox(image);
    };

    getImages(): Array<React.ReactNode> | null {
        const { locale, source } = this.props;

        const images = getImageURLs(source, locale);
        return images.map((urlWithLocale, i) => {
            return (
                <img
                    src={urlWithLocale}
                    alt=''
                    key={i}
                    onClick={this.openLightbox(urlWithLocale)}
                />
            );
        });
    }

    render(): null | React.ReactNode {
        const images = this.getImages();
        if (!images) {
            return null;
        }

        return (
            <React.Fragment>
                <div className='screenshots'>{images}</div>
            </React.Fragment>
        );
    }
}
