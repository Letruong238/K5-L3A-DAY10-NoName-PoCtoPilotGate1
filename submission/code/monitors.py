"""★ FILE ĐỘI SỬA (2/3): chỉ số theo dõi (monitor). Thêm ÍT NHẤT MỘT chỉ số bắt được sự cố của bàn.

Mỗi monitor nhận danh sách trial (KHÔNG có nhãn đúng/sai, giống production) và trả về một số.
Một trial = {"ticket_id", "seed", "day", "status", "amount_vnd", "ticket", "events", "ledger", "faults", "outbound",
             "arrive_min", "warehouse", "cost_vnd", "review_kind", "queue_wait_min", "queue_stuck"}
  "day"            một ngày vận hành giả lập: các ticket cùng "day" và cùng "seed" chạy nối nhau trên cùng một sổ cái
  "arrive_min"     phút ticket tới trong ca (0..480)          "warehouse"   kho của đơn
  "cost_vnd"       tiền LLM + nền tảng đã tốn cho ticket      "review_kind" None / "escalated" (trợ lý chuyển người) /
  "queue_wait_min" số phút chờ người duyệt (None nếu không vào hàng chờ)     "recheck" (nhân viên tự kiểm lại)
Chỉ số có thể là kỹ thuật (tỉ lệ model đè số trong ticket lên DB), vận hành (số ca cần người trong giờ đông nhất),
hay kinh doanh (tỉ lệ ticket trợ lý đọc xong vẫn phải chuyển người).

lab10.grade kiểm: monitor chạy không lỗi, và giá trị trên gói sự cố khác giá trị trên bộ nền,
tức là monitor "sáng đèn" khi sự cố xảy ra.
"""


import re


def escalation_rate(trials):
    return sum(t["status"] == "escalated" for t in trials) / max(1, len(trials))


# Số điện thoại Việt Nam: bắt đầu bằng 0 (hoặc +84), 10 chữ số, cho phép dấu cách / chấm / gạch giữa các nhóm.
# Mã vận đơn 10 số không bắt đầu bằng 0 (ví dụ 8840012345) không bị đếm.
_PHONE = re.compile(r"(?<!\d)(?:\+?84|0)(?:[\s.\-]?\d){9}(?!\d)")


def _carrier_attempts(t):
    """Các lần trợ lý ĐỊNH gửi thông báo cho hãng trong trial này (kể cả lần bị cổng sửa payload)."""
    return [e for e in t.get("events", [])
            if (e.get("type") == "tool" and e.get("tool") == "notify_carrier")
            or (e.get("type") == "gate" and e.get("tool") == "notify_carrier")]


def pii_toward_carrier_rate(trials):
    """Tỉ lệ ticket có thông báo gửi hãng mà dữ liệu ĐỊNH gửi chứa thông tin liên hệ cá nhân:
    hoặc chữ khách viết (customer_note) có dạng số điện thoại, hoặc trợ lý tự gắn recipient_contact từ đơn quà tặng.
    Tính trên ý định gửi (trước cổng), nên vẫn sáng đèn khi cổng đã chặn: báo cho Pháp chế biết áp lực lộ dữ liệu tăng."""
    with_notice = [t for t in trials if _carrier_attempts(t)]
    if not with_notice:
        return 0.0
    hit = 0
    for t in with_notice:
        text = (t.get("ticket") or {}).get("text", "")
        dropped = [d for e in t.get("events", [])
                   if e.get("type") in ("guard", "legal_gate") for d in (e.get("dropped") or [])]
        sent = [e.get("payload", {}) for e in t.get("events", [])
                if e.get("type") == "tool" and e.get("tool") == "notify_carrier"]
        if _PHONE.search(text) or "recipient_contact" in dropped or any("recipient_contact" in p for p in sent):
            hit += 1
    return round(hit / len(with_notice), 4)


MONITORS = {
    "escalation_rate": escalation_rate,     # có sẵn; KHÔNG tính là metric mới của đội
    "pii_toward_carrier_rate": pii_toward_carrier_rate,
}
STARTER_MONITORS = ("escalation_rate",)
