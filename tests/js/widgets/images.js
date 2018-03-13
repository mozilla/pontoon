
import React from 'react';

import {shallow} from 'enzyme';

import {Avatar, AvatarLink, Image, ImageLink, Logo} from 'widgets/images';


test('Image render', () => {
    let image = shallow(<Image />);
    expect(image.text()).toBe('');
    let img = image.find('img');
    expect(img.length).toBe(0);

    image = shallow(
        <Image
           width={23}
           height={43}
           className='foo'
           src="/some/image.svg" />);
    expect(image.text()).toBe('');
    img = image.find('img');
    expect(img.length).toBe(1);
    expect(img.props().src).toBe('/some/image.svg');
    expect(img.props().height).toBe(43);
    expect(img.props().width).toBe(23);
    expect(img.props().className).toBe('foo');
});


test('ImageLink render', () => {
    let imagelink = shallow(<ImageLink />);
    expect(imagelink.text()).toBe('');

    // no src - nothing is rendered
    expect(imagelink.find('a').length).toBe(0);

    // set the src
    imagelink = shallow(<ImageLink src="/some/image.svg" />);

    // anchor tag is there but nothing set
    let anchor = imagelink.find('a');
    expect(anchor.length).toBe(1);
    expect(anchor.props().className).toBe(undefined);
    expect(anchor.props().href).toBe(undefined);

    let image = anchor.find(Image);
    expect(image.length).toBe(1);
    expect(image.props().src).toBe("/some/image.svg");

    imagelink = shallow(
        <ImageLink
           src="/some/image.svg"
           href="/nowhere"
           className="some-special-image"
           width={23}
           height={43}
           />);

    anchor = imagelink.find('a');
    expect(anchor.length).toBe(1);
    expect(anchor.props().className).toBe('some-special-image');
    expect(anchor.props().href).toBe('/nowhere');

    image = anchor.find(Image);
    expect(image.length).toBe(1);
    expect(image.props().src).toBe("/some/image.svg");
    expect(image.props().width).toBe(23);
    expect(image.props().height).toBe(43);
});


test('Logo render', () => {
    let logo = shallow(<Logo />);
    expect(logo.text()).toBe('<ImageLink />');
    let image = logo.find(ImageLink);
    expect(image.props().className).toBe('logo');
    expect(image.props().src).toBe(undefined);
    expect(image.props().href).toBe(undefined);
    expect(image.props().height).toBe(32);
    expect(image.props().width).toBe(32);

    logo = shallow(
        <Logo
           className="special-logo"
           src="/some/image.svg"
           href="/nowhere"
           height={17}
           width={113}
           />);
    image = logo.find(ImageLink);
    expect(image.props().className).toBe('special-logo');
    expect(image.props().src).toBe('/some/image.svg');
    expect(image.props().href).toBe('/nowhere');
    expect(image.props().height).toBe(17);
    expect(image.props().width).toBe(113);
});


test('Avatar render', () => {
    let avatar = shallow(<Avatar />);
    expect(avatar.text()).toBe('');
    let image = avatar.find('Image');
    expect(image.length).toBe(0);

    avatar = shallow(<Avatar src="/some/avatatar.png?s=" />);
    expect(avatar.text()).toBe('<Image />');
    image = avatar.find('Image');
    expect(image.length).toBe(1);
    expect(image.props().src).toBe("/some/avatatar.png?s=88");

    avatar = shallow(
        <Avatar
           foo={23}
           bar={43}
           size={13}
           className="another"
           src="/another/avatatar.png?s=" />);
    expect(avatar.text()).toBe('<Image />');
    image = avatar.find('Image');
    expect(image.length).toBe(1);
    expect(image.props().src).toBe("/another/avatatar.png?s=13");
    expect(image.props().className).toBe("another");
    expect(image.props().foo).toBe(23);
    expect(image.props().bar).toBe(43);
});


test('AvatarLink render', () => {
    let avatarlink = shallow(<AvatarLink />);
    expect(avatarlink.text()).toBe('');

    avatarlink = shallow(<AvatarLink src="/some/avatar.png" />);
    expect(avatarlink.text()).toBe('<ImageLink />');
    let imagelink = avatarlink.find(ImageLink);
    expect(imagelink.props()).toEqual(
        {children: undefined,
         className: "avatar",
         components: {image: Avatar},
         imageProps: {
             className: "rounded",
             height: undefined,
             width: undefined},
         src: "/some/avatar.png"});


    avatarlink = shallow(
        <AvatarLink
           components={{image: 7, foo: 23}}
           imageProps={{baz: 17, className: 'other'}}
           src="/some/avatar.png">
          AVATARTEXT
        </AvatarLink>);
    expect(avatarlink.text()).toBe('<ImageLink />');
    imagelink = avatarlink.find(ImageLink);
    expect(imagelink.props()).toEqual(
        {children: "AVATARTEXT",
         className: "avatar",
         components: {image: 7, foo: 23},
         imageProps: {
             baz: 17,
             className: "other",
             height: undefined,
             width: undefined},
         src: "/some/avatar.png"});
});
