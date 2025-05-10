export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ""
export const AI_API_BASE_URL = "https://app-dev-ai-swec-001.azurewebsites.net"

export const DEFAULT_AI_SETTINGS = {
    top: 5,
    temperature: 0.3,
    minimum_reranker_score: 0,
    minimum_search_score: 0,
    retrieval_mode: "hybrid",
    semantic_ranker: true,
    semantic_captions: false,
    suggest_followup_questions: false,
    use_oid_security_filter: false,
    use_groups_security_filter: false,
    vector_fields: ["embedding"],
    use_gpt4v: false,
    gpt4v_input: "textAndImages",
}