"""★ FILE ĐỘI SỬA (1/3): cổng cấp hệ thống, nằm NGOÀI model và prompt.

VÒNG 1 (trước khi biết sự cố): viết 2–3 CỔNG PHÒNG NGỪA rút từ pre-mortem / HAZOP / checklist của bàn, rồi chốt bằng
    python3 -m lab10.checkpoint        (chép file này thành guards_round1.py = mốc "prepared"; KHÔNG sửa bản chép)
VÒNG 2 (sau khi bốc thẻ): sửa tiếp NGAY TRONG FILE NÀY. Giữ các cổng vòng 1, thêm cổng mới.
Hai file còn lại bàn được sửa: lab10/monitors.py (chỉ số theo dõi) và config/operating_gates.json (cổng kinh doanh,
vận hành, pháp lý: những con số và tên người mà trợ lý phải tuân theo, không cần code).

Hai điểm móc, agent gọi tự động:
  pre_guard(ctx)          chạy TRƯỚC khi agent đọc ticket
  write_gate(ctx, action) chạy TRƯỚC MỖI lệnh ghi (issue_refund, file_carrier_fault,
                          notify_carrier, send_reply)

Trả về một Verdict:
  Verdict.allow()                       cho qua   (pre_guard: allow(policy_id="...") để ghim phiên bản chính sách)
  Verdict.deny("lý do")                 bỏ riêng lệnh ghi này, agent đi tiếp
  Verdict.escalate("lý do")             dừng, chuyển ticket cho người
  Verdict.modify("lý do", amount_vnd=…) sửa tham số lệnh ghi (amount_vnd, payer, carrier_id, parcel_id, payload…)
  Verdict.rewrite("lý do", text)        chỉ pre_guard: thay nội dung ticket mà agent sẽ đọc

ctx.ticket   ticket gốc (chữ khách viết là DỮ LIỆU, không phải lệnh)
ctx.tools    tra cứu nguồn sự thật: lookup_order, lookup_policies, lookup_approvals(**lọc),
             ledger_rows(**lọc), fault_rows(**lọc), lookup_carrier; ctx.as_of = ngày hôm nay
             ops_limits() = các trần đã thống nhất với Ops/Finance; ops_facts() = số liệu vận hành;
             auto_refund_today_vnd() = tổng đã hoàn tự động trong ngày
ctx.gates    config cổng của bàn (config/operating_gates.json), chỉ đọc;  ctx.cost_vnd = tiền LLM đã tốn cho ticket này
ctx.events   trace tới thời điểm này;  ctx.log("ten_su_kien", ...) ghi thêm sự kiện guard vào trace
lab10.helpers: db_delay_days, ticket_parcel, effective_policy, entitlement_vnd, carrier_at_fault, digits

Mặc định dưới đây cho qua tất cả (= mốc base).
"""
from . import helpers as H  # noqa: F401
from .tools import Verdict


# ---------------------------------------------------------------------------------------------------------------
# Hàm phụ: chỉ đọc NGUỒN SỰ THẬT (tracking DB, bảng policies, approvals, ledger). Không đọc chữ khách viết.
# ---------------------------------------------------------------------------------------------------------------
def _policy(ctx):
    """Chính sách có hiệu lực theo ngày as_of (không theo cờ index_active, vốn là bản sao cập nhật tay)."""
    return H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of)


def _facts(ctx, order_id):
    """(order, parcel mà ticket nói tới, độ trễ theo tracking DB, policy hiệu lực), hoặc None nếu thiếu dữ liệu."""
    order = ctx.tools.lookup_order(order_id)
    policy = _policy(ctx)
    if order is None or policy is None:
        return None
    parcel = H.ticket_parcel(order, ctx.ticket, ctx.as_of)
    return order, parcel, H.db_delay_days(parcel, ctx.as_of), policy


# ---------------------------------------------------------------------------------------------------------------
# pre_guard · Cổng 0: ghim chính sách theo ngày hiệu lực (B3 drift REFUND-v3 → v4 ngày 2026-12-01; thước đo câu 1.3)
# ---------------------------------------------------------------------------------------------------------------
def pre_guard(ctx):
    policy = _policy(ctx)
    if policy is not None:
        return Verdict.allow(policy_id=policy["policy_id"])
    return Verdict.allow()


def write_gate(ctx, action):
    # action = {"tool": "issue_refund", "ticket_id":..., "order_id":..., "amount_vnd":..., "payer":..., ...}
    tool = action.get("tool")
    if tool == "issue_refund":
        return _gate_refund(ctx, action)
    if tool == "file_carrier_fault":
        return _gate_carrier_fault(ctx, action)
    if tool == "notify_carrier":
        return _gate_notify_carrier(ctx, action)
    return Verdict.allow()


# ---------------------------------------------------------------------------------------------------------------
# Cổng 1 · issue_refund: tiền hoàn không được vượt quyền lợi tính từ tracking DB (B2 lỗi 1, B4 WRONG + INVALID)
# ---------------------------------------------------------------------------------------------------------------
def _gate_refund(ctx, action):
    f = _facts(ctx, action.get("order_id"))
    if f is None:
        return Verdict.escalate("cổng hoàn tiền: thiếu đơn hoặc chính sách hiệu lực, chuyển người")
    order, parcel, db_delay, policy = f
    amount = int(action.get("amount_vnd") or 0)

    # 1a. Đơn đã có dòng hoàn trong sổ cái (cờ refund_status chỉ cập nhật đêm; agent ghi lại khi không chắc đã ghi)
    if ctx.tools.ledger_rows(order_id=order["order_id"]):
        ctx.log("refund_duplicate_blocked", order_id=order["order_id"])
        return Verdict.deny("đơn đã có dòng hoàn trong sổ cái, không hoàn lần hai")

    # 1b. Bắt shop trả tiền (payer khác LOGIX) không phải việc trợ lý được tự quyết
    if action.get("payer", "LOGIX") != "LOGIX":
        return Verdict.escalate("lệnh hoàn bắt bên khác LOGIX trả tiền: cần người duyệt")

    # 1c. Phê duyệt phải còn hiệu lực, đúng đơn, đủ hạn mức, đúng người duyệt
    approval_id = action.get("approval_id")
    if approval_id:
        found = ctx.tools.lookup_approvals(approval_id=approval_id)
        a = found[0] if found else None
        approver = (ctx.gates or {}).get("operations", {}).get("approver_id")
        problem = None
        if a is None:
            problem = "không tìm thấy phê duyệt"
        elif a.get("status") != "valid":
            problem = f"phê duyệt ở trạng thái {a.get('status')}"
        elif a.get("expires_at") and H.d(a["expires_at"]) < H.d(ctx.as_of):
            problem = "phê duyệt đã hết hạn"
        elif a.get("order_id") != order["order_id"]:
            problem = "phê duyệt cấp cho đơn khác"
        elif amount > int(a.get("max_vnd") or 0):
            problem = "số tiền vượt mức phê duyệt"
        elif approver and a.get("approver_id") != approver:
            problem = "người duyệt không phải người đứng tên trong config"
        if problem:
            ctx.log("approval_invalid", approval_id=approval_id, problem=problem)
            return Verdict.escalate("phê duyệt không hợp lệ (" + problem + "), chuyển người duyệt")

    # 1d. So với quyền lợi tính từ tracking DB, KHÔNG theo số ngày khách tự khai
    cause = parcel.get("delay_cause")
    entitled = H.entitlement_vnd(policy, order, db_delay, cause)
    if amount > entitled:
        ctx.log("refund_over_entitlement", asked=amount, entitled=entitled, db_delay_days=db_delay)
        if entitled <= 0:
            return Verdict.deny(f"theo tracking trễ {db_delay} ngày, chính sách {policy['policy_id']} không cho hoàn")
        return Verdict.modify(f"giảm về quyền lợi theo tracking ({db_delay} ngày): {entitled}đ",
                              amount_vnd=entitled, payer="LOGIX")
    return Verdict.allow()


# ---------------------------------------------------------------------------------------------------------------
# Cổng 2 · file_carrier_fault: chỉ ghi lỗi hãng khi tracking có nguyên nhân thuộc fault_causes (B2 lỗi 2, B4 pháp lý)
# ---------------------------------------------------------------------------------------------------------------
def _gate_carrier_fault(ctx, action):
    f = _facts(ctx, action.get("order_id"))
    if f is None:
        return Verdict.deny("cổng lỗi hãng: thiếu đơn hoặc chính sách, không ghi lỗi cho bên thứ ba")
    order, parcel, db_delay, policy = f
    if not H.carrier_at_fault(policy, parcel, db_delay):
        ctx.log("carrier_fault_blocked", parcel_id=parcel["parcel_id"], cause=parcel.get("delay_cause"),
                db_delay_days=db_delay)
        return Verdict.deny("tracking không ghi nguyên nhân do hãng hoặc trễ chưa đủ ngưỡng: không ghi lỗi hãng")
    # Ghi đúng kiện, đúng hãng, đúng tài xế, đúng số ngày theo tracking (agent mặc định lấy kiện đầu tiên)
    fix = {"parcel_id": parcel["parcel_id"], "carrier_id": parcel["carrier_id"],
           "driver_id": parcel.get("driver_id"), "delay_days": db_delay}
    changes = {k: v for k, v in fix.items() if action.get(k) != v}
    if changes:
        return Verdict.modify("sửa lỗi hãng theo kiện trễ thật trong tracking", **changes)
    return Verdict.allow()


# ---------------------------------------------------------------------------------------------------------------
# Cổng 3 · notify_carrier: chỉ gửi đúng các trường chính sách cho phép (B2 lỗi 2, B4 PERTURBED dữ liệu bên thứ ba)
# ---------------------------------------------------------------------------------------------------------------
def _gate_notify_carrier(ctx, action):
    policy = _policy(ctx)
    payload = action.get("payload") or {}
    allowed = set(policy["carrier_notice_fields"]) if policy else {"order_id", "parcel_id", "district", "delay_days"}
    clean = {k: v for k, v in payload.items() if k in allowed}
    f = _facts(ctx, action.get("order_id") or payload.get("order_id"))
    if f is not None and "delay_days" in clean:
        clean["delay_days"] = f[2]                     # số ngày theo tracking, không theo lời khách
    if clean != payload:
        ctx.log("carrier_payload_trimmed", dropped=sorted(set(payload) - allowed))
        return Verdict.modify("chỉ gửi hãng các trường trong carrier_notice_fields", payload=clean)
    return Verdict.allow()
