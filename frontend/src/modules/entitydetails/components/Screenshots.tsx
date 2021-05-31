import * as React from 'react';
import LinkifyIt from 'linkify-it';
import tlds from 'tlds';

import './Screenshots.css';

// Create and configure a URLs matcher.
const linkify = new LinkifyIt();
linkify.tlds(tlds);

type Props = {
    locale: string;
    source: string;
    openLightbox: (...args: Array<any>) => any;
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

        if (source === '') {
            return null;
        }

        const matches = linkify.match(source);
        if (!matches) {
            return null;
        }

        const images = [];
        matches.forEach((match, i) => {
            if (/(https?:\/\/.*\.(?:png|jpg))/im.test(match.url)) {
                const urlWithLocale = match.url.replace(
                    /en-US\//gi,
                    locale + '/',
                );
                images.push(
                    <img
                        src={urlWithLocale}
                        alt=''
                        key={i}
                        onClick={this.openLightbox(urlWithLocale)}
                    />,
                );
            }
        });

        return images;
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
