import streamlit as st
from pypdf import PdfWriter, PdfReader
import io
import fitz  # PyMuPDF (for compress)

st.set_page_config(page_title="My PDF Tool", page_icon="📄", layout="centered")
st.title("📄 My PDF Tool")

tool = st.selectbox("Choose a tool", ["Merge", "Rotate", "Split", "Compress"])

# -------------------- MERGE --------------------
if tool == "Merge":
    uploaded_files = st.file_uploader("Upload PDFs (2 or more)", type=["pdf"], accept_multiple_files=True)

    if st.button("Merge", type="primary", disabled=not uploaded_files or len(uploaded_files) < 2):
        writer = PdfWriter()

        # 1) 收集输入文件名（去掉 .pdf，并做简单清理）
        names = []
        for f in uploaded_files:
            writer.append(f)
            base = f.name
            if base.lower().endswith(".pdf"):
                base = base[:-4]
            base = base.replace(" ", "_")
            names.append(base)

        # 2) 生成输出文件名（最多取前3个，避免太长）
        base_name = "_".join(names[:3])
        if len(names) > 3:
            base_name += "_etc"

        output_name = f"{base_name}_merged.pdf"

        # 3) 写入内存并下载
        buffer = io.BytesIO()
        writer.write(buffer)
        buffer.seek(0)

        st.success("Done!")
        safe_name = output_name.replace("_", "\\_")

        st.download_button(
        f"Download {safe_name}",
        data=buffer,
        file_name=output_name,
        mime="application/pdf"
        )

# -------------------- ROTATE --------------------
elif tool == "Rotate":
    uploaded_file = st.file_uploader("Upload ONE PDF", type=["pdf"], accept_multiple_files=False)
    angle = st.selectbox("Rotate all pages by", [90, 180, 270], index=0)

    if st.button("Rotate", type="primary", disabled=not uploaded_file):
        reader = PdfReader(uploaded_file)
        writer = PdfWriter()

        for page in reader.pages:
            page.rotate(angle)
            writer.add_page(page)

        # 👉 生成文件名
        name = uploaded_file.name
        if name.lower().endswith(".pdf"):
            name = name[:-4]
        name = name.replace(" ", "_")

        output_name = f"{name}_rotated.pdf"

        buffer = io.BytesIO()
        writer.write(buffer)
        buffer.seek(0)

        st.success("Done!")
        st.download_button(
            f"Download {output_name.replace('_','\\_')}",
            data=buffer,
            file_name=output_name,
            mime="application/pdf"
        )
# -------------------- SPLIT --------------------
elif tool == "Split":
    uploaded_file = st.file_uploader("Upload ONE PDF", type=["pdf"], accept_multiple_files=False)

    if uploaded_file:
        reader = PdfReader(uploaded_file)
        total_pages = len(reader.pages)

        if total_pages < 2:
            st.info("This PDF has only 1 page, nothing to split.")
        else:
            split_at = st.number_input(
                f"Split at page (1 to {total_pages - 1})",
                min_value=1,
                max_value=total_pages - 1,
                value=1,
                step=1
            )

            if st.button("Split", type="primary"):
                w1, w2 = PdfWriter(), PdfWriter()

                for i, p in enumerate(reader.pages):
                    if i < split_at:
                        w1.add_page(p)
                    else:
                        w2.add_page(p)

                # 👉 生成文件名
                name = uploaded_file.name
                if name.lower().endswith(".pdf"):
                    name = name[:-4]
                name = name.replace(" ", "_")

                part1_name = f"{name}_part1.pdf"
                part2_name = f"{name}_part2.pdf"

                b1, b2 = io.BytesIO(), io.BytesIO()
                w1.write(b1); w2.write(b2)
                b1.seek(0); b2.seek(0)

                st.success("Done!")
                c1, c2 = st.columns(2)

                with c1:
                    st.download_button(
                        f"Download {part1_name.replace('_','\\_')}",
                        b1,
                        part1_name,
                        "application/pdf"
                    )

                with c2:
                    st.download_button(
                        f"Download {part2_name.replace('_','\\_')}",
                        b2,
                        part2_name,
                        "application/pdf"
                    )

# -------------------- COMPRESS --------------------
elif tool == "Compress":
    uploaded_file = st.file_uploader("Upload ONE PDF", type=["pdf"], accept_multiple_files=False)
    st.caption("Tip: compression效果跟PDF内容有关（扫描件/大图通常更明显）。")

    if st.button("Compress", type="primary", disabled=not uploaded_file):
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        out = io.BytesIO()
        doc.save(out, garbage=4, deflate=True)
        out.seek(0)

        # 👉 生成文件名
        name = uploaded_file.name
        if name.lower().endswith(".pdf"):
            name = name[:-4]
        name = name.replace(" ", "_")

        output_name = f"{name}_compressed.pdf"

        st.success("Done!")
        st.download_button(
            f"Download {output_name.replace('_','\\_')}",
            data=out,
            file_name=output_name,
            mime="application/pdf"
        )

st.markdown("---")
st.caption("🔒 Files are processed in memory and not stored.")
