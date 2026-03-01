# ═══════════════════════════════════════════════════════════════════════════════
# TFF PERFORMANS SİSTEMİ - EXPORT ARAÇLARI
# ═══════════════════════════════════════════════════════════════════════════════

import streamlit as st
import pandas as pd
import io
import re
from datetime import datetime

class ExportManager:
    @staticmethod
    def _safe_filename(filename):
        """Dosya isimlerini güvenli hale getirir"""
        return re.sub(r'[^\w\s-]', '', filename).strip().replace(' ', '_')

    @staticmethod
    def export_figure_png(fig, filename="figure"):
        """Plotly figürü PNG olarak indir (metadata dahil)"""
        safe_fname = ExportManager._safe_filename(filename)
        try:
            img_bytes = fig.to_image(format="png", width=1400, height=700, scale=2)
            st.download_button(
                label="📷 PNG İNDİR",
                data=img_bytes,
                file_name=f"{safe_fname}_{datetime.now().strftime('%d%m%Y')}.png",
                mime="image/png",
                key=f"png_{safe_fname}"
            )
        except Exception as e:
            st.button("❌ PNG HATASI", disabled=True, key=f"png_err_{safe_fname}", 
                     help=f"Sisteminizde 'kaleido' eksik olabilir. Detay: {str(e)}")

    @staticmethod
    def export_figure_html(fig, filename="figure"):
        """Plotly figürü HTML olarak indir (interaktif)"""
        safe_fname = ExportManager._safe_filename(filename)
        try:
            html_string = fig.to_html(include_plotlyjs='cdn')
            st.download_button(
                label="🌐 İNTERAKTİF HTML",
                data=html_string,
                file_name=f"{safe_fname}_{datetime.now().strftime('%d%m%Y')}.html",
                mime="text/html",
                key=f"html_{safe_fname}"
            )
        except Exception as e:
            st.error(f"HTML export hatası: {e}")

    @staticmethod
    def export_dataframe_excel(df, filename="data"):
        """DataFrame'i Excel olarak indir"""
        safe_fname = ExportManager._safe_filename(filename)
        try:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Veri', index=False)
                
                # Excel formatlaması
                worksheet = writer.sheets['Veri']
                for idx, col in enumerate(df.columns, 1):
                    worksheet.column_dimensions[chr(64 + idx)].width = 15
            
            buffer.seek(0)
            st.download_button(
                label="📊 EXCEL İNDİR",
                data=buffer.getvalue(),
                file_name=f"{safe_fname}_{datetime.now().strftime('%d%m%Y')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"excel_{safe_fname}"
            )
        except Exception as e:
            st.error(f"Excel export hatası: {e}")

    @staticmethod
    def export_dataframe_csv(df, filename="data"):
        """DataFrame'i CSV olarak indir"""
        safe_fname = ExportManager._safe_filename(filename)
        try:
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📝 CSV İNDİR",
                data=csv,
                file_name=f"{safe_fname}_{datetime.now().strftime('%d%m%Y')}.csv",
                mime="text/csv",
                key=f"csv_{safe_fname}"
            )
        except Exception as e:
            st.error(f"CSV export hatası: {e}")

export_manager = ExportManager()

print("✅ Export Araçları Yüklendi | PNG, HTML, Excel Support")
