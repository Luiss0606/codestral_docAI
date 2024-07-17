# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_admin import initialize_app, firestore, credentials
from dotenv import load_dotenv
from firebase_functions.firestore_fn import (
    Event,
    on_document_created,
    DocumentSnapshot,
)
from firebase_functions import options

from langflow.load import run_flow_from_json


cred = credentials.Certificate("./credentials.json")

initialize_app(cred)
db = firestore.client()


load_dotenv()


TWEAKS_SCRIPT = {
    "ChatInput-qNjGp": {
        "files": "",
        "input_value": "",
        "sender": "User",
        "sender_name": "User",
        "session_id": "",
        "store_message": True,
    },
    "Prompt-TLE1F": {
        "template": "You are an AI specialized in generating technical documentation. Generate complete and professional documentation for the following project:\n\n{input_message}\n\nThe documentation must include the following sections, formatted according to the specified output format:\n\n1. Introduction\n   - Project general description.\n   - Key features and benefits.\n   - Target audience and use cases.\n\n2. Installation\n   - Detailed steps for project setup.\n   - Dependencies and prerequisites.\n   - Platform-specific instructions (if any).\n\n3. Use\n   - How to use the project.\n   - Common use cases and workflows.\n   - Command line options (if applicable).\n\n4. API Reference\n   - Detailed documentation for all public classes, functions and methods.\n   - Parameters, return values ​​and exceptions.\n   - Code snippets and examples (if applicable).\n\n5. Examples (if applicable)\n   - Practical examples that demonstrate how to use the project.\n   - Step-by-step guides and tutorials.\n\n6. FAQ (if applicable)\n   - Frequently asked questions and their answers.\n   - Troubleshooting tips.\n\n7. Conclusion\n   - Summary of project capabilities.\n   - Future plans and roadmap (if any).\n   - Contact information and support resources.\n\nAdditional requirements:\n- Documentation must be written in tone (Style/Tone)\n- Ensure that the content is clear, concise and easy to understand.\n- Maintain a consistent format and style throughout the document.\n- Highlight important information and best practices.\n\nUse the following project metadata to customize the documentation:\n\n- Project Name\n- Description\n- Project Type\n- Target Audience\n- Level of Detail\n- Include examples\n- Output format\n- Script information",
        "input_message": "",
    },
    "ChatOutput-JZXWU": {
        "data_template": "{text}",
        "input_value": "",
        "sender": "Machine",
        "sender_name": "AI",
        "session_id": "",
        "store_message": True,
    },
    "MistralModel-y0gwj": {
        "input_value": "",
        "max_concurrent_requests": 3,
        "max_retries": 5,
        "max_tokens": 4080,
        "mistral_api_base": "https://codestral.mistral.ai/v1/",
        "mistral_api_key": "MISTRAL_API_KEY",
        "model_name": "codestral-latest",
        "random_seed": 1,
        "safe_mode": False,
        "stream": False,
        "system_message": "",
        "temperature": 0.5,
        "timeout": 60,
        "top_p": 1,
    },
}
TWEAKS_UPLOAD = {
    "SplitText-rKsBs": {"chunk_overlap": 500, "chunk_size": 4000, "separator": "\n"},
    "AstraVectorStoreComponent-G0VlA": {
        "api_endpoint": "ASTRADB_END_POINT",
        "collection_indexing_policy": "",
        "collection_name": "codestral",
        "metadata_indexing_exclude": "",
        "metadata_indexing_include": "",
        "metric": "",
        "namespace": "",
        "number_of_results": 4,
        "pre_delete_collection": False,
        "search_filter": {},
        "search_input": "",
        "search_score_threshold": 0,
        "search_type": "Similarity",
        "setup_mode": "Sync",
    },
    "OpenAIEmbeddings-JhYca": {
        "chunk_size": 1000,
        "client": "",
        "default_headers": {},
        "default_query": {},
        "deployment": "",
        "embedding_ctx_length": 1536,
        "max_retries": 3,
        "model": "text-embedding-3-large",
        "model_kwargs": {},
        "openai_api_base": "",
        "openai_api_key": "",
        "openai_api_type": "",
        "openai_api_version": "",
        "openai_organization": "",
        "openai_proxy": "",
        "show_progress_bar": False,
        "skip_empty": False,
        "tiktoken_enable": True,
        "tiktoken_model_name": "",
    },
    "Directory-hseXE": {
        "depth": 0,
        "load_hidden": False,
        "max_concurrency": 2,
        "path": "",
        "recursive": False,
        "silent_errors": False,
        "types": [],
        "use_multithreading": False,
    },
}


@on_document_created(
    timeout_sec=400, document="requesScript/{campId}", memory=options.MemoryOption.GB_2
)
def request_script(event: Event[DocumentSnapshot]) -> None:
    try:
        request_script_data = event.data.to_dict()

        script_info = request_script_data["script"]

        id_request_script = event.data.id
        print("id_request_script", id_request_script)

        id_request = request_script_data["request_ref"].id
        print("id_request", id_request)

        request_gen_data_dict = (
            db.collection("requestGen").document(id_request).get().to_dict()
        )
        print("request_gen_data", request_gen_data_dict)

        request_gen_data = "\n".join(
            [
                f"{key}: {value}"
                for key, value in request_gen_data_dict.items()
                if key != "owner" and key != "time_created"
            ]
        )

        input_doc_gen = f"{request_gen_data}\n{script_info}"
        print("input_doc_gen", input_doc_gen)

        result = (
            run_flow_from_json(
                flow="./jsons/doc_script_gen.json",
                input_value=input_doc_gen,
                fallback_to_env_vars=True,  # False by default
                tweaks=TWEAKS_SCRIPT,
            )[0]
            .outputs[0]
            .results["message"]
            .text
        )

        db.collection("requesScript").document(id_request_script).update(
            {"documentation": result, "in_progress": False}
        )

    except Exception as e:
        import traceback

        print("Error: ", e)
        traceback.print_exc()
