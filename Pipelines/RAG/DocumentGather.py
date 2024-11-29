from pathlib import Path
from haystack.components.writers import DocumentWriter
from haystack.components.converters import (
    MarkdownToDocument,
    PyPDFToDocument,
    TextFileToDocument,
    HTMLToDocument,
)
from haystack.components.preprocessors import DocumentSplitter, DocumentCleaner
from haystack.components.routers import FileTypeRouter
from haystack.components.joiners import DocumentJoiner
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack import Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore

class DocumentProcessingPipeline:
    def __init__(self, directory_path="C:/Users/alvar/Documents/Cono"):
        self.directory_path = directory_path
        self.document_store = InMemoryDocumentStore()
        self.pipeline = Pipeline()
        self._setup_pipeline()

    def _setup_pipeline(self):
        file_type_router = FileTypeRouter(
            mime_types=["text/plain", "application/pdf", "text/markdown", "text/html"]
        )
        text_file_converter = TextFileToDocument()
        markdown_converter = MarkdownToDocument()
        pdf_converter = PyPDFToDocument()
        document_joiner = DocumentJoiner()
        document_cleaner = DocumentCleaner()
        document_splitter = DocumentSplitter(
            split_by="word", split_length=150, split_overlap=50
        )
        document_embedder = SentenceTransformersDocumentEmbedder(
            model="sentence-transformers/all-MiniLM-L6-v2"
        )
        document_embedder.warm_up()
        document_writer = DocumentWriter(self.document_store)
        html_converter = HTMLToDocument()

        self.pipeline.add_component(instance=file_type_router, name="file_type_router")
        self.pipeline.add_component(instance=html_converter, name="html_to_document")
        self.pipeline.add_component(instance=text_file_converter, name="text_file_converter")
        self.pipeline.add_component(instance=markdown_converter, name="markdown_converter")
        self.pipeline.add_component(instance=pdf_converter, name="pypdf_converter")
        self.pipeline.add_component(instance=document_joiner, name="document_joiner")
        self.pipeline.add_component(instance=document_cleaner, name="document_cleaner")
        self.pipeline.add_component(instance=document_splitter, name="document_splitter")
        self.pipeline.add_component(instance=document_embedder, name="document_embedder")
        self.pipeline.add_component(instance=document_writer, name="document_writer")

        # Connect components
        self._connect_pipeline_components()

    def _connect_pipeline_components(self):
        self.pipeline.connect("file_type_router.text/plain", "text_file_converter.sources")
        self.pipeline.connect("file_type_router.text/html", "html_to_document.sources")
        self.pipeline.connect("file_type_router.application/pdf", "pypdf_converter.sources")
        self.pipeline.connect("file_type_router.text/markdown", "markdown_converter.sources")
        self.pipeline.connect("text_file_converter", "document_joiner")
        self.pipeline.connect("pypdf_converter", "document_joiner")
        self.pipeline.connect("markdown_converter", "document_joiner")
        self.pipeline.connect("html_to_document", "document_joiner")
        self.pipeline.connect("document_joiner", "document_cleaner")
        self.pipeline.connect("document_cleaner", "document_splitter")
        self.pipeline.connect("document_splitter", "document_embedder")
        self.pipeline.connect("document_embedder", "document_writer")

    def run(self):
        output = self.pipeline.run(
            {
                "file_type_router": {
                    "sources": list(Path(self.directory_path).rglob("*"))
                }
            }
        )
        return output

if __name__ == "__main__":
    pipeline = DocumentProcessingPipeline()
    output = pipeline.run()
    
    print(output)
    # Uncomment below lines to print details about the processed documents
    # documents = output[0]
    # print(f"Processed {len(documents)} documents.")
    # print(documents)
    # for doc in documents:
    #     print(doc.content)
