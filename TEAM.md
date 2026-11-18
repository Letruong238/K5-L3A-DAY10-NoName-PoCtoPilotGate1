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

## HoVaTen-MSSV

### Phần việc phụ trách

Vai trong bàn; câu nào của đề, mục nào của phiếu A/B/C, file nào (`lab10/guards.py`, `config/operating_gates.json`, …).

### Đóng góp cụ thể

...

### Bằng chứng

Mã commit, mã lần chạy (`runs/<mã>`), dòng trong phiếu.

### Exit ticket

Một điều học được, một điều còn chưa chắc.

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
