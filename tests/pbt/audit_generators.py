"""Hypothesis strategies for U5 audit/activity events (PBT-07)."""

from __future__ import annotations

from hypothesis import strategies as st

from mini_aip.domain.audit import ActivityEvent, AuditEvent

ids = st.from_regex(r"[a-z0-9-]{1,20}", fullmatch=True)
_text = st.text(max_size=20)
_opt_text = st.one_of(st.none(), _text)


@st.composite
def audit_events(draw: st.DrawFn) -> AuditEvent:
    return AuditEvent(
        id=draw(ids),
        timestamp=draw(st.datetimes()).isoformat(),
        operation=draw(_text),
        actor=draw(_opt_text),
        roles=tuple(draw(st.lists(_text, max_size=3))),
        object_type=draw(_opt_text),
        object_id=draw(_opt_text),
        decision=draw(st.sampled_from(["allowed", "denied"])),
        outcome=draw(st.sampled_from(["ok", "error"])),
        reason=draw(_text),
    )


@st.composite
def activity_events(draw: st.DrawFn) -> ActivityEvent:
    return ActivityEvent(
        id=draw(ids),
        timestamp=draw(st.datetimes()).isoformat(),
        actor=draw(_text),
        action=draw(_text),
        object_type=draw(_opt_text),
        object_id=draw(_opt_text),
        visibility=draw(st.sampled_from(["shared", "private"])),
    )
