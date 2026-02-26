import streamlit as st
from pypdf import PdfWriter, PdfReader
import io
import fitz  # PyMuPDF (for compress)

st.set_page_config(page_title="QuickPDF", page_icon="📄", layout="centered")

# -------------------- LANGUAGE --------------------
lang = st.radio("Language / 语言", ["English", "中文"], horizontal=True)

def t(en, zh):
    return zh if lang == "中文" else en

# （可选）把 uploader 的英文提示“视觉上换成中文”
if lang == "中文":
    st.markdown("""
    <style>
    /* Hide default English hint inside uploader */
    [data-testid="stFileUploaderDropzone"] div div div p {
        display: none;
    }
    /* Show Chinese hint */
    [data-testid="stFileUploaderDropzone"] div div div::before {
        content: "拖拽 PDF 到这里，或点击右侧按钮选择文件";
        font-size: 16px;
        font-weight: 600;
        opacity: 0.85;
    }
    </style>
    """, unsafe_allow_html=True)

st.title(t("📄 My PDF Tool", "📄 我的 PDF 工具"))

tool = st.selectbox(
    t("Choose a tool", "选择功能"),
    [t("Merge", "合并"), t("Rotate", "旋转"), t("Split", "分割"), t("Compress", "压缩"), t("Extract", "提取单页")]
)

# Keep internal tool keys stable
tool_key = {
    "Merge": "Merge", "合并": "Merge",
    "Rotate": "Rotate", "旋转": "Rotate",
    "Split": "Split", "分割": "Split",
    "Compress": "Compress", "压缩": "Compress",
    "Extract": "Extract", "提取单页": "Extract",
}[tool]

# -------------------- MERGE --------------------
if tool_key == "Merge":
    uploaded_files = st.file_uploader(
        t("Upload PDFs (2 or more)", "上传多个 PDF（至少 2 个）"),
        type=["pdf"],
        accept_multiple_files=True
    )

    if st.button(t("Merge", "合并"), type="primary", disabled=not uploaded_files or len(uploaded_files) < 2):
        writer = PdfWriter()

        names = []
        for f in uploaded_files:
            writer.append(f)
            base = f.name
            if base.lower().endswith(".pdf"):
                base = base[:-4]
            base = base.replace(" ", "_")
            names.append(base)

        base_name = "_".join(names[:3])
        if len(names) > 3:
            base_name += "_etc"

        output_name = f"{base_name}_{t('merged','合并')}.pdf"

        buffer = io.BytesIO()
        writer.write(buffer)
        buffer.seek(0)

        st.success(t("Done!", "完成！"))
        safe_label = output_name.replace("_", "\\_")

        st.download_button(
            t(f"Download {safe_label}", f"下载 {safe_label}"),
            data=buffer,
            file_name=output_name,
            mime="application/pdf"
        )

# -------------------- ROTATE --------------------
elif tool_key == "Rotate":
    uploaded_file = st.file_uploader(
        t("Upload ONE PDF", "上传一个 PDF"),
        type=["pdf"],
        accept_multiple_files=False
    )
    angle = st.selectbox(
        t("Rotate all pages by", "所有页面旋转角度"),
        [90, 180, 270],
        index=0
    )

    if st.button(t("Rotate", "旋转"), type="primary", disabled=not uploaded_file):
        reader = PdfReader(uploaded_file)
        writer = PdfWriter()

        for page in reader.pages:
            page.rotate(angle)
            writer.add_page(page)

        name = uploaded_file.name
        if name.lower().endswith(".pdf"):
            name = name[:-4]
        name = name.replace(" ", "_")

        output_name = f"{name}_{t('rotated','旋转')}_{angle}.pdf"

        buffer = io.BytesIO()
        writer.write(buffer)
        buffer.seek(0)

        st.success(t("Done!", "完成！"))
        st.download_button(
            t(f"Download {output_name.replace('_','\\_')}", f"下载 {output_name.replace('_','\\_')}"),
            data=buffer,
            file_name=output_name,
            mime="application/pdf"
        )

# -------------------- SPLIT --------------------
elif tool_key == "Split":
    uploaded_file = st.file_uploader(
        t("Upload ONE PDF", "上传一个 PDF"),
        type=["pdf"],
        accept_multiple_files=False
    )

    if uploaded_file:
        reader = PdfReader(uploaded_file)
        total_pages = len(reader.pages)

        if total_pages < 2:
            st.info(t("This PDF has only 1 page, nothing to split.",
                      "这个 PDF 只有 1 页，无法分割。"))
        else:
            split_at = st.number_input(
                t(f"Split at page (1 to {total_pages - 1})", f"在第几页分割（1 到 {total_pages - 1}）"),
                min_value=1,
                max_value=total_pages - 1,
                value=1,
                step=1
            )

            if st.button(t("Split", "分割"), type="primary"):
                w1, w2 = PdfWriter(), PdfWriter()

                for i, p in enumerate(reader.pages):
                    if i < split_at:
                        w1.add_page(p)
                    else:
                        w2.add_page(p)

                name = uploaded_file.name
                if name.lower().endswith(".pdf"):
                    name = name[:-4]
                name = name.replace(" ", "_")

                part1_name = f"{name}_{t('part','部分')}1.pdf"
                part2_name = f"{name}_{t('part','部分')}2.pdf"

                b1, b2 = io.BytesIO(), io.BytesIO()
                w1.write(b1); w2.write(b2)
                b1.seek(0); b2.seek(0)

                st.success(t("Done!", "完成！"))
                c1, c2 = st.columns(2)

                with c1:
                    st.download_button(
                        t(f"Download {part1_name.replace('_','\\_')}", f"下载 {part1_name.replace('_','\\_')}"),
                        b1,
                        part1_name,
                        "application/pdf"
                    )

                with c2:
                    st.download_button(
                        t(f"Download {part2_name.replace('_','\\_')}", f"下载 {part2_name.replace('_','\\_')}"),
                        b2,
                        part2_name,
                        "application/pdf"
                    )

# -------------------- COMPRESS --------------------
elif tool_key == "Compress":
    uploaded_file = st.file_uploader(
        t("Upload ONE PDF", "上传一个 PDF"),
        type=["pdf"],
        accept_multiple_files=False
    )
    st.caption(t("Tip: Compression depends on the PDF content (scans/images compress better).",
                 "提示：压缩效果取决于 PDF 内容（扫描件/图片多的通常更明显）。"))

    if st.button(t("Compress", "压缩"), type="primary", disabled=not uploaded_file):
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        out = io.BytesIO()
        doc.save(out, garbage=4, deflate=True)
        out.seek(0)

        name = uploaded_file.name
        if name.lower().endswith(".pdf"):
            name = name[:-4]
        name = name.replace(" ", "_")

        output_name = f"{name}_{t('compressed','压缩')}.pdf"

        st.success(t("Done!", "完成！"))
        st.download_button(
            t(f"Download {output_name.replace('_','\\_')}", f"下载 {output_name.replace('_','\\_')}"),
            data=out,
            file_name=output_name,
            mime="application/pdf"
        )

# -------------------- EXTRACT (ONE PAGE) --------------------
elif tool_key == "Extract":
    uploaded_file = st.file_uploader(
        t("Upload ONE PDF", "上传一个 PDF"),
        type=["pdf"],
        accept_multiple_files=False
    )

    if uploaded_file:
        reader = PdfReader(uploaded_file)
        total_pages = len(reader.pages)

        page_num = st.number_input(
            t(f"Extract page (1 to {total_pages})", f"提取第几页（1 到 {total_pages}）"),
            min_value=1,
            max_value=total_pages,
            value=1,
            step=1
        )

        if st.button(t("Extract", "提取"), type="primary"):
            writer = PdfWriter()
            writer.add_page(reader.pages[int(page_num) - 1])

            name = uploaded_file.name
            if name.lower().endswith(".pdf"):
                name = name[:-4]
            name = name.replace(" ", "_")

            output_name = f"{name}_{t('page','页')}{int(page_num)}.pdf"

            buffer = io.BytesIO()
            writer.write(buffer)
            buffer.seek(0)

            st.success(t("Done!", "完成！"))
            st.download_button(
                t(f"Download {output_name.replace('_','\\_')}", f"下载 {output_name.replace('_','\\_')}"),
                data=buffer,
                file_name=output_name,
                mime="application/pdf"
            )

st.markdown("---")
st.caption(t("🔒 Files are processed in memory and not stored.",
             "🔒 文件仅在内存中处理，不会被保存。"))
