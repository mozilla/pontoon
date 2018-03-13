
import React from 'react';

import {shallow} from 'enzyme';

import {Deadline} from 'widgets/deadline';
import Datetime from 'utils/datetime';

jest.mock('utils/datetime');


test('Deadline render', () => {

    let deadline = shallow(<Deadline />);
    expect(deadline.text()).toBe("No deadline set");

    deadline = shallow(<Deadline deadline={0} />);
    expect(deadline.text()).toBe("No deadline set");

    Datetime.mockImplementation(() => ({date: 'DATETIME'}))

    deadline = shallow(<Deadline deadline={23} />);
    expect(deadline.text()).toBe("DATETIME");

    expect(Datetime.mock.calls).toEqual([[23]])
    let time = deadline.find('time');
    expect(time.length).toBe(1)
    expect(time.props().className).toBe('overdue');
    expect(time.props().dateTime).toBe(23);

    const future = new Date();
    future.setDate(future.getDate() + 1);
    deadline = shallow(<Deadline deadline={future} />);
    time = deadline.find('time');
    expect(time.props().dateTime).toBe(future);
    expect(time.props().className).toBe('');
});
