from langchain_chroma import Chroma
from langchain_core.documents import Document
from typing import List, Dict, Any, Optional
import os
import re
from myEmbedding import MyEmbeddingFunction

class LatexProcessor:
    def __init__(self, pathToDB:str):

        self.collection = Chroma(collection_name="structured_latex_rag",
                                 embedding_function=MyEmbeddingFunction,
                                 persist_directory=pathToDB)

    def extract_latex_structures(self, content: str) -> Dict[str, Any]:
        """Извлекает различные структуры из LaTeX документа"""
        structures = {
            "sections": self.extract_sections(content),
            "equations": self.extract_equations(content),
            "theorems": self.extract_theorems(content),
            "tables": self.extract_tables(content),
            "plain_text": self.extract_plain_text(content)
        }
        return structures

    def extract_tables(self, content: str) -> List[Dict]:
        """
         Извлекает таблицы из LaTeX контента

         Args:
             content: Содержимое LaTeX файла

         Returns:
             List[Dict]: Список таблиц с метаданными
         """
        tables = []

        # Паттерны для различных типов таблиц
        table_patterns = [
            # Стандартное окружение table
            (r'(\\begin\{table\}.*?\\end\{table\})', 'table'),
            # Окружение tabular внутри table
            (r'(\\begin\{tabular\}.*?\\end\{tabular\})', 'tabular'),
            # Окружение longtable
            (r'(\\begin\{longtable\}.*?\\end\{longtable\})', 'longtable'),
            # Окружение tabularx
            (r'(\\begin\{tabularx\}.*?\\end\{tabularx\})', 'tabularx'),
            # Окружение tabulary
            (r'(\\begin\{tabulary\}.*?\\end\{tabulary\})', 'tabulary'),
        ]

        for pattern, table_type in table_patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                table_content = match.group(1)

                # Извлекаем дополнительные метаданные
                caption = self.extract_table_caption(table_content)
                label = self.extract_table_label(table_content)

                tables.append({
                    'content': table_content,
                    'type': table_type,
                    'caption': caption,
                    'label': label,
                    'position': self.find_table_position(content, table_content),
                    'clean_content': self.clean_table_content(table_content)
                })

        return tables


    def extract_table_caption(self, table_content: str) -> Optional[str]:
        """Извлекает заголовок таблицы"""
        caption_match = re.search(r'\\caption\{(.*?)\}', table_content, re.DOTALL)
        if caption_match:
            return caption_match.group(1).strip()
        return None


    def extract_table_label(self, table_content: str) -> Optional[str]:
        """Извлекает метку таблицы"""
        label_match = re.search(r'\\label\{(.*?)\}', table_content)
        if label_match:
            return label_match.group(1).strip()
        return None


    def find_table_position(self, full_content: str, table_content: str) -> Dict[str, int]:
        """Находит позицию таблицы в документе"""
        start_pos = full_content.find(table_content)
        end_pos = start_pos + len(table_content)

        # Находим ближайшую секцию перед таблицей
        content_before = full_content[:start_pos]
        section_match = re.findall(r'\\(section|subsection|subsubsection)\{([^}]*)\}', content_before)

        nearest_section = section_match[-1] if section_match else (None, None)

        return {
            'start': start_pos,
            'end': end_pos,
            'section_type': nearest_section[0] if nearest_section else None,
            'section_title': nearest_section[1] if nearest_section else None
        }


    def clean_table_content(self, table_content: str) -> str:
        """Очищает содержимое таблицы для лучшей читаемости"""
        # Удаляем комментарии
        cleaned = re.sub(r'%.*', '', table_content)
        # Нормализуем пробелы
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        return cleaned.strip()

    def extract_sections(self, content: str) -> List[Dict]:
        """Извлекает секции с полной разметкой"""
        sections = []
        pattern = r'(\\(section|subsection|subsubsection|paragraph)\{([^}]*)\})(.*?)(?=\\section|\\subsection|\\subsubsection|\\end{document}|$)'

        matches = re.finditer(pattern, content, re.DOTALL)
        for match in matches:
            full_command = match.group(1)
            section_type = match.group(2)
            title = match.group(3)
            section_content = match.group(4).strip()

            sections.append({
                "type": section_type,
                "title": title,
                "full_command": full_command,
                "content": section_content,
                "full_markup": full_command + "\n" + section_content
            })

        return sections

    def extract_equations(self, content: str) -> List[Dict]:
        """Извлекает уравнения с полной разметкой"""
        equations = []

        # Блочные уравнения \[ \]
        block_eqs = re.findall(r'(\\\[.*?\\\])', content, re.DOTALL)
        for eq in block_eqs:
            equations.append({"type": "block_equation", "content": eq})

        # Окружение equation
        env_eqs = re.findall(r'(\\begin\{equation\}.*?\\end\{equation\})', content, re.DOTALL)
        for eq in env_eqs:
            equations.append({"type": "equation_env", "content": eq})

        # Встроенные уравнения $ $
        inline_eqs = re.findall(r'(\$[^$]*\$)', content)
        for eq in inline_eqs:
            equations.append({"type": "inline_equation", "content": eq})

        return equations

    def extract_theorems(self, content: str) -> List[Dict]:
        """Извлекает теоремы и доказательства"""
        theorems = []
        theorem_pattern = r'(\\begin\{(theorem|lemma|corollary|proof)\}.*?\\end\{\2\})'

        matches = re.finditer(theorem_pattern, content, re.DOTALL)
        for match in matches:
            theorems.append({
                "type": match.group(2),
                "content": match.group(1)
            })

        return theorems

    def extract_plain_text(self, content: str) -> str:
        """Извлекает чистый текст для поиска"""
        # Удаляем комментарии
        text = re.sub(r'%.*', '', content)
        # Заменяем команды на их содержимое
        text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', text)
        # Заменяем уравнения на метки
        text = re.sub(r'\$[^$]*\$', '[MATH]', text)
        text = re.sub(r'\\\[.*?\\\]', '[MATH]', text)
        return text.strip()

    def add_latex_file(self, file_path: str):
        """Добавляет LaTeX файл в базу данных"""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        structures = self.extract_latex_structures(content)
        filename = os.path.basename(file_path)

        documents = []

        # Добавляем секции
        for i, section in enumerate(structures["sections"]):
            metaData = {
                "filename": filename,
                "structure_type": "section",
                "section_type": section["type"],
                "title": section["title"],
                "content_type": "latex_markup",
                "clean_text": self.extract_plain_text(section["content"])
            }
            iD = f"{filename}_section_{i}"
            documents.append(Document(page_content=section["full_markup"],
                                      metadata=metaData,
                                      id=iD))  # LaTeX с разметкой

        # Добавляем уравнения
        for i, equation in enumerate(structures["equations"]):
            metaData = {
                "filename": filename,
                "structure_type": "equation",
                "equation_type": equation["type"],
                "content_type": "latex_markup"
            }
            iD = f"{filename}_equation_{i}"

            documents.append(Document(page_content=equation["content"],
                                      metadata=metaData,
                                      id=iD))  # LaTeX с разметкой

        # Добавляем теоремы
        for i, theorem in enumerate(structures["theorems"]):
            metaData = {
                "filename": filename,
                "structure_type": "theorem",
                "theorem_type": theorem["type"],
                "content_type": "latex_markup",
                "clean_text": self.extract_plain_text(theorem["content"])
            }
            iD = f"{filename}_theorem_{i}"
            documents.append(Document(page_content=theorem["content"],
                                      metadata=metaData,
                                      id=iD))  # LaTeX с разметкой

        self.collection.add_documents(documents=documents)