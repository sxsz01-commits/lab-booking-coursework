"""Booking rules, independent from HTTP and storage."""

from datetime import datetime, time, timedelta


class ValidationError(ValueError):
    pass


class ConflictError(ValueError):
    pass


def validate_booking(data: dict, capacity: int) -> dict:
    """Validate and normalize a proposed local-time booking."""
    if not isinstance(data, dict):
        raise ValidationError("请求必须是 JSON 对象")
    name = str(data.get("requester", "")).strip()
    purpose = str(data.get("purpose", "")).strip()
    if not (1 <= len(name) <= 40):
        raise ValidationError("预约人长度须为 1 至 40 个字符")
    if not (1 <= len(purpose) <= 120):
        raise ValidationError("用途长度须为 1 至 120 个字符")
    try:
        participants = int(data.get("participants"))
    except (TypeError, ValueError) as exc:
        raise ValidationError("人数必须为整数") from exc
    if isinstance(data.get("participants"), bool) or participants < 1 or participants > capacity:
        raise ValidationError(f"人数须在 1 至 {capacity} 之间")
    try:
        start = datetime.fromisoformat(str(data.get("start", "")))
        end = datetime.fromisoformat(str(data.get("end", "")))
    except ValueError as exc:
        raise ValidationError("时间须为 YYYY-MM-DDTHH:MM 格式") from exc
    if start.tzinfo or end.tzinfo:
        raise ValidationError("请使用本地时间，不要附加时区")
    if start.date() != end.date() or end <= start or end - start > timedelta(hours=4):
        raise ValidationError("预约须在同一天，时长大于 0 且不超过 4 小时")
    if start.time() < time(8) or end.time() > time(22):
        raise ValidationError("预约时间须在 08:00 至 22:00 之间")
    return {
        "requester": name,
        "purpose": purpose,
        "participants": participants,
        "start": start.isoformat(timespec="minutes"),
        "end": end.isoformat(timespec="minutes"),
    }

