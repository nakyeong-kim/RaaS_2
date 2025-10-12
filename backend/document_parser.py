
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import tempfile, os

def parse_document(file):
    endpoint = os.environ.get("AZURE_DOC_ENDPOINT")
    key = os.environ.get("AZURE_DOC_KEY")
    client = DocumentAnalysisClient(endpoint, AzureKeyCredential(key))

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        content = file.getvalue()
        tmp.write(content)
        tmp_path = tmp.name

    poller = client.begin_analyze_document("prebuilt-layout", document=open(tmp_path, "rb"))
    poller = client.begin_analyze_document("prebuilt-layout", f)
    result = poller.result()

    text = "\n".join([line.content for page in result.pages for line in page.lines])
    os.remove(tmp_path)
    return text
