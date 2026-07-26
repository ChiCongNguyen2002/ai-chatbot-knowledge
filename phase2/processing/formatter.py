"""Response formatter - cấu trúc output rõ ràng và chuyên nghiệp"""

from typing import Dict, List


class ResponseFormatter:
    """Format RAG output với cấu trúc chuẩn, dễ đọc"""

    @staticmethod
    def format_technical_answer(answer: str, sources: List[Dict], intent: str) -> str:
        """Format câu trả lời kỹ thuật"""
        
        # Detect type based on content
        if '|' in answer and 'Khía cạnh' in answer:  # Comparison table
            return ResponseFormatter._format_comparison(answer, sources)
        elif '✅' in answer or '❌' in answer:  # Pro/con list
            return ResponseFormatter._format_list(answer, sources)
        elif '\n•' in answer:  # Bullet points
            return ResponseFormatter._format_bullets(answer, sources)
        else:
            return ResponseFormatter._format_paragraph(answer, sources)

    @staticmethod
    def _format_comparison(content: str, sources: List[Dict]) -> str:
        """Format bảng so sánh"""
        lines = content.split('\n')
        
        result = []
        result.append("📊 **SO SÁNH CHI TIẾT**\n")
        
        # Extract table
        in_table = False
        for line in lines:
            if '|' in line:
                if not in_table:
                    result.append("```")
                    in_table = True
                result.append(line)
            elif in_table and line.strip():
                result.append("```\n")
                in_table = False
                result.append(line)
        
        if in_table:
            result.append("```")
        
        # Add sources
        result.append(ResponseFormatter._format_sources_compact(sources))
        
        return '\n'.join(result)

    @staticmethod
    def _format_list(content: str, sources: List[Dict]) -> str:
        """Format danh sách ưu/nhược điểm"""
        lines = content.split('\n')
        
        result = []
        result.append("**PHÂN TÍCH CHI TIẾT**\n")
        
        for line in lines:
            if line.strip().startswith('✅') or line.strip().startswith('❌'):
                # Add emoji spacing
                result.append(f"  {line.strip()}")
            elif line.strip():
                result.append(f"  {line.strip()}")
        
        result.append("")
        result.append(ResponseFormatter._format_sources_compact(sources))
        
        return '\n'.join(result)

    @staticmethod
    def _format_bullets(content: str, sources: List[Dict]) -> str:
        """Format bullet points"""
        lines = content.split('\n')
        
        result = []
        result.append("**THÔNG TIN CHÍNH**\n")
        
        for line in lines:
            if line.strip().startswith('•'):
                result.append(f"  {line.strip()}")
            elif line.strip() and ':' in line:
                # Highlight key/value
                key, val = line.split(':', 1)
                result.append(f"  **{key.strip()}:** {val.strip()}")
            elif line.strip():
                result.append(f"  {line.strip()}")
        
        result.append("")
        result.append(ResponseFormatter._format_sources_compact(sources))
        
        return '\n'.join(result)

    @staticmethod
    def _format_paragraph(content: str, sources: List[Dict]) -> str:
        """Format đoạn văn thường"""
        result = []
        
        # Split into paragraphs
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                result.append(para.strip())
                result.append("")
        
        result.append(ResponseFormatter._format_sources_compact(sources))
        
        return '\n'.join(result)

    @staticmethod
    def _format_sources_compact(sources: List[Dict]) -> str:
        """Format sources compactly"""
        if not sources:
            return ""
        
        result = []
        result.append("**📚 NGUỒN TÀI LIỆU**")
        
        for i, src in enumerate(sources[:3], 1):
            title = src.get('title', 'Unknown')
            score = src.get('score', 0)
            result.append(f"  [{i}] {title} ({score:.0%})")
        
        return '\n'.join(result)

    @staticmethod
    def format_greeting() -> str:
        """Format lời chào"""
        return "👋 Xin chào! Tôi là AI Assistant của Anfin. Bạn muốn hỏi gì về kiến thức công nghệ?"

    @staticmethod
    def format_error() -> str:
        """Format lỗi"""
        return "⚠️ Xin lỗi, tôi chưa tìm thấy thông tin liên quan. Hãy thử hỏi về:\n• Microservices\n• Docker/Kubernetes\n• API Design\n• Testing\n• DevOps\n• Security"
