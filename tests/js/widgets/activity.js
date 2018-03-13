
import React from 'react';

import {shallow} from 'enzyme';

import Datetime from 'utils/datetime';

import {LatestActivity, LatestActivityTooltip} from 'widgets/activity';
import {
    LatestActivityTooltipFooter,
    LatestActivityTooltipTranslation} from 'widgets/activity/tooltip';


test('LatestActivity render', () => {

    class MockLatestActivity extends LatestActivity {

        renderTime () {
            return 'TIME';
        }

        renderTooltip () {
            return 'TOOLTIP';
        }
    }

    const activity = shallow(<MockLatestActivity />);
    expect(activity.text()).toBe('TIMETOOLTIP');
    expect(activity.state().showTooltip).toBe(false);

    const div = activity.find('div.latest-activity-inline');
    expect(div.length).toBe(1);

    const span = div.find('span.latest-inline');
    expect(span.props()).toEqual(
        {children: ["TIME", "TOOLTIP"],
         className: "latest-inline",
         onMouseEnter: activity.instance().popTooltip,
         onMouseLeave: activity.instance().unpopTooltip});
})


test('LatestActivity renderTime', () => {
    const activity = shallow(<LatestActivity ago={23} />);

    let time = shallow(activity.instance().renderTime());
    expect(time.find('time').length).toBe(1);
    expect(time.props()).toEqual({children: 23})
});


test('LatestActivity renderTooltip', async () => {
    const activity = shallow(<LatestActivity foo={23} bar={7} />);
    expect(activity.instance().renderTooltip()).toBe('');

    await activity.setState({showTooltip: true});
    let tooltip = shallow(activity.instance().renderTooltip());
    expect(tooltip.text()).toBe("<LatestActivityTooltip />");
    expect(tooltip.find('aside.tooltip').length).toBe(1);
    const tooltipComponent = tooltip.find(LatestActivityTooltip);
    expect(tooltipComponent.props()).toEqual({bar: 7, foo: 23});
});


test('LatestActivity renderTooltip custom', async () => {

    class MockTooltip extends LatestActivityTooltip {

    }

    const activity = shallow(<LatestActivity components={{tooltip: MockTooltip}} foo={23} bar={7} />);
    await activity.setState({showTooltip: true});
    let tooltip = shallow(activity.instance().renderTooltip());
    expect(tooltip.text()).toBe("<MockTooltip />");
    expect(tooltip.find('aside.tooltip').length).toBe(1);
    const tooltipComponent = tooltip.find(MockTooltip);
    expect(tooltipComponent.props()).toEqual({bar: 7, foo: 23});
});


test('LatestActivity popAndUnpop', async () => {
    const activity = shallow(<LatestActivity foo={23} bar={7} />);

    activity.instance().popTooltip();
    expect(activity.state().showTooltip).toBe(true);

    activity.instance().unpopTooltip();
    expect(activity.state().showTooltip).toBe(false);
});

test('LatestActivityTooltipTranslation render', () => {
    const translation = shallow(<LatestActivityTooltipTranslation translation='FOO' />);
    expect(translation.text()).toBe('FOO');
    expect(translation.find('.quote').length).toBe(1);
    expect(translation.find('.translation').length).toBe(1);
});


test('LatestActivityTooltip render', () => {
    const tooltip = shallow(
        <LatestActivityTooltip
           action={7}
           date={13}
           user={17}
           translation={{string: 23}} />);
    expect(tooltip.text()).toBe(
        "<LatestActivityTooltipTranslation /><LatestActivityTooltipFooter />");
    const translation = tooltip.find(LatestActivityTooltipTranslation);
    expect(translation.props()).toEqual({translation: 23});

    const footer = tooltip.find(LatestActivityTooltipFooter);
    expect(footer.props()).toEqual({"action": 7, "date": 13, "user": 17});
});


test('LatestActivityTooltipFooter render', () => {
    const footer = shallow(
        <LatestActivityTooltipFooter date={0} />);
    footer.instance().renderAction = jest.fn(() => 7);
    footer.instance().renderDatetime = jest.fn(() => 13);
    footer.instance().renderAvatar = jest.fn(() => 23);

    // force the component to rerender
    footer.setProps({foo: 23});

    expect(footer.text()).toBe("71323");
    expect(footer.instance().datetime).toEqual(new Datetime(0));
});


test('LatestActivityTooltipFooter renderByline', () => {
    const footer = shallow(
        <LatestActivityTooltipFooter date={0} />);
    expect(footer.instance().renderByline()).toBe('');
    footer.setProps({user: {name: 'FOO'}});
    expect(footer.instance().renderByline()).toEqual(
        <span>by <span className="translation-author">FOO</span></span>);
});


test('LatestActivityTooltipFooter renderAvatar', () => {
    const footer = shallow(
        <LatestActivityTooltipFooter date={0} />);
    expect(footer.instance().renderAvatar()).toBe('');
    footer.setProps({user: {avatar: 'BAR'}});
    expect(footer.instance().renderAvatar()).toEqual(
        <img className="rounded" height="44" src="BAR" width="44" />);
});


test('LatestActivityTooltipFooter renderAction', () => {
    const footer = shallow(
        <LatestActivityTooltipFooter date={0} action="BAZ" />);
    footer.instance().renderByline = jest.fn(() => 7);
    expect(shallow(footer.instance().renderAction()).text()).toBe("BAZ7");
});


test('LatestActivityTooltipFooter renderDatetime', () => {
    const footer = shallow(
        <LatestActivityTooltipFooter date={0} />);
    expect(shallow(footer.instance().renderDatetime()).text()).toBe(
        "on January 1, 1970at 12:00:00 AM");
});
