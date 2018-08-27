/* @flow */

import * as React from 'react';
import LinkifyIt from 'linkify-it';
import tlds from 'tlds';

import './Screenshots.css';

import { Lightbox } from 'core/lightbox';


// Create and configure a URLs matcher.
const linkify = new LinkifyIt();
linkify.tlds(tlds);


type Props = {|
    locale: string,
    source: string,
|};

type State = {|
    lightboxOpen: boolean,
    lightboxImage: string,
|};


/**
 * Shows screenshot miniatures based on the content of a string.
 *
 * This component looks at all URLs to an image (either .png or .jpg) in a
 * source string and then shows a miniature of those images.
 */
export default class Screenshots extends React.Component<Props, State> {
    constructor(props: Props): void {
        super(props);
        this.state = {
            lightboxOpen: false,
            lightboxImage: '',
        };
    }

    openLightbox(image: string): Function {
        return (): void => {
            this.setState({
                lightboxOpen: true,
                lightboxImage: image,
            });
        }
    }

    closeLightbox = (): void => {
        this.setState({ lightboxOpen: false });
    }

    getImages(): ?Array<React.Node> {
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
                const urlWithLocale = match.url.replace(/en-US\//gi, locale + '/');
                images.push(<img
                    src={ urlWithLocale }
                    alt=""
                    key={ i }
                    onClick={ this.openLightbox(urlWithLocale) }
                />);
            }
        });

        return images;
    }

    render(): React.Node {
        const images = this.getImages();
        if (!images) {
            return null;
        }

        return <React.Fragment>
            <div className="screenshots">
                { images }
            </div>
            { this.state.lightboxOpen && <Lightbox
                image={ this.state.lightboxImage }
                close={ this.closeLightbox }
            /> }
        </React.Fragment>
    }
}
