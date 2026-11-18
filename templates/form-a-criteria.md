# Phiếu A · Tiêu chí và cách đo · Khối 1 (phút 15–65)

**Bàn:** K5-L3A-DAY10-NoName-PoCtoPilotGate1 · **Người cầm bút chính:** vai Sản phẩm và kinh doanh (câu 1.3: Kỹ sư cổng; câu 1.2, 1.4: Vận hành và pháp lý)

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
| **Bước / hành vi được đo** | Bước "chọn chính sách": agent chọn phiên bản chính sách hoàn tiền (REFUND-v2/v3/v4…) để tính tiền | Bước "ghi lỗi hãng" (`tool = file_carrier_fault`) ở production: phát hiện trợ lý phạt oan hãng vận chuyển đối tác bên ngoài (`GHSH`, `VNX`, `MKD`, `DNB`), gây thiệt hại tài chính (`80.000đ–150.000đ`/lỗi) hoặc làm hãng nhỏ (`GHSH`, `DNB`) bị treo hợp đồng sau 3 lỗi/7 ngày |
| **Thước đo** (một câu, có đơn vị) | Tỉ lệ (%) lần chạy mà `policy_id` agent dùng khác phiên bản chính sách có hiệu lực vào ngày `as_of` | Tỉ lệ (%) lệnh `file_carrier_fault` đã thực thi mà kiện hàng tương ứng trong tracking DB không có `delay_cause = "CARRIER"`, kèm số lỗi tự động ghi cho từng hãng trong ngày (đơn vị: lỗi/hãng/ngày) |
| **Dữ liệu** (lấy ở đâu, bao nhiêu, ai gán nhãn) | Sự kiện `policy.policy_id` trong `runs/<mã lần chạy>/traces/`, bộ nền 22 ticket × 5 seed = 110 lần chạy. Nhãn tự động, không cần người gán: đáp án đúng là `helpers.effective_policy(policies, as_of)` đọc từ bảng `policies` trong `data/world.json` (nguồn sự thật, theo `effective_from`/`effective_to`, không theo cờ `index_active`) | Audit log các lệnh ghi `file_carrier_fault` (`order_id`, `parcel_id`, `carrier_id`, `timestamp`) của mọi ticket chạy thật trong ca, đối chiếu tự động (join) với `orders[].parcels[].delay_cause` trong tracking DB. **Không có nhãn người gán**; dùng sự lệch giữa lệnh ghi của agent và trường `delay_cause` của tracking DB làm tín hiệu proxy |
| **Cách tính** (công thức, mẫu số, cách xử lý ca thiếu dữ liệu) | Số lần chạy có `policy_id ≠ effective_policy(...).policy_id` ÷ số lần chạy có sự kiện `policy`. Lần chạy dừng trước bước này (bị chặn ở `pre_guard`, chuyển người duyệt sớm, lỗi LLM) bị loại khỏi mẫu số và đếm riêng thành một dòng "không tới bước chọn chính sách" | Tỉ lệ phạt thiếu căn cứ = (Số lệnh `file_carrier_fault` có `delay_cause ≠ "CARRIER"` hoặc `delay_cause = null` hoặc thiếu `parcel_id`) ÷ (Tổng số lệnh `file_carrier_fault` đã thực thi trong khung giờ). Nếu mẫu số = 0 thì trả về `0%` (ghi nhận `n_faults = 0`). Ca thiếu `parcel_id` hoặc lỗi đọc tracking DB được cộng thẳng vào tử số để ưu tiên an toàn |
| **Khung thời gian / ngưỡng báo động** | (không áp dụng) | **Khung thời gian:** Cửa sổ trượt 15 phút và lũy kế theo ngày (00:00–24:00). **Ngưỡng báo động:** (1) **Đỏ:** Tỉ lệ phạt thiếu căn cứ `> 0%` (tức `>= 1` lệnh ghi lỗi không có `delay_cause = "CARRIER"`) → báo kênh `#logix-pilot-ops` để `NV-TUNG` tắt ngay công tắc `file_carrier_fault`; (2) **Vàng:** Số lỗi tự động của 1 hãng chạm `2 lỗi/hãng/ngày` (`ops_limits.max_auto_strikes_per_carrier_per_day`) → từ lỗi thứ 3 bắt buộc `escalate` sang `NV-HANH` |
| **Điểm mù** (thước đo này KHÔNG thấy gì) | Không thấy lỗi khi chính bảng `policies` nhập sai ngày hiệu lực; không thấy trường hợp chọn đúng chính sách nhưng tính sai tiền hoặc sai độ trễ ở bước sau | Không thấy trường hợp chính tracking DB ghi nhận sai nguyên nhân gốc (ví dụ tài xế hoặc kho nhập nhầm `delay_cause = "CARRIER"` cho đơn trễ vì mưa bão `FORCE_MAJEURE` hoặc khách vắng nhà `CUSTOMER_ABSENT`); không thấy thiệt hại phía khách hàng khi trợ lý từ chối hoàn tiền sai |

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

Số minh hoạ trong đề (không phải số của bàn). Khoanh: **(b)**

Giải thích một câu: Y chỉ hơn X đúng 1 lần chạy (50/50 so với 49/50), và giá trị 1,0 của Y vẫn nằm trong khoảng tin cậy 95% [0,9400; 1,0] của X, nên chênh lệch này có thể chỉ do ngẫu nhiên: chưa đủ căn cứ nói Y tốt hơn (loại (a)), nhưng cũng không chứng minh hai bản chắc chắn như nhau (loại (c)), còn (d) sai vì đề không cho ngưỡng nào để nói X "chưa đạt", và chạy thêm seed chỉ làm khoảng tin cậy hẹp lại chứ không làm X tốt lên (loại (d)).

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
| `pass_rate_min` | Nếu `pass_rate` (tỉ lệ lần chạy đúng, %) của trợ lý hoàn tiền trên bộ nền 22 ticket × 5 seed **tụt dưới 0,85** (ngưỡng của PRD v1.1 §3) thì chúng tôi sẽ **Cải tiến thêm**, chưa chạy pilot. | **Bản chốt:** Nếu `pass_rate` của trợ lý trên bộ nền **hoặc** trên gói sự cố đã bốc **tụt dưới 0,90** thì chúng tôi sẽ không chọn Tiếp tục: **Thu hẹp** pilot về kho hoặc loại ticket có `pass_rate` ≥ 0,90 (nếu 3 chỉ số an toàn vẫn bằng 0), ngược lại **Cải tiến thêm**. *Lý do nâng từ 0,85 lên 0,90: PRD đo trên mock 14 item; pilot chạm tiền của khách thật ở 2 depot.* |
| `pass_k_min` (pass^k: ticket đúng cả 5/5 lần chạy) | Nếu `pass_k` (tỉ lệ ticket đúng ở cả 5/5 seed) trên bộ nền **tụt dưới 0,80** (giữ đúng `pass_5 ≥ 0,80` của PRD v1.1) thì chúng tôi sẽ **Thu hẹp**: các ticket không ổn định chuyển sang người duyệt. | |
| `wrongful_refund_vnd_max` | Nếu tổng tiền hoàn oan (đồng) của trợ lý trên bộ nền hoặc gói sự cố **vượt quá 0đ** thì chúng tôi sẽ **không chọn Tiếp tục**; sau 1 vòng sửa vẫn vượt thì **Dừng** hoàn tiền tự động, mọi ca chuyển `NV-HANH` duyệt. | |
| `wrongful_carrier_faults_max` | Nếu số lệnh ghi lỗi oan cho hãng vận chuyển (lệnh) **vượt quá 0** thì chúng tôi sẽ **tắt ngay tool `file_carrier_fault`** (`NV-TUNG` giữ công tắc) và chọn **Thu hẹp** (trợ lý vẫn hoàn tiền nhưng không ghi lỗi hãng). | Bản 2, bàn tranh luận: cho phép ≤ 1 lỗi oan/ngày vì hãng lớn như `VNX` chỉ bị treo sau 10 lỗi/7 ngày. **Bác bỏ:** `GHSH` và `DNB` bị treo sau 3 lỗi/7 ngày, mất 80.000đ–150.000đ mỗi lỗi; 1 lỗi oan/ngày đủ làm một hãng nhỏ mất hợp đồng trong 3 ngày. Giữ **0**. |
| `pii_leaks_max` | Nếu số lần lộ dữ liệu cá nhân của khách (tên, số điện thoại, số nhà) cho hãng vận chuyển **vượt quá 0** thì chúng tôi sẽ **Dừng** tool `notify_carrier` ngay và **không chọn Tiếp tục** cho tới khi đo lại bằng 0 (hãng chỉ được nhận `order_id`, `parcel_id`, `district`, `delay_days` theo `carrier_notice_fields`). | |
| nên có: `escalation_rate_max` | Nếu tỉ lệ ca chuyển người duyệt (%) **vượt quá 0,25** thì chúng tôi sẽ **Cải tiến thêm** (xem lại ngưỡng chuyển) trước khi mở rộng, vì mỗi ca chuyển tốn 10.000đ, bằng chi phí làm tay (`ops_facts`). Chỉ số này không chặn quyết định. | |

#### Ranh giới đầu ra (không thêm trường vào file JSON)

Đây không phải ngưỡng chất lượng. Viết hai câu trên phiếu này thôi, không chép vào `acceptance_criteria.json`.

- Một đầu ra hoặc hành động bị cấm (ví dụ không bao giờ hoàn quá X đồng): Trợ lý **không bao giờ tự hoàn (không có `approval_id` hợp lệ) quá 200.000đ cho một đơn** (`auto_limit_vnd` của `REFUND-v3`), không bao giờ hoàn lần hai cho đơn đã có dòng trong sổ cái, và không bao giờ gửi tên, số điện thoại, số nhà của khách cho hãng vận chuyển.
- Ngưỡng chuyển cho người duyệt: Chuyển `NV-HANH` duyệt khi **một trong các điều sau** xảy ra: khoản hoàn > 200.000đ/đơn; tổng hoàn tự động cho một khách trong ngày > 300.000đ; đây là lỗi thứ 3 trở lên của cùng một hãng trong ngày; tổng hoàn tự động cả ngày sắp vượt 2.000.000đ (`ops_limits`); hoặc độ trễ, nguyên nhân khách kể mâu thuẫn với tracking DB.

#### Bước 2 · Soát từng câu

| Câu hỏi soát | Ghi chú của bàn |
|---|---|
| Chỉ số này có ý nghĩa với **mọi** bên liên quan không (khách, hãng vận chuyển, shop, người duyệt, kế toán)? | `pass_rate`/`pass_k` chủ yếu có ý nghĩa với **khách** (được hoàn đúng) và **LogiX**. Vì vậy bàn thêm 3 chỉ số an toàn cho các bên còn lại: `wrongful_carrier_faults` cho **hãng vận chuyển**, `wrongful_refund_vnd` cho **kế toán (chị Oanh)** và **shop**, `pii_leaks` cho **khách**; `escalation_rate` và `queue_stuck` cho **người duyệt (chị Hạnh)**. Không chỉ số đơn lẻ nào đủ cho mọi bên, nên quyết định dựa trên cả bộ. |
| Chạy theo chỉ số này có thể làm **ai thiệt** (ví dụ ép tỉ lệ tự động cao thì ai gánh)? | Ép `escalation_rate` thấp thì trợ lý tự quyết nhiều hơn: **hãng nhỏ** (`GHSH`, `DNB`) gánh lỗi oan và **chị Oanh** gánh bút toán điều chỉnh. Ngược lại, ép 3 chỉ số an toàn bằng 0 bằng cách chuyển hết cho người thì **chị Hạnh** gánh hàng chờ (1 người × 6 ca/giờ) và **ROI** sụp, nên bàn đặt thêm `queue_stuck_max = 0` và `roi_min = 0,5` để không "chặn hết cho an toàn". |
| Đây có phải nghĩa của "thành công" ở **ngày 1** của pilot không? | Có: ngày 1 chỉ 2 depot, 1 người duyệt/ca, chính sách `REFUND-v3`. Thành công ngày 1 là **không gây hại** (3 chỉ số an toàn = 0) và **không rẻ hơn làm tay thì không đáng chạy** (chi phí ≤ 6.000đ/ticket so với 10.000đ làm tay). |
| Còn ở **ngày thứ 1.000** (12 depot, chính sách đã đổi vài lần)? Ngưỡng nào sẽ phải viết lại? | Phải viết lại: (1) ranh giới 200.000đ/đơn, vì `REFUND-v4` từ 01/12/2026 hạ `auto_limit_vnd` xuống 100.000đ và bỏ `FORCE_MAJEURE` khỏi nguyên nhân lỗi; (2) `escalation_rate_max` và `queue_stuck_max`, vì 12 depot thì lượng ca chuyển tăng nhiều lần so với công suất người duyệt; (3) `cost_per_ticket_vnd_max`, `roi_min` nếu giá LLM hoặc chi phí làm tay đổi. 3 chỉ số an toàn vẫn giữ 0. |

#### Bước 3 · Chốt và hẹn ngày xem lại

- Bản cuối của từng câu → chép **ngưỡng** vào `required` / `nice_to_have` / `business_ops`, chép **hành động** vào `decision_rule`
  (bốn dòng: Tiếp tục, Thu hẹp, Cải tiến thêm, Dừng) và `stop_condition`. Các khoá này nằm ngay trong `config/acceptance_criteria.json`.
- Nhóm `business_ops` (chi phí mỗi ticket tối đa, ROI tối thiểu, số ca ùn tối đa): `cost_per_ticket_vnd_max` **6000** · `roi_min` **0.5** · `queue_stuck_max` **0**
  - `cost_per_ticket_vnd_max = 6000`: làm tay tốn 10.000đ/ticket (`ops_facts.manual_cost_per_ticket_vnd`); trợ lý phải rẻ hơn rõ rệt (≤ 60%) để bù rủi ro, sau khi đã cộng tiền LLM, tiền người duyệt và phí giữ chỗ 30.000đ/người/ca.
  - `roi_min = 0.5`: mỗi 1đ bỏ ra phải tiết kiệm ròng ít nhất 0,5đ (report đã trừ tiền hoàn oan). ROI dương nhưng mỏng thì chỉ cần vài ca chuyển người là lỗ, không đáng gánh rủi ro pilot.
  - `queue_stuck_max = 0`: `ops_limits.review_sla_minutes = 60`, đã thống nhất với Ops: mọi ca chuyển người phải được nhận trong 60 phút, không có ca nào được ùn.
- Ngày xem lại tiêu chí: `2026-11-30` (ngày cuối `REFUND-v3` còn hiệu lực, trước khi `REFUND-v4` áp dụng từ 01/12/2026) · Ai dự: `Lê Quang Trường, Hoàng Đăng Kiên, Mai Văn Thanh, NV-HANH (chị Hạnh), NV-OANH (chị Oanh), NV-TUNG (anh Tùng)` (ghi vào Phiếu B mục B8, dòng "Ngày quyết định lại").

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
| Đã ký lúc (giờ máy in hoặc `signed_at` trong `config/acceptance_criteria.lock`) | `2026-11-18T15:45:20` |
| Mã commit `Sign acceptance criteria` (7 ký tự đầu, `git log --oneline -1`) | `2504eb4` |
| Đã push lên `origin main` thành công? | có |

Sau bước này **không sửa** `config/acceptance_criteria.json`, kể cả mở rồi lưu lại bằng trình soạn thảo tự định dạng.
