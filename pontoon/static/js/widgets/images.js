
import React from 'react';


export class Image extends React.PureComponent {

    render () {
        if (!this.props.src) {
            return '';
        }
        return (
            <img src={this.props.src}
                 className={this.props.className}
                 width={this.props.width}
                 height={this.props.height} />);
    }
}


export class ImageLink extends React.PureComponent {

    get components () {
        const components = {image: Image};
        return Object.assign({}, components, (this.props.components || {}));
    }

    render () {
        if (!this.props.src) {
            return '';
        }
        const {image: Image} = this.components;
        return (
            <a className={this.props.className}
               href={this.props.href}>
              <Image
                 src={this.props.src}
                 width={this.props.width}
                 height={this.props.height}
                 {...this.props.imageProps} />
              {this.props.children}
            </a>);
    }
}


export class Logo extends React.PureComponent {

    get height () {
        return this.props.height || 32;
    }

    get width () {
        return this.props.width || 32;
    }

    get className () {
        return this.props.className || "logo";
    }

    render () {
        return (
            <ImageLink
               className={this.className}
               href={this.props.href}
               src={this.props.src}
               height={this.height}
               width={this.width}
               />);
    }
}


export class Avatar extends React.PureComponent {

    get avatar () {
        return this.props.src + this.size.toString();
    }

    get className () {
        return this.props.className || '';
    }

    get size () {
        return this.props.size || 88;
    }

    render () {
        if (!this.props.src) {
            return '';
        }
        return (
            <Image
               {...this.props}
               className={this.className}
               src={this.avatar} />);
    }
}


export class AvatarLink extends React.PureComponent {

    get components () {
        const components = {image: Avatar}
        return Object.assign({}, components, (this.props.components || {}))
    }

    get imageProps () {
        const imageProps = {
            className: 'rounded',
            width: this.props.width,
            height: this.props.height};
        return Object.assign({}, imageProps, (this.props.imageProps || {}));
    }

    render () {
        if (!this.props.src) {
            return '';
        }
        return (
            <ImageLink
               className="avatar"
               src={this.props.src}
               imageProps={this.imageProps}
               components={this.components}>
              {this.props.children}
            </ImageLink>);
    }
}
