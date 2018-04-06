
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
    components = {image: Image};

    render () {
        if (!this.props.src) {
            return '';
        }
        const {image: Image = this.components.image} = (this.props.components || {});
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
    className = "logo";
    height = 32;
    width = 32;

    render () {
        return (
            <ImageLink
               className={this.props.className || this.className}
               href={this.props.href}
               src={this.props.src}
               height={this.props.height || this.height}
               width={this.props.width || this.width}
               />);
    }
}


export class Avatar extends React.PureComponent {
    size = 88;

    get avatar () {
        return this.props.src + (this.props.size || this.size).toString();
    }

    render () {
        if (!this.props.src) {
            return '';
        }
        return (
            <Image
               {...this.props}
               className={this.props.className || ''}
               src={this.avatar} />);
    }
}


export class AvatarLink extends React.PureComponent {
    components = {image: Avatar};

    get imageProps () {
        const imageProps = {
            className: 'rounded',
            size: this.props.size,
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
               components={Object.assign({}, this.components, (this.props.components || {}))}>
              {this.props.children}
            </ImageLink>);
    }
}
