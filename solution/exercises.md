# K4 — Ngày 1: Bài Tập & Phản Ánh

### Câu 1.1 — Độ nhạy của temperature

> Ở temperature 0.0, câu trả lời đi thẳng vào một thông tin cụ thể về hang Sơn Đoòng. Khi tăng temperature, model có nhiều khả năng chọn cách diễn đạt hoặc chi tiết khác cho cùng một câu hỏi; temperature thấp hợp với câu trả lời cần ổn định, còn temperature cao hơn hợp khi muốn có thêm phương án diễn đạt.

### Câu 1.2 — Chọn temperature cho sản phẩm

> Em sẽ đặt khoảng 0.2–0.3. Chatbot hỗ trợ khách hàng cần trả lời nhất quán, không tự bịa thêm chính sách, nhưng mức này vẫn đủ tự nhiên khi viết tiếng Việt.

### Câu 1.3 — Đánh đổi chi phí

> Tổng output là 10,5 triệu token/ngày. GPT-4o tốn khoảng 105 USD/ngày, còn GPT-4o-mini khoảng 6,3 USD/ngày, nên GPT-4o đắt hơn khoảng 16,7 lần. GPT-4o hợp với phân tích tài liệu khó; mini hợp với FAQ và phân loại yêu cầu số lượng lớn.

### Câu 2.1 — Sức mạnh của persona

> Persona giáo viên dùng hình ảnh “cuốn sổ ghi chép đặc biệt”, câu ngắn và ví dụ lớp học. Persona chuyên gia dùng các từ “cơ sở dữ liệu phân tán”, “mã hóa” và “đồng thuận”, nên dày thuật ngữ hơn. System prompt đã đổi đối tượng người đọc, cách chọn từ và mức độ chi tiết của câu trả lời.

### Câu 2.2 — tiktoken vs đếm từ

> Với đoạn văn 97 từ tiếng Việt, `count_tokens` cho 105 token; ước lượng `số từ / 0.75` cho 129,3 token, lệch khoảng 18,8%. Công thức theo số từ chỉ nên dùng để ước tính nhanh vì tokenizer có thể tách tiếng Việt có dấu khác tiếng Anh.

### Câu 3.1 — Trải nghiệm người dùng với streaming

> Streaming quan trọng khi câu trả lời dài hoặc người dùng đang chờ trước màn hình. Chữ xuất hiện sớm giúp họ biết hệ thống đang làm việc và có thể dừng nếu câu trả lời đi sai hướng. Non-streaming hợp với tác vụ cần một kết quả hoàn chỉnh như phân loại hoặc trích xuất JSON.

### Câu 3.2 — Vì sao backoff theo cấp số nhân?

> Exponential backoff tạo khoảng nghỉ ngày càng dài, giảm áp lực lên dịch vụ đang quá tải. Nếu hàng nghìn client cùng chờ cố định 1 giây, họ sẽ cùng quay lại và tạo thêm một đợt quá tải mới. Có thể cộng jitter ngẫu nhiên để các lần retry lệch nhau hơn.

### Câu 4.1 — Thiết kế persona

> Persona: “Bạn là trợ lý học LLM API cho người mới. Trả lời bằng tiếng Việt, giải thích theo từng bước ngắn, dùng ví dụ đơn giản và nêu rõ lệnh cần chạy khi phù hợp.” Cụm “cho người mới” giúp trợ lý không nhảy cóc kiến thức; “từng bước ngắn” phù hợp khi thao tác trong terminal.

### Câu 4.2 — Hạn chế & cải thiện

> Hạn chế lớn nhất là history chỉ giữ ba lượt gần nhất, nên trợ lý dễ quên bối cảnh. Em sẽ tóm tắt các lượt cũ trước khi cắt history, rồi giữ system prompt, phần tóm tắt và ba lượt mới nhất. Cách này tiết kiệm token hơn lưu toàn bộ hội thoại mà vẫn giữ được mục tiêu chính.
