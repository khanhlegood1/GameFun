-- SINH TỰ ĐỘNG bởi scripts/gen_supabase_migrations.py — ĐỪNG SỬA TAY.
-- Nguồn: pm/sql/*.sql và pm/*.json. Sửa nguồn rồi chạy lại.

-- Nguồn: pm/action-register.json · pm/claims-registry.json
-- as_of: 2026-11-23

begin;

insert into pm_people (code, name, kind, role, tz) values
  ('AGENT', 'Tác nhân tự động', 'agent', 'agent', 'Asia/Ho_Chi_Minh'),
  ('LXK', 'Lê Xuân Khánh', 'human', 'người sáng lập kiêm PO', 'Asia/Ho_Chi_Minh')
on conflict (code) do update set name = excluded.name, role = excluded.role;

insert into pm_actions (id, title, source_doc, why, owner_code, agent_allowed,
  owner_reason, not_before, due, block_if_unmet, block_note, evidence_req,
  status, done_on, evidence) values
  ('P1', 'Thêm ràng buộc biên S_LP < X_end·(1−f) vào validate_launch', 'docs/36-kvu-lemmas-and-the-version-unit.md', $q$Nếu S_LP vượt biên, mẫu số của (★) âm và bất đẳng thức escrow ≥ 0 KHÔNG NÓI ĐƯỢC GÌ — loại lỗi nguy hiểm hơn 'sai'. Hiện validate_launch chưa chặn.$q$, 'LXK', false, 'Sửa spec nguồn ⇒ đổi terms_hash của mọi launch tương lai và rebuild PDF. Cần người quyết.', '2026-11-23', '2026-12-18', 'revert', $q$Quá hạn ⇒ DÙNG số biên rút gọn và ghi rõ spec chưa chặn; hoặc gỡ câu 'escrow ≥ 0 được bảo đảm trước launch' khỏi mọi tài liệu.$q$, 'docs/YELLOWPAPER.md §5.1 hoặc §6.1 có câu ràng buộc biên, VÀ scripts/kvu_invariants.py lemma3 vẫn xanh', 'OPEN', null, null),
  ('P2', 'Ghi vào YELLOWPAPER §4.3 rằng gộp root Merkle theo giờ là BẮT BUỘC vì rent', 'docs/36-kvu-lemmas-and-the-version-unit.md', 'Spec đã dùng Root_h (một root/giờ) nhưng không nói đó là quyết định chi phí. Nếu mỗi phiên bản một root: 10.000 root/giờ × 48 B ⇒ ~11 SOL/giờ rent, không khả thi.', 'LXK', false, 'Thêm một câu vào nguồn spec ⇒ rebuild PDF. Nội dung câu thì agent soạn được, việc ký thì không.', '2026-11-23', '2026-12-18', 'revert', $q$Quá hạn ⇒ gỡ con số '11 SOL/giờ' khỏi mọi tài liệu trình bày và chỉ nói 'gộp theo giờ'.$q$, 'docs/YELLOWPAPER.md §4.3 chứa một câu về rent/gộp', 'OPEN', null, null),
  ('P3', 'Requirements lock: ghim phiên bản Python cho mọi cổng chạy CI (điều kiện tham số, không phải lời hứa)', 'docs/30-openrouter-deterministic-egress.md', 'Cổng chỉ chạy được nếu môi trường dựng lại được. `docs/README-PDF.md` còn nói `pip install reportlab` không phiên bản trong khi CI ghim 5.1.0 ⇒ md5 PDF khác giữa máy dev và CI.', 'AGENT', true, 'Máy kiểm được: tệp tồn tại, phiên bản khớp workflow, cổng đọc được nó.', '2026-12-15', '2026-12-20', 'remove', $q$Quá hạn ⇒ gỡ dòng 'md5 khớp' khỏi docs/README-PDF.md vì nó không còn đúng.$q$, 'requirements.txt có reportlab/fonttools/pypdf/pypdfium2, và docs/README-PDF.md trỏ tới nó', 'OPEN', null, null),
  ('P4', 'Cổng thứ 17: mọi việc có hạn đều phải kiểm được (check_actions.py)', 'docs/37-action-register-and-contradiction-hunt.md', 'P1 và P2 vừa được đăng ký bằng văn xuôi trong docs/36. Một việc có hạn nằm trong văn xuôi là một việc không có hạn — không cổng nào đọc được nó.', 'AGENT', true, 'Toàn bộ là mã và dữ liệu; máy tự kiểm.', '2026-11-23', '2026-11-24', 'remove', 'Quá hạn ⇒ xoá tệp này và ghi lại rằng P1/P2 chỉ là văn xuôi.', 'scripts/check_actions.py --selftest xanh trong .github/workflows/docs.yml', 'DONE', '2026-11-23', $q$scripts/check_actions.py --selftest → 'ACTION LOCK SELFTEST: PASS — 7/7 phép thử đúng chiều' (tệp: scripts/check_actions.py)$q$),
  ('P5', 'Biên (★) trên mô hình ĐẦY ĐỦ của cả hai hồ sơ là một bất biến của verify_protocol_math.py', 'docs/36-kvu-lemmas-and-the-version-unit.md', 'kvu_invariants.py đã tính 4,79× nhưng dưới dạng SỐ IN RA. Một con số in ra không phải một cổng: nó không làm CI đỏ khi công thức §6.1 đổi.', 'AGENT', true, 'Thêm assert vào tệp đã có; không đổi số đã công bố.', '2026-11-23', '2026-11-24', 'remove', $q$Quá hạn ⇒ xoá dòng 'biên thật 4,79×' khỏi docs/36 §5.2 vì nó chưa được khoá.$q$, 'verify_protocol_math.py có assert biên cho cả VBOND-LV và VGBC-4T; chạy lại vẫn 100%', 'DONE', '2026-11-23', $q$scripts/verify_protocol_math.py in 'margin (★) = 1.251170x / 4.790421x' và assert đúng hai giá trị đó (tệp: scripts/verify_protocol_math.py)$q$),
  ('P6', 'Bốn bất biến chưa có mã kiểm (INV-05, INV-07, INV-11, INV-12) phải có assert hoặc bị gỡ khỏi danh mục', 'docs/38-invariant-ledger-and-the-three-numbering-systems.md', 'Yellow Paper §8.1 khai 12 bất biến; scripts/ kiểm 8. Bốn mã còn lại là TÊN: INV-05 (phả hệ phiên bản), INV-07 (cô lập lưu ký token), INV-11 (cầu dao BotShare), INV-12 (bất biến governance). Một bất biến không có mã kiểm vẫn được trích trong tài liệu gọi vốn — và người đọc không có cách nào biết nó chưa được kiểm.', 'AGENT', true, 'Máy kiểm được: either có assert mang thẻ, hoặc mã bị gỡ khỏi danh mục và gỡ khỏi mọi câu trích. Cả hai đều là thay đổi cổng đọc được.', '2026-11-23', '2026-12-05', 'remove', $q$Quá hạn ⇒ gỡ 4 mã khỏi §8.1 và đổi mọi câu '12 bất biến' thành '8 bất biến có mã kiểm'.$q$, $q$scripts/check_invariants_coverage.py --audit cho 12/12 asserted, HOẶC danh mục YP §8.1 còn 8 mã và không tài liệu nào nói '12'$q$, 'DONE', '2026-11-23', $q$python3 scripts/verify_invariants.py → 'INVARIANTS: PASS — 66 kiểm tra · 4 bất biến (INV-05, 07, 11, 12)' và check_invariants_coverage.py --audit → 12/12 asserted (tệp: scripts/verify_invariants.py)$q$),
  ('P7', 'Thống nhất `--selftest` / `--self-test` thành MỘT tên cờ trên mọi cổng', 'docs/40-gates-that-never-ran.md', $q$`gate_decide.py` và `check_specs.py` nhận `--self-test`; mười cổng còn lại nhận `--selftest`. Chép một dòng workflow sang cổng khác ⇒ argparse thoát mã 2 với 'unrecognized arguments'. Lỗi ồn ào nhưng dễ bị 'sửa' bằng cách xoá cổng khỏi workflow — đúng thứ docs/40 muốn chặn.$q$, 'AGENT', true, 'Đổi tên cờ là việc cơ học, máy kiểm được: mọi cổng nhận cùng một tên, và check_gate_wiring.py đọc được cờ.', '2026-11-23', '2026-12-10', 'accept', 'Quá hạn ⇒ chấp nhận hai tên cờ, nhưng phải ghi vào AGENTS.md rằng tên cờ KHÁC NHAU giữa các cổng — để người chép workflow biết mà tra.', 'mọi cổng trong scripts/ nhận cùng một tên cờ, và check_gate_wiring.py vẫn xanh', 'OPEN', null, null),
  ('P8', 'Chọn thứ tự sản phẩm: launchpad-first hay dịch-vụ-kiểm-định-first', 'docs/41-testing-is-the-product.md', $q$docs/41 §2 chỉ ra arena đấu mù cần người chấm là game thủ, còn §5 chỉ ra 3/5 nguồn thu (quảng cáo 50/50, dịch vụ studio, và gián tiếp LP) không cần nhà đầu tư nào tồn tại. Nếu sản phẩm đầu là dịch vụ kiểm định thì điều kiện mở launchpad '500 người chơi thật/tuần' đang đặt sai chỗ: nó là điều kiện cho sản phẩm thứ hai.$q$, 'LXK', false, 'Đổi thứ tự sản phẩm ⇒ đổi §3 WHO, §5.4 doanh thu, điều kiện mở launchpad, và rebuild whitepaper + pitch deck. Đây là quyết định chiến lược, không phải việc máy kiểm được.', '2026-11-23', '2026-12-15', 'accept', 'Quá hạn ⇒ giữ nguyên launchpad-first và ghi vào whitepaper rằng dịch vụ kiểm định là nguồn thu giai đoạn 2 — tức chấp nhận rủi ro Cold-Start 3 bên đã nêu ở §8.', 'docs/WHITEPAPER.md §3 hoặc §5.4 có câu trả lời rõ cho thứ tự sản phẩm, HOẶC docs/41 được đánh dấu ACCEPTED với lý do giữ nguyên', 'OPEN', null, null),
  ('P9', 'Tách `Trust Stamp` (miễn phí) khỏi báo cáo chẩn đoán (bán) thành HAI mục doanh thu riêng', 'docs/41-testing-is-the-product.md', $q$§5.4 nguồn thu #5 ('gói phân tích playtest cho studio') ĐÃ là issuer-pays nhưng chưa gọi tên. Không tách thì điểm Arena là thứ mua được, và mô hình chết về uy tín (Moody's 2008).$q$, 'LXK', false, 'Tách hai sản phẩm ⇒ đổi §5.4 whitepaper ⇒ rebuild PDF + deck. Cần người quyết nội dung.', '2026-11-23', '2026-12-15', 'revert', 'Quá hạn ⇒ giữ nguyên một nguồn thu và ghi rõ trong whitepaper rằng điểm công khai LÀ thứ studio trả tiền để có.', $q$docs/WHITEPAPER.md §5.4 có hai mục riêng, một mục ghi rõ 'không bán'$q$, 'OPEN', null, null),
  ('P10', $q$Cổng canh 'điểm công khai không phải thứ mua được'$q$, 'docs/41-testing-is-the-product.md', 'Ràng buộc đạo đức của mô hình (§2) chỉ có giá trị nếu máy làm nó ĐỎ được. Hiện chỉ là văn xuôi.', 'AGENT', true, 'Kiểm được bằng máy: nếu §5.4 tách hai mục (P9), cổng đọc được chúng; trước đó chưa có gì để canh.', '2026-12-15', '2026-12-22', 'remove', $q$Quá hạn ⇒ gỡ câu 'điểm công khai không mua được' khỏi docs/41 — câu không có cổng là câu hứa.$q$, 'một script trong scripts/ đỏ khi nguồn thu có doanh thu gắn với điểm công khai', 'OPEN', null, null),
  ('P11', 'Kiểm lại điều kiện dừng `500 người chơi thật/tuần` theo kết luận docs/41 §5', 'docs/41-testing-is-the-product.md', '§5 chỉ ra 30 người chấm ĐÚNG đã đủ cho một phán quyết thống kê. Con số 500 đúng nếu launchpad là sản phẩm đầu, sai nếu sản phẩm đầu là dịch vụ kiểm định.', 'LXK', false, 'Đây là điều kiện dừng ĐÃ CÔNG BỐ trong whitepaper §4/§8. Agent không được tự đổi điều kiện dừng của người.', '2026-11-23', '2026-12-15', 'accept', 'Quá hạn ⇒ giữ 500 và ghi rõ nó là điều kiện cho LAUNCHPAD, không phải cho dịch vụ kiểm định.', 'docs/WHITEPAPER.md §4 hoặc §8 có câu nói rõ 500 áp cho sản phẩm nào', 'OPEN', null, null),
  ('P12', 'Cam kết ngày cho 6 việc docs/23 §9 (KOL wave) — chúng có lý do chặn nhưng KHÔNG có hạn', 'docs/23-dino-race-starter-kit.md', $q$Sáu việc đã được viết là 'phải làm trước làn sóng KOL' nhưng không có người và ngày — đúng định nghĩa 'một mong muốn' của docs/37. docs/23 §9 tự nói cả sáu đã có trong docs/17.$q$, 'LXK', false, 'Cần người chọn ngày và thứ tự; agent không được tự đặt hạn cho việc của người.', '2026-11-23', '2026-12-20', 'accept', $q$Quá hạn ⇒ gỡ câu 'phải làm trước làn sóng KOL' khỏi docs/23 §9 vì không có ngày thì không có 'trước'.$q$, $q$mỗi việc trong 6 việc có một mục P-id riêng với due, hoặc câu 'trước làn sóng KOL' bị gỡ$q$, 'OPEN', null, null)
on conflict (id) do update set title = excluded.title, due = excluded.due, status = excluded.status, done_on = excluded.done_on, evidence = excluded.evidence;

insert into pm_action_deps (action_id, blocked_by, note) values
  ('P1', 'P8', 'Ràng buộc biên S_LP thuộc hồ sơ đường cong; nếu P8 chọn dịch-vụ-kiểm-định-first thì thứ tự sửa spec đổi'),
  ('P9', 'P8', 'Không tách được trước khi P8 chọn thứ tự sản phẩm'),
  ('P10', 'P9', 'Viết cổng trước khi tách hai sản phẩm là canh một thứ không tồn tại (docs/41 §7)'),
  ('P11', 'P8', 'Không trả lời được khi chưa chọn thứ tự sản phẩm')
on conflict (action_id, blocked_by) do update set note = excluded.note;

insert into pm_action_stakeholders (action_id, person_code) values
  ('P1', 'LXK'),
  ('P2', 'LXK'),
  ('P3', 'AGENT'),
  ('P4', 'AGENT'),
  ('P5', 'AGENT'),
  ('P6', 'AGENT'),
  ('P7', 'AGENT'),
  ('P8', 'LXK'),
  ('P9', 'LXK'),
  ('P10', 'AGENT'),
  ('P11', 'LXK'),
  ('P12', 'LXK')
on conflict do nothing;

commit;
