# K4 — Ngày 1: Bài Tập & Phản Ánh
## Khám Phá LLM API | Phiếu Thực Hành

**Thời lượng:** 4 tiếng
**Cách làm:** Trả lời từng câu ngay sau khi hoàn thành block tương ứng —
đừng để dồn hết về cuối buổi. Thay dòng `*Câu trả lời của bạn*` bằng câu
trả lời thật (chấm tự động sẽ đếm số câu đã trả lời).

---

## Block 1 — API Cơ Bản (trả lời sau Checkpoint 1)

### Câu 1.1 — Độ nhạy của temperature
Gọi `call_openai` với temperature 0.0, 0.5, 1.0 và 1.5 dùng prompt
**"Hãy kể cho tôi một sự thật thú vị về Việt Nam."**

**Bạn nhận thấy quy luật gì qua bốn phản hồi?** (2–3 câu)
> Ở temperature 0.0, câu trả lời đi thẳng vào một thông tin cụ thể về hang Sơn Đoòng, ít diễn giải thêm. Khi tăng temperature, model có nhiều khả năng chọn cách diễn đạt hoặc chi tiết khác cho cùng một câu hỏi; sự thay đổi không theo một đường thẳng vì mỗi lần gọi vẫn có yếu tố lấy mẫu. Vì vậy temperature thấp hợp với câu trả lời cần ổn định, còn temperature cao hơn phù hợp khi muốn có thêm phương án diễn đạt.

### Câu 1.2 — Chọn temperature cho sản phẩm
**Bạn sẽ đặt temperature bao nhiêu cho chatbot hỗ trợ khách hàng, và tại sao?**
> Em sẽ đặt khoảng 0.2–0.3. Chatbot hỗ trợ khách hàng cần trả lời nhất quán, không tự bịa thêm chính sách hay đưa ra các cách xử lý quá khác nhau cho cùng một tình huống. Mức này vẫn đủ tự nhiên khi viết tiếng Việt.

### Câu 1.3 — Đánh đổi chi phí
Kịch bản: 10.000 người dùng hoạt động mỗi ngày, mỗi người gọi API 3 lần,
mỗi lần trung bình ~350 token đầu ra.

**Ước tính GPT-4o đắt hơn GPT-4o-mini bao nhiêu lần cho workload này? Nêu một
trường hợp GPT-4o xứng đáng với chi phí và một trường hợp nên dùng mini:**
> Tổng output là 10.000 × 3 × 350 = 10,5 triệu token mỗi ngày. Với giá output trong bài, GPT-4o tốn khoảng 105 USD/ngày, còn GPT-4o-mini khoảng 6,3 USD/ngày, tức GPT-4o đắt hơn khoảng 16,7 lần. GPT-4o đáng dùng khi cần phân tích tài liệu khó hoặc xử lý tình huống có rủi ro cao; mini hợp với FAQ, phân loại yêu cầu và các câu trả lời lặp lại với số lượng lớn.

---

## Block 2 — System Prompt & Token (trả lời sau Checkpoint 2)

### Câu 2.1 — Sức mạnh của persona
Gọi `chat_with_system_prompt` hai lần với cùng câu hỏi
**"Giải thích blockchain là gì?"** nhưng hai system prompt khác nhau:
- "Bạn là giáo viên tiểu học, giải thích thật đơn giản cho trẻ 8 tuổi."
- "Bạn là chuyên gia tài chính, trả lời chuyên sâu bằng thuật ngữ kỹ thuật."

**Hai phản hồi khác nhau như thế nào (độ dài, từ vựng, ví dụ)? System prompt
ảnh hưởng đến hành vi model ra sao?** (3–4 câu)
> Persona giáo viên tiểu học dùng hình ảnh “cuốn sổ ghi chép đặc biệt”, câu ngắn và ví dụ lớp học nên dễ hình dung hơn. Persona chuyên gia tài chính mở đầu bằng “cơ sở dữ liệu phân tán”, “mã hóa” và “đồng thuận”, vì thế dày thuật ngữ hơn và hướng đến cơ chế vận hành. Cùng một model nhưng system prompt đã đổi đối tượng người đọc, cách chọn từ và mức độ chi tiết của câu trả lời.

### Câu 2.2 — tiktoken vs đếm từ
Chọn một đoạn văn tiếng Việt ~100 từ. So sánh số token theo `count_tokens`
(tiktoken) với ước lượng `số từ / 0.75` mà Part 1 đã dùng.

**Hai con số chênh nhau bao nhiêu phần trăm? Vì sao tiếng Việt thường tốn
nhiều token hơn tiếng Anh cùng độ dài?**
> Với đoạn văn 97 từ tiếng Việt, `count_tokens` cho 105 token; ước lượng `số từ / 0.75` cho 129,3 token. Hai số lệch khoảng 18,8%, cho thấy công thức theo số từ chỉ nên dùng để ước tính nhanh. Tiếng Việt thường có nhiều tiếng tách bằng dấu cách và có dấu; tokenizer có thể tách chúng khác tiếng Anh, nên cùng một ý tiếng Việt thường không có tỷ lệ từ/token cố định.

---

## Block 3 — Streaming & Độ Bền (trả lời sau Checkpoint 3)

### Câu 3.1 — Trải nghiệm người dùng với streaming
**Streaming quan trọng nhất trong trường hợp nào, và khi nào thì
non-streaming lại phù hợp hơn?** (1 đoạn văn)
> Streaming quan trọng khi câu trả lời dài hoặc người dùng đang chờ trước màn hình, ví dụ chatbot tư vấn hay trợ lý soạn nội dung. Chữ xuất hiện sớm giúp người dùng biết hệ thống đang làm việc và có thể dừng nếu câu trả lời đi sai hướng. Non-streaming phù hợp với tác vụ ngắn cần nhận một kết quả hoàn chỉnh để xử lý tiếp, như phân loại, trích xuất JSON hoặc chạy ở nền.

### Câu 3.2 — Vì sao backoff theo cấp số nhân?
**So với delay cố định (ví dụ luôn chờ 1 giây), exponential backoff có lợi
thế gì khi API bị quá tải? Điều gì xảy ra nếu hàng nghìn client cùng retry
với delay cố định giống nhau?**
> Exponential backoff tạo khoảng nghỉ ngày càng dài: lần đầu thử lại nhanh, nhưng nếu dịch vụ vẫn quá tải thì client giảm áp lực thay vì liên tục gửi thêm request. Nếu hàng nghìn client đều chờ cố định 1 giây, họ sẽ cùng quay lại gần như một lúc và tạo thêm một đợt quá tải mới. Trong thực tế có thể cộng thêm jitter ngẫu nhiên để các lần retry lệch nhau hơn.

---

## Block 4 — Mini-Project (trả lời sau Checkpoint 4)

### Câu 4.1 — Thiết kế persona
**Bạn chọn persona gì cho trợ lý của mình? Viết lại system prompt đó và giải
thích 1–2 lựa chọn từ ngữ quan trọng trong prompt (ví dụ: vì sao yêu cầu
"trả lời ngắn gọn", vì sao chỉ định ngôn ngữ...):**
> Em chọn persona: “Bạn là trợ lý học LLM API cho người mới. Trả lời bằng tiếng Việt, giải thích theo từng bước ngắn, dùng ví dụ đơn giản và nêu rõ lệnh cần chạy khi phù hợp.” Cụm “cho người mới” buộc trợ lý tránh nhảy cóc kiến thức; “từng bước ngắn” phù hợp khi người học đang thao tác trong terminal. Yêu cầu tiếng Việt giúp câu trả lời dễ theo dõi trong lúc làm lab.

### Câu 4.2 — Hạn chế & cải thiện
**Trợ lý của bạn hiện có hạn chế lớn nhất là gì (ví dụ: history chỉ 3 lượt,
không có bộ nhớ dài hạn, không kiểm duyệt nội dung...)? Đề xuất một cải
thiện cụ thể và mô tả ngắn cách triển khai:**
> Hạn chế lớn nhất là history chỉ giữ ba lượt gần nhất, nên trợ lý dễ quên bối cảnh nếu cuộc hội thoại dài. Em sẽ thêm một phần tóm tắt ngắn cho các lượt cũ trước khi cắt history: sau vài lượt, gửi history cũ cho model để tạo summary, rồi giữ system prompt + summary + ba lượt mới nhất. Cách này tiết kiệm token hơn việc lưu toàn bộ hội thoại nhưng vẫn giữ được mục tiêu chính.

---

## Danh Sách Kiểm Tra Nộp Bài

- [ ] `python grade.py` — xem điểm tự động, mục tiêu ≥ 75/100
- [ ] Cả 4 checkpoint pytest đều pass
- [ ] Tất cả 9 câu trong file này đã được trả lời
- [ ] Đã copy bài làm vào folder `solution/`, push lên fork và dán link trên trang bài Lab ở VLearn trước 23:59 ngày 11/09/2026
