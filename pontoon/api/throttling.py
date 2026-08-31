from rest_framework.throttling import ScopedRateThrottle, SimpleRateThrottle


class _SuffixedScopedRateThrottle(ScopedRateThrottle):
    """
    Like ScopedRateThrottle, but looks up the rate under `<throttle_scope>_<suffix>`,
    so a view can combine several rates for a single `throttle_scope`.
    """

    suffix = ""

    def allow_request(self, request, view):
        scope = getattr(view, self.scope_attr, None)
        if not scope:
            return True

        self.scope = f"{scope}_{self.suffix}"
        self.rate = self.get_rate()
        self.num_requests, self.duration = self.parse_rate(self.rate)

        return SimpleRateThrottle.allow_request(self, request, view)


class BurstRateThrottle(_SuffixedScopedRateThrottle):
    """Short-window rate, to stop too many requests in a short period.
    Rate key: `<throttle_scope>_burst`."""

    suffix = "burst"


class SustainedRateThrottle(_SuffixedScopedRateThrottle):
    """Long-window rate, to cap total volume.
    Rate key: `<throttle_scope>_sustained`."""

    suffix = "sustained"


# Throttles for endpoints that write translations from uploaded files.
# Views using these should set `throttle_scope = "upload"`
# so that they share a single quota per user.
UPLOAD_THROTTLE_CLASSES = [BurstRateThrottle, SustainedRateThrottle]
