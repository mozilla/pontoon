import { Localized } from '@fluent/react';
import React, { useEffect, useState } from 'react';
import { USER } from '~/modules/user';
import { dismissAddonPromotion_ } from '~/modules/user/actions';
import { useAppDispatch, useAppSelector } from '~/hooks';
import './AddonPromotion.css';

interface PontoonAddonInfo {
  installed?: boolean;
}

interface WindowWithInfo extends Window {
  PontoonAddon?: PontoonAddonInfo;
}

/**
 * Renders Pontoon Add-On promotion banner.
 */
export function AddonPromotion(): React.ReactElement<'div'> | null {
  const dispatch = useAppDispatch();
  const { hasDismissedAddonPromotion, isAuthenticated } = useAppSelector(
    (state) => state[USER],
  );
  const [installed, setInstalled] = useState(false);

  // Hide Add-On Promotion if Add-On installed while active
  useEffect(() => {
    const handleMessages = ({ data, origin, source }: MessageEvent) => {
      // only allow messages from authorized senders (extension content script, or Pontoon itself)
      if (origin === window.origin && source === window) {
        if (typeof data === 'string') {
          // backward compatibility
          // TODO: remove some reasonable time after https://github.com/MikkCZ/pontoon-addon/pull/155 is released
          try {
            data = JSON.parse(data);
          } catch {
            return;
          }
        }

        if (data?._type === 'PontoonAddonInfo' && data.value?.installed) {
          setInstalled(true);
        }
      }
    };

    window.addEventListener('message', handleMessages);
    return () => {
      window.removeEventListener('message', handleMessages);
    };
  });

  const isFirefox = navigator.userAgent.indexOf('Firefox') !== -1;
  const isChrome = navigator.userAgent.indexOf('Chrome') !== -1;
  const downloadHref = isFirefox
    ? 'https://addons.mozilla.org/firefox/addon/pontoon-tools/'
    : isChrome
    ? 'https://chrome.google.com/webstore/detail/pontoon-add-on/gnbfbnpjncpghhjmmhklfhcglbopagbb'
    : '';

  // User not authenticated or promotion dismissed or add-on installed or
  // page not loaded in Firefox or Chrome (add-on not available for other browsers)
  if (
    !isAuthenticated ||
    hasDismissedAddonPromotion ||
    installed ||
    (window as WindowWithInfo).PontoonAddon?.installed === true ||
    !downloadHref
  ) {
    return null;
  }

  return (
    <div className='addon-promotion'>
      <div className='container'>
        <Localized
          id='addonpromotion-AddonPromotion--dismiss'
          attrs={{ ariaLabel: true }}
        >
          <button
            className='dismiss'
            aria-label='Dismiss'
            onClick={() => dispatch(dismissAddonPromotion_())}
          >
            ×
          </button>
        </Localized>

        <Localized id='addonpromotion-AddonPromotion--text'>
          <p className='text'>
            Take your Pontoon notifications everywhere with the official Pontoon
            Add-on.
          </p>
        </Localized>

        <Localized id='addonpromotion-AddonPromotion--get'>
          <a className='get' href={downloadHref}>
            Get Pontoon Add-On
          </a>
        </Localized>
      </div>
    </div>
  );
}
