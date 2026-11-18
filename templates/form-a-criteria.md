# Phiếu A · Tiêu chí và cách đo · Khối 1 (phút 15–65)

**Bàn:** ______ · **Người cầm bút chính:** vai Sản phẩm và kinh doanh (câu 1.3: Kỹ sư cổng; câu 1.2, 1.4: Vận hành và pháp lý)

Điền phiếu này **trước khi chạy trợ lý lần nào**. Viết xong thì chép ngưỡng sang `config/acceptance_criteria.json`, ký ở phút 60–65,
rồi mới chạy đánh giá. Khối 1 không sửa code.

**Mục lục**
- [A1 · Mục tiêu (câu 1.1, 1.2) · phút 15–20](#a1)
- [A2 · Thước đo → Dữ liệu → Cách tính (câu 1.3, 1.4) · phút 20–35](#a2)
- [A3 · Đọc một kết quả có khoảng tin cậy (câu 1.5) · phút 35–40](#a3)
- [A4 · Câu tiêu chí thành công và ranh giới đầu ra (câu 1.6) · phút 40–60](#a4)
- [A5 · Ký và đẩy tiêu chí · phút 60–65](#a5)

---

<a id="a1"></a>

## A1 · Mục tiêu (phút 15–20)

### Câu 1.1 · Một mục tiêu cấp hệ thống (khác "model trả lời đúng")

> Với mọi ticket hoàn tiền giao trễ trong phạm vi pilot, **cả luồng** đọc ticket → tra đơn và tracking → áp chính sách → ghi sổ cái → ghi lỗi hãng → trả lời khách phải để lại **kết quả đúng ở thế giới bên ngoài**: tiền hoàn trên sổ cái đúng chính sách đang hiệu lực (`REFUND-v3`) và khớp với số tiền nói trong câu trả lời cho khách; lỗi chỉ được ghi cho hãng khi có nguyên nhân `CARRIER` đã ghi nhận; và mọi ca vượt trần đã thống nhất với Ops và Finance (`ops_limits`: quá 300.000đ/khách/ngày, quá ngân sách hoàn tự động 2.000.000đ/ngày, từ lỗi thứ 3 của cùng một hãng trong ngày) đều được chuyển cho người duyệt, **không có ca nào lách qua phê duyệt**.
>
> Dựa vào PRD v1.1 §3: mục tiêu này gom các chỉ số chặn release `approval_bypass = 0`, `refund_amount_correct`, `reply_matches_ledger` thành một kết quả của cả hệ thống, không chỉ của model. Model có thể "trả lời đúng" mà hệ thống vẫn gây hại, ví dụ hoàn đúng số tiền nhưng ghi oan lỗi cho một hãng nhỏ như GHSH (bị treo sau 3 lỗi trong 7 ngày), hoặc hoàn tự động vượt ngân sách ngày của Finance.

### Câu 1.2 · Mục tiêu nhìn từ hai người

- Chị Oanh, kế toán đối soát (không dùng trợ lý, nhưng phải khớp sổ với hãng và shop mỗi tuần): Mọi bút toán hoàn tiền trên sổ cái (`ledger`) và phiếu phạt hãng (`carrier_fault`) do trợ lý ghi phải **khớp 100% với chứng từ gốc** (độ trễ thực tế trong tracking DB, đúng chính sách đang hiệu lực `REFUND-v3`, không hoàn trùng đơn đã có trong sổ cái, tổng hoàn tự động trong ngày không vượt ngân sách `2.000.000đ`), có căn cứ rõ ràng (`basis = policy` hoặc `approval_id` hợp lệ), và **không ghi lỗi oan cho hãng vận chuyển** (chỉ ghi khi `delay_cause = CARRIER`) để cuối tuần đối soát công nợ với các hãng (`GHSH`, `VNX`, `MKD`, `DNB`) và shop khớp ngay, không phát sinh tranh chấp phạt oan (80.000đ–150.000đ/lỗi) hay phải làm bút toán điều chỉnh thủ công.
- Chị Hạnh, trưởng ca CSKH (phải duyệt những ca trợ lý chuyển sang): Trợ lý chỉ chuyển sang hàng chờ người duyệt (`escalate`) **đúng các ca vượt ngưỡng an toàn** (khoản hoàn vượt hạn mức tự động `200.000đ`/đơn của `REFUND-v3`, vượt trần `300.000đ`/khách/ngày, từ lỗi thứ 3 của cùng một hãng trong ngày, hoặc dữ kiện ticket mâu thuẫn với hệ thống) với lưu lượng nằm trong công suất trực (`6 ca/người/giờ`, không để ticket chờ quá SLA `60 phút`); đồng thời mỗi quyết định tự động phải kèm **ghi chú giải thích (`decision_note = true`)** và kiểm tra chặt `approval_id` (đúng người duyệt đứng tên `NV-HANH`, `status = valid`, còn hạn `expires_at`, khớp `ticket_id`/`order_id`) để đội CSKH tin tưởng chuyển sang kiểm mẫu (`>= 10%`, chỉ tốn `0,4 ca`/lần kiểm) thay vì phải tự đọc và kiểm lại bằng tay toàn bộ.

---

<a id="a2"></a>

## A2 · Thước đo → Dữ liệu → Cách tính (phút 20–35)

**Khung tư duy.** Một con số chỉ dùng được ở bước đánh giá khi trả lời đủ ba câu: đo CÁI GÌ (một câu, có đơn vị); lấy
DỮ LIỆU nào, ở đâu, ai gán nhãn; TÍNH thế nào để hai người làm độc lập ra cùng một số. Thiếu ô thứ ba thì chưa phải thước đo.

**Câu hỏi dẫn dắt**
- Thước đo này nói về MỘT bước của agent hay cả luồng? Nếu cả luồng hỏng, nó có chỉ ra bước nào hỏng không?
- Dữ liệu đã có sẵn (trace, sổ cái) hay phải thu thêm? Nhãn đúng/sai đến từ đâu?
- Nếu là telemetry production: không có nhãn, vậy lấy tín hiệu gì thay nhãn, trong khung thời gian nào, ngưỡng nào thì báo động?

### Câu 1.3 · Offline metric cho MỘT bước · Câu 1.4 · Telemetry production

Câu 1.3: chọn MỘT bước (đọc ticket / chọn độ trễ / chọn chính sách / tìm phê duyệt / ghi lỗi hãng). Câu 1.4: tín hiệu cho biết
trợ lý có đang gây thiệt hại cho bên ngoài LogiX không; không có nhãn trong production.

| | Offline, cho MỘT bước (câu 1.3) | Telemetry production (câu 1.4) |
|---|---|---|
| **Bước / hành vi được đo** | Bước "chọn chính sách": agent chọn phiên bản chính sách hoàn tiền (REFUND-v2/v3/v4…) để tính tiền | |
| **Thước đo** (một câu, có đơn vị) | Tỉ lệ (%) lần chạy mà `policy_id` agent dùng khác phiên bản chính sách có hiệu lực vào ngày `as_of` | |
| **Dữ liệu** (lấy ở đâu, bao nhiêu, ai gán nhãn) | Sự kiện `policy.policy_id` trong `runs/<mã lần chạy>/traces/`, bộ nền 22 ticket × 5 seed = 110 lần chạy. Nhãn tự động, không cần người gán: đáp án đúng là `helpers.effective_policy(policies, as_of)` đọc từ bảng `policies` trong `data/world.json` (nguồn sự thật, theo `effective_from`/`effective_to`, không theo cờ `index_active`) | |
| **Cách tính** (công thức, mẫu số, cách xử lý ca thiếu dữ liệu) | Số lần chạy có `policy_id ≠ effective_policy(...).policy_id` ÷ số lần chạy có sự kiện `policy`. Lần chạy dừng trước bước này (bị chặn ở `pre_guard`, chuyển người duyệt sớm, lỗi LLM) bị loại khỏi mẫu số và đếm riêng thành một dòng "không tới bước chọn chính sách" | |
| **Khung thời gian / ngưỡng báo động** | (không áp dụng) | |
| **Điểm mù** (thước đo này KHÔNG thấy gì) | Không thấy lỗi khi chính bảng `policies` nhập sai ngày hiệu lực; không thấy trường hợp chọn đúng chính sách nhưng tính sai tiền hoặc sai độ trễ ở bước sau | |

**Ví dụ mẫu (bước "chọn độ trễ" của agent, đừng chép):**
Thước đo: tỉ lệ lần chạy mà độ trễ agent dùng để tính tiền khác độ trễ theo tracking DB. Dữ liệu: sự kiện `proposal.delay_days_used`
và `tracking.db_delay_days` trong `runs/<mã lần chạy>/traces/`, 22 ticket × 5 seed của bộ nền. Cách tính: số lần hai giá trị khác
nhau chia cho số lần chạy có sự kiện `proposal`; lần chạy không tới bước `proposal` bị loại khỏi mẫu số và đếm riêng.
Điểm mù: không thấy trường hợp chính tracking DB sai.

*(Ở vòng 2, Phiếu C mục C8 dùng lại đúng bảng ba ô này cho chỉ số theo dõi mới của bàn.)*

---

<a id="a3"></a>

## A3 · Đọc một kết quả có khoảng tin cậy (phút 35–40)

### Câu 1.5 · Chọn MỘT kết luận và giải thích một câu

Số minh hoạ trong đề (không phải số của bàn). Khoanh: **(a) · (b) · (c) · (d)**

Giải thích một câu: …

---

<a id="a4"></a>

## A4 · Câu tiêu chí thành công (phút 40–60)

### Câu 1.6 · Bản tiêu chí

**Cách làm, ba bước:** (1) viết tiêu chí thành **một câu có hành động đi kèm**, thử vài phiên bản;
(2) đưa từng phiên bản qua bốn câu hỏi soát; (3) chốt bản cuối và hẹn ngày xem lại. Điểm mấu chốt: một tiêu chí chưa nói
"nếu trượt thì làm gì" thì chưa phải tiêu chí.

#### Bước 1 · Viết câu tiêu chí (mỗi chỉ số bắt buộc một câu; thử 2 phiên bản cho chỉ số bàn tranh luận nhiều nhất)

> Nếu **{chỉ số, có đơn vị}** của **{trợ lý hoàn tiền, trên bộ thử nào}** **{tụt dưới / vượt quá}** **{ngưỡng}**
> thì chúng tôi sẽ **{hành động cụ thể: Tiếp tục / Thu hẹp phần nào / Cải tiến thêm tới ngày nào / Dừng}**.

| Chỉ số (khoá trong `acceptance_criteria.json`) | Phiên bản 1 | Phiên bản 2 (nếu có) |
|---|---|---|
| `pass_rate_min` | | |
| `pass_k_min` (pass^k: ticket đúng cả 5/5 lần chạy) | | |
| `wrongful_refund_vnd_max` | | |
| `wrongful_carrier_faults_max` | | |
| `pii_leaks_max` | | |
| nên có: `escalation_rate_max` | | |

#### Ranh giới đầu ra (không thêm trường vào file JSON)

Đây không phải ngưỡng chất lượng. Viết hai câu trên phiếu này thôi, không chép vào `acceptance_criteria.json`.

- Một đầu ra hoặc hành động bị cấm (ví dụ không bao giờ hoàn quá X đồng): ____
- Ngưỡng chuyển cho người duyệt: ____

#### Bước 2 · Soát từng câu

| Câu hỏi soát | Ghi chú của bàn |
|---|---|
| Chỉ số này có ý nghĩa với **mọi** bên liên quan không (khách, hãng vận chuyển, shop, người duyệt, kế toán)? | |
| Chạy theo chỉ số này có thể làm **ai thiệt** (ví dụ ép tỉ lệ tự động cao thì ai gánh)? | |
| Đây có phải nghĩa của "thành công" ở **ngày 1** của pilot không? | |
| Còn ở **ngày thứ 1.000** (12 depot, chính sách đã đổi vài lần)? Ngưỡng nào sẽ phải viết lại? | |

#### Bước 3 · Chốt và hẹn ngày xem lại

- Bản cuối của từng câu → chép **ngưỡng** vào `required` / `nice_to_have` / `business_ops`, chép **hành động** vào `decision_rule`
  (bốn dòng: Tiếp tục, Thu hẹp, Cải tiến thêm, Dừng) và `stop_condition`. Các khoá này nằm ngay trong `config/acceptance_criteria.json`.
- Nhóm `business_ops` (chi phí mỗi ticket tối đa, ROI tối thiểu, số ca ùn tối đa): `cost_per_ticket_vnd_max` ____ · `roi_min` ____ · `queue_stuck_max` ____
- Ngày xem lại tiêu chí: `__________` · Ai dự: `__________` (ghi vào Phiếu B mục B8, dòng "Ngày quyết định lại").

**Gợi ý chọn ngưỡng:** các chỉ số an toàn (`wrongful_refund_vnd_max`, `wrongful_carrier_faults_max`, `pii_leaks_max`) có thể để 0; với chi phí, tỉ lệ và ROI, xem `data/world.json` mục `ops_facts`.

**Ví dụ một câu (đừng chép ngưỡng):** "Nếu số lỗi hãng oan của trợ lý trên bộ nền hoặc trên bất kỳ gói thử nào vượt quá 0
thì chúng tôi sẽ không chọn Tiếp tục; nếu sau một vòng sửa vẫn vượt, tắt tool ghi lỗi hãng và chọn Thu hẹp."

---

<a id="a5"></a>

## A5 · Ký và đẩy tiêu chí (phút 60–65)

Soát lại `config/acceptance_criteria.json` lần cuối (tên bàn ở `team`, người ký ở `signed_by`, đủ ngưỡng, `decision_rule`,
`stop_condition`), rồi chạy **trước khi chạy đánh giá lần nào**:

```bash
python3 -m lab10.criteria sign
git add config/acceptance_criteria.json config/acceptance_criteria.lock && git commit -m 'Sign acceptance criteria' && git push -u origin main
```

| Mục | Điền |
|---|---|
| Đã ký lúc (giờ máy in hoặc `signed_at` trong `config/acceptance_criteria.lock`) | |
| Mã commit `Sign acceptance criteria` (7 ký tự đầu, `git log --oneline -1`) | |
| Đã push lên `origin main` thành công? | có / chưa |

Sau bước này **không sửa** `config/acceptance_criteria.json`, kể cả mở rồi lưu lại bằng trình soạn thảo tự định dạng.
