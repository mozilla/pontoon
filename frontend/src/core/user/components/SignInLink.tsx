import * as React from 'react';

type Props = {
    children?: React.ReactNode;
    url: string;
};

/*
 * Render a link to the Sign In process.
 */
export default class SignInLink extends React.Component<Props> {
    generateSignInURL(): string {
        const absoluteUrl = window.location.origin + this.props.url;
        const parsedUrl = new URL(absoluteUrl);
        const next = window.location.pathname + window.location.search;

        parsedUrl.searchParams.set('next', next);

        return parsedUrl.toString();
    }

    render(): React.ReactElement<'a'> {
        return <a href={this.generateSignInURL()}>{this.props.children}</a>;
    }
}
