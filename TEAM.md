# Team

## Thông tin nhóm

- Tên nhóm: NoName
- Lớp: L3A
- Repo của bàn:https://github.com/Letruong238/K5-L3A-DAY10-NoName-PoCtoPilotGate1
- Thẻ sự cố đã bốc (S1–S8): S7

## Thành viên

Họ tên đầy đủ và MSSV của **mọi** thành viên; thêm dòng nếu cần. Vai: Kỹ sư cổng · Sản phẩm và kinh doanh · Vận hành và pháp lý (README mục 3, phút 0–15).

| STT | Họ và tên       | MSSV        | Vai                    | Trưởng nhóm |
| --: | --------------- | ----------- | ---------------------- | :---------: |
|   1 | Lê Quang Trường | 2A202603663 | Sản phẩm và kinh doanh |      X      |
|   2 | Hoàng Đăng Kiên | 2A202603636 | Vận hành và pháp lý    |             |
|   3 | Mai Văn Thanh   | 2A202603696 | Kỹ sư cổng             |             |
|   4 |                 |             |                        |             |

Ghi `members` trong `submission/submission.json` theo dạng `"HoVaTen-MSSV"`, khớp bảng trên.

## Cá nhân

Mỗi thành viên tự viết một mục bên dưới (chép mẫu, đổi tiêu đề thành họ tên không dấu và MSSV, ví dụ `## NguyenVanAn-20241234`).

## LeQuangTruong-2A202603663

### Phần việc phụ trách

Vai **Sản phẩm và kinh doanh**, trưởng nhóm. Phút 0–15: tạo repo, gắn `upstream`, điền bảng thành viên, chọn eval card và PRD v1.1 từ Lab 9 của mình làm bản chung (`evalcard&PRDv1.1.md`). Khối 1: câu 1.1, 1.5, 1.6 và ký tiêu chí (Phiếu A mục A1, A3, A4, A5; `config/acceptance_criteria.json`). Khối 2: câu 2.3 (Phiếu B mục B3), câu 2.9 (Phiếu B mục B7.4; `config/operating_gates.json` mục `business`). Khối 3: ghi thẻ S7, câu 3.0 (Phiếu C mục C0, C1), câu 3.2 (C5), câu 3.4 (C6), câu 3.5 phần `business` và tổng hợp bảng sửa (C7), quyết định Gate 1 v2 và ba dòng bắt buộc (C12).

### Đóng góp cụ thể

- **Tiêu chí ký trước khi đo:** viết mục tiêu cấp hệ thống từ PRD v1.1 §3 (tiền đúng chính sách và khớp câu trả lời, không ghi lỗi oan cho hãng, không lách phê duyệt); đọc khoảng tin cậy câu 1.5 (chọn (b)); viết 6 câu "Nếu … thì chúng tôi sẽ …", hai câu ranh giới đầu ra, bảng soát bốn câu hỏi. Chọn ngưỡng từ PRD Lab 9 và `data/world.json`, không chép file example: `pass_rate_min` 0,9; `pass_k_min` 0,8; ba chỉ số an toàn bằng 0; `escalation_rate_max` 0,25; `cost_per_ticket_vnd_max` 6.000đ; `roi_min` 0,5; `queue_stuck_max` 0; cùng `stop_condition` và bốn dòng `decision_rule`. Ký và push trước lần đánh giá đầu tiên.
- **Bản đồ dữ liệu (B3):** chỉ ra trường nguồn sự thật và bản sao (độ trễ tính từ `delivered_date − promised_date`, số ngày khách kể chỉ là lời kể; `index_active` là bản sao); ví dụ drift `REFUND-v3 → REFUND-v4` ngày 01/12/2026 là quan hệ vào–ra đổi, minh hoạ bằng `T-002` (tracking trễ 2 ngày: v3 từ chối, v4 phải hoàn).
- **Cổng kinh doanh (B7.4):** trần hoàn tự động 800.000đ/ngày (2/5 ngân sách Finance 2.000.000đ cho 2 kho pilot), ngân sách LLM 1.500đ/ticket (đúng `ops_limits`), `roi_min` 0,5, phạm vi HN + HCM ở vòng 1.
- **Vòng 2, thẻ S7:** đo mốc prepared và phát hiện cổng vòng 1 chặn 30/30 lần lộ nhưng **2 ticket kho DN, CT bị che** bởi `pilot_scope` chứ không phải đã sửa, và chi phí 6.434đ vượt ngưỡng đã ký. Viết SPEC-S7 (kênh gửi hãng chỉ cho đi 4 trường trong `carrier_notice_fields`, giá trị lấy từ dữ liệu hệ thống), phân biệt **ngăn** (allowlist) với **giảm** (dò mẫu số điện thoại), và tìm ra khe hở "nhét dữ liệu vào khoá hợp lệ". Vẽ fault tree 5 lá ở 4 tầng. Đổi `business.pilot_scope` về tất cả kho: độ phủ S7 0,75 → 1,0, chi phí 6.434đ → 5.005đ, ROI 0,55 → 1,0, bộ nền không ca nào hỏng.
- **Quyết định:** v2 đổi từ Thu hẹp (v1) sang **Tiếp tục có điều kiện**, khớp dòng "Tiếp tục" của `decision_rule` đã ký; viết ba dòng bắt buộc.
- **Giữ tính toàn vẹn bài nộp:** phát hiện commit "2.4" vô tình đổi ký tự xuống dòng của `config/acceptance_criteria.json` (hash lệch `3631fb42` so với bản ký `9e43a50e`); thử hai cách trên bản sao, chọn viết lại lịch sử sau commit ký rồi force push có điều kiện, sau đó kiểm `lab10.criteria` báo "tiêu chí giữ nguyên từ commit 'Sign acceptance criteria'". Lấy đủ thẻ S1–S8 và đối chiếu 32/32 file với `lab10/MANIFEST.json` để dòng integrity qua (bàn chỉ mở và làm thẻ S7).

### Bằng chứng

- Commit: `f53b30d` (bảng thành viên, link Lab 9), `bd9ff5f` (câu 1.1), `2504eb4` (**Sign acceptance criteria**, hash tiêu chí `9e43a50e`), `937dfcb` (Phiếu A mục A1–A5), `0dbc2d5` (câu 2.3), `6e8f8c4` (câu 2.9), `a5c09eb` (thẻ S7, C0, C1), `32e7ee9` (C5 câu 3.2), `f70c3d2` (đủ thẻ S1–S8), `ef49bf0` (vòng 2: cổng `notify_carrier`, `pilot_scope`, ops/legal; C6, C7), commit C12.
- Lần chạy: S7 prepared `R-S7-prepared-20261118-172454-0f72f4`; sau khi sửa `R-S7-after-20261118-172913-5940b3` (code), `R-S7-after-20261118-172924-ce259f` (`pilot_scope`), `R-S7-after-20261118-172950-5029fa` (ops/legal); bộ nền `R-base-after-20261118-172950-5029fa`; tự kiểm tra `R-S7-grade-20261118-174454-d43ead` (**PASS-VISIBLE**, cả 5 dòng ✅).
- Dòng trong phiếu: Phiếu A mục A1 (câu 1.1), A3, A4, A5; Phiếu B mục B3, B7.4; Phiếu C dòng `Thẻ đã bốc`, C0 dòng 1–5, C1, C5 (câu 3.2), C6, C7, C12.
- Dùng AI: có dùng Claude Code để đọc đề, code và dữ liệu, chạy lệnh, soạn nháp câu trả lời và xử lý lỗi Git. Mọi ngưỡng, con số và quyết định tôi đã đối chiếu lại với report và trace, và giải thích được lúc demo.

### Exit ticket

- Một điều học được: viết ngưỡng **trước** khi xem số thì quyết định mới không bị kéo theo kết quả; và "thu hẹp phạm vi" không phải lúc nào cũng an toàn hơn: ở thẻ S7, thu hẹp về HN + HCM vừa che mất lỗi ở kho DN vừa làm chi phí mỗi ticket vượt ngưỡng đã ký.
- Một điều còn chưa chắc: quyết định "Tiếp tục" dựa trên bộ thử mock 8 ticket và MockLLM tất định; tôi chưa chắc cổng còn đứng được trước bài kiểm tra ẩn, trước LLM thật, và khi chính dữ liệu nguồn (`district`, `delay_cause`) bị nhập sai.

## MaiVanThanh-2A202603696

### Phần việc phụ trách

Vai **Kỹ sư cổng**. Câu 1.3 (Phiếu A mục A2, cột Offline); câu 2.1, 2.2 (Phiếu B mục B0 dòng 1–4, B1, B2); câu 2.6, 2.7, 2.8 (Phiếu B mục B7.1, B7.2, B7.3) và bản nháp pre-mortem câu 2.5 (B6) cho cả bàn sửa; chốt cổng vòng 1 và chạy mốc prepared (B8); vòng 2: nhận thẻ S7, câu 3.1 (Phiếu C mục C2), câu 3.6 (Phiếu C mục C8). File: `lab10/guards.py`, `lab10/monitors.py`.

### Đóng góp cụ thể

- Thiết kế thước đo offline cho bước "chọn chính sách" (tỉ lệ `policy_id` khác chính sách có hiệu lực theo ngày `as_of`).
- Chạy mốc base, so với tiêu chí đã ký, dò trace `T-002@55` và xếp hai lỗi chìm: hoàn 20.000đ theo số ngày khách khai, ghi lỗi oan cho VNX kèm gửi `customer_note` cho hãng.
- Viết 4 cổng trong `lab10/guards.py`: `pre_guard` ghim chính sách theo ngày hiệu lực; `write_gate` cho `issue_refund` (tính lại quyền lợi từ tracking, chặn hoàn trùng, kiểm phê duyệt, chặn bắt shop trả); `file_carrier_fault` (chỉ ghi lỗi khi tracking có nguyên nhân thuộc `fault_causes`, sửa đúng kiện, đúng hãng); `notify_carrier` (chỉ gửi các trường trong `carrier_notice_fields`). Bộ nền từ 109/110 lên 110/110 lần chạy đúng, không ca nào hỏng; cổng `notify_carrier` vòng 1 chặn được 30/30 lần lộ dữ liệu của thẻ S7 trước khi bàn biết sự cố.
- Viết behavioral test và hai ticket hiểm (`O-1004` khai phồng ngày trễ, `O-1026` quà tặng có số điện thoại) dùng cho demo.
- Phát hiện và xử lý lỗi CRLF: Git trên Windows đổi ký tự xuống dòng của `config/acceptance_criteria.json` làm lệnh kiểm tra báo "tiêu chí đã bị sửa"; trả file về đúng bản lúc ký (hash `9e43a50e`), viết lại commit "2.4" để không còn commit nào chạm file tiêu chí sau commit ký.
- Lấy thẻ S7, đối chiếu cả 4 file với hash trong `lab10/MANIFEST.json` trước khi đưa vào repo; dò 8 ticket của thẻ, tìm hai đường lộ dữ liệu khác nguồn (`customer_note` chép chữ khách; `recipient_contact` trợ lý tự lấy từ đơn quà tặng).
- Thêm chỉ số `pii_toward_carrier_rate` trong `lab10/monitors.py`: 0,0 trên bộ nền, 0,7143 trên gói S7.

### Bằng chứng

- Commit: `fd27022` (câu 1.3), `3191cd8` (câu 2.1, 2.2), `fde3a85` (câu 2.5–2.8, cổng vòng 1), `3f874b9` (chốt cổng vòng 1, hash `8229821d`), `c2bb3ac` (nhận thẻ S7), `ee76b73` (Phiếu C mục C2), `c40080f` (câu 3.6, mục C8).
- Lần chạy: base `R-base-before-20261118-155047-b45eeb`; cổng vòng 1 `R-base-after-20261118-160900-347f50`; prepared `R-base-prepared-20261118-163540-1eb136`; chỉ số mới `R-S7-after-20261118-173353-5c508a` và `R-base-after-20261118-173354-5c508a`; tự kiểm tra `R-S7-grade-20261118-173356-5c508a` (integrity, criteria, visible, regression, monitor đều ✅).
- Dòng trong phiếu: Phiếu A mục A2; Phiếu B mục B0, B1, B2, B6, B7.1–B7.3, B8; Phiếu C mục C2, C8 và dòng 6 của C0.
- Dùng AI: có dùng Claude Code để đọc code agent, gợi ý cách viết cổng và chỉ số theo dõi, chạy lệnh và soạn nháp câu trả lời trong phiếu. Mọi con số, cổng và kết luận tôi đã đối chiếu lại với trace và report, và giải thích được lúc demo.

### Exit ticket

- Một điều học được: cổng tốt nhất là cổng "chỉ cho đi những gì được phép" dựa trên nguồn sự thật (tracking DB, danh sách trường trong chính sách), không phải cổng dò từng mẫu lỗi; nhờ vậy cổng vòng 1 đỡ được sự cố S7 trước khi biết thẻ.
- Một điều còn chưa chắc: cổng chỉ đúng khi chính nguồn sự thật đúng; nếu `delay_cause` do tài xế nhập tay sai, hoặc chính sách tự thêm một trường cá nhân, cổng vẫn cho qua mà chưa có chỉ số nào bắt được.
