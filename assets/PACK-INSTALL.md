# 📦 Prompt-Library README Visual Pack

Bộ asset để visualize dự án **prompt-library** trên profile README của bạn
(`github.com/lhlhai/lhlhai`). Tải zip này về, giải nén, dùng — không cần commit vào repo prompt-library.

## Chứa gì?

| File | Dùng để làm gì |
|---|---|
| `readme-banner.svg` | Banner hero 1200x360, dark glassmorphism đồng bộ theme trang web |
| `prompt-map.svg` | Biểu đồ phân bố categories/pages (tái tạo bằng script) |
| `PROMPT-LIBRARY-SECTION.md` | **Đoạn Markdown cắt-dán thẳng vào profile README** (kèm badge Shields.io động) |
| `README-BADGES.md` | Tham khảo: mọi biến thể badge + cách đổi màu/số đo |
| `generate-readme-badges.py` | Script đếm prompts/categories thật từ `prompts.js`, vẽ lại SVG + sinh badge |
| `readme-badges.yml` | GitHub Action chạy script tự động mỗi tuần / mỗi lần repo thay đổi |

## Cách dùng nhanh (5 phút)

### 1. Upload SVG lên repo profile

```bash
# Trong repo profile của bạn (lhlhai/lhlhai)
mkdir -p assets
cp readme-banner.svg prompt-map.svg assets/
git add assets && git commit -m "Add prompt-library visuals" && git push
```

Hoặc kéo-thả trực tiếp vào tab **Add file -> Upload files** trên GitHub.

### 2. Dán section vào README

Mở `PROMPT-LIBRARY-SECTION.md`, copy toàn bộ nội dung, dán vào profile README
(gợi ý: giữa phần `About Me` và `🐍 Commit`). Sửa đường dẫn ảnh nếu bạn đặt
SVG ở folder khác, ví dụ:

```md
![Prompt Library banner](./assets/readme-banner.svg)
```

> 💡 Badge dạng `shields.io` dùng `/count/...` sẽ tự hiện số **đang chạy**,
> không cần cập nhật thủ công.

### 3. (Tuỳ chọn) Tự động hoá số liệu

Nếu muốn SVG & badge luôn phản ánh đúng số prompts thật:

1. Copy `generate-readme-badges.py` vào repo **prompt-library** tại `scripts/`
2. Copy `readme-badges.yml` vào `.github/workflows/`
3. Cấp token có quyền ghi repo profile (fine-grained PAT làm secret, hoặc
   bật allowlist cross-repo cho `GITHUB_TOKEN`).

Script đếm `PROMPTS.length`, số category, số page HTML rồi render lại 2 file
SVG và block badge trong `assets/PROMPT-LIBRARY-SECTION.md`.

### 4. Chạy local để thử

```bash
python3 generate-readme-badges.py --repo ../prompt-library --out ./preview
open preview/readme-banner.svg
```

Cần Python >= 3.9, không cần thư viện ngoài.

## Mẹo hiển thị đẹp hơn

- Bọc banner trong `<picture>` nếu sau này bạn làm thêm bản light theme.
- Muốn banner "sống": thay bằng GIF/MP4 preview quay màn hình trang chủ
  `https://lhlhai.github.io/prompt-library/`.
- Nếu ảnh không hiện: chắc chắn URL là raw path trong repo profile
  (`./assets/...`) chứ không phải link localhost.

Chúc khoe dự án tâm huyết thành công 🎉
