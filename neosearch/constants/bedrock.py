# Bedrock model ids: <https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html#model-ids-arns>

# AI21 Labs Models
AI21_JAMBA_INSTRUCT = "ai21.jamba-instruct-v1:0"
AI21_JURASSIC2_MID = "ai21.j2-mid-v1"
AI21_JURASSIC2_ULTRA = "ai21.j2-ultra-v1"
AI21_JAMBA_15_LARGE = "ai21.jamba-1-5-large-v1:0"
AI21_JAMBA_15_MINI = "ai21.jamba-1-5-mini-v1:0"

AI21_MODELS = {
    AI21_JAMBA_INSTRUCT,
    AI21_JURASSIC2_MID,
    AI21_JURASSIC2_ULTRA,
    AI21_JAMBA_15_LARGE,
    AI21_JAMBA_15_MINI
}

# Amazon Models
AMAZON_TITAN_TEXT_EXPRESS = "amazon.titan-text-express-v1"
AMAZON_TITAN_TEXT_LITE = "amazon.titan-text-lite-v1"
AMAZON_TITAN_TEXT_PREMIER = "amazon.titan-text-premier-v1:0"
AMAZON_TITAN_EMBED_TEXT = "amazon.titan-embed-text-v1"
AMAZON_TITAN_EMBED_TEXT_V2 = "amazon.titan-embed-text-v2:0"
AMAZON_TITAN_EMBED_IMAGE = "amazon.titan-embed-image-v1"
AMAZON_TITAN_IMAGE_GEN = "amazon.titan-image-generator-v1"
AMAZON_TITAN_IMAGE_GEN_V2 = "amazon.titan-image-generator-v2:0"

AMAZON_MODELS = {
    AMAZON_TITAN_TEXT_EXPRESS,
    AMAZON_TITAN_TEXT_LITE,
    AMAZON_TITAN_TEXT_PREMIER,
    AMAZON_TITAN_EMBED_TEXT,
    AMAZON_TITAN_EMBED_TEXT_V2,
    AMAZON_TITAN_EMBED_IMAGE,
    AMAZON_TITAN_IMAGE_GEN,
    AMAZON_TITAN_IMAGE_GEN_V2
}

# Anthropic Models
ANTHROPIC_CLAUDE_V2 = "anthropic.claude-v2"
ANTHROPIC_CLAUDE_V21 = "anthropic.claude-v2:1"
ANTHROPIC_CLAUDE3_SONNET = "anthropic.claude-3-sonnet-20240229-v1:0"
ANTHROPIC_CLAUDE35_SONNET = "anthropic.claude-3-5-sonnet-20240620-v1:0"
ANTHROPIC_CLAUDE35_SONNET_V2 = "anthropic.claude-3-5-sonnet-20241022-v2:0"
ANTHROPIC_CLAUDE3_HAIKU = "anthropic.claude-3-haiku-20240307-v1:0"
ANTHROPIC_CLAUDE35_HAIKU = "anthropic.claude-3-5-haiku-20241022-v1:0"
ANTHROPIC_CLAUDE3_OPUS = "anthropic.claude-3-opus-20240229-v1:0"
ANTHROPIC_CLAUDE_INSTANT = "anthropic.claude-instant-v1"

ANTHROPIC_MODELS = {
    ANTHROPIC_CLAUDE_V2,
    ANTHROPIC_CLAUDE_V21,
    ANTHROPIC_CLAUDE3_SONNET,
    ANTHROPIC_CLAUDE35_SONNET,
    ANTHROPIC_CLAUDE35_SONNET_V2,
    ANTHROPIC_CLAUDE3_HAIKU,
    ANTHROPIC_CLAUDE35_HAIKU,
    ANTHROPIC_CLAUDE3_OPUS,
    ANTHROPIC_CLAUDE_INSTANT
}

# Cohere Models
COHERE_COMMAND = "cohere.command-text-v14"
COHERE_COMMAND_LIGHT = "cohere.command-light-text-v14"
COHERE_COMMAND_R = "cohere.command-r-v1:0"
COHERE_COMMAND_R_PLUS = "cohere.command-r-plus-v1:0"
COHERE_EMBED_ENGLISH = "cohere.embed-english-v3"
COHERE_EMBED_MULTILINGUAL = "cohere.embed-multilingual-v3"

COHERE_MODELS = {
    COHERE_COMMAND,
    COHERE_COMMAND_LIGHT,
    COHERE_COMMAND_R,
    COHERE_COMMAND_R_PLUS,
    COHERE_EMBED_ENGLISH,
    COHERE_EMBED_MULTILINGUAL
}

# Meta Models
META_LLAMA3_8B = "meta.llama3-8b-instruct-v1:0"
META_LLAMA3_70B = "meta.llama3-70b-instruct-v1:0"
META_LLAMA31_8B = "meta.llama3-1-8b-instruct-v1:0"
META_LLAMA31_70B = "meta.llama3-1-70b-instruct-v1:0"
META_LLAMA31_405B = "meta.llama3-1-405b-instruct-v1:0"
META_LLAMA32_1B = "meta.llama3-2-1b-instruct-v1:0"
META_LLAMA32_3B = "meta.llama3-2-3b-instruct-v1:0"
META_LLAMA32_11B = "meta.llama3-2-11b-instruct-v1:0"
META_LLAMA32_90B = "meta.llama3-2-90b-instruct-v1:0"

META_MODELS = {
    META_LLAMA3_8B,
    META_LLAMA3_70B,
    META_LLAMA31_8B,
    META_LLAMA31_70B,
    META_LLAMA31_405B,
    META_LLAMA32_1B,
    META_LLAMA32_3B,
    META_LLAMA32_11B,
    META_LLAMA32_90B
}

# Mistral AI Models
MISTRAL_7B = "mistral.mistral-7b-instruct-v0:2"
MISTRAL_MIXTRAL = "mistral.mixtral-8x7b-instruct-v0:1"
MISTRAL_LARGE = "mistral.mistral-large-2402-v1:0"
MISTRAL_LARGE_2407 = "mistral.mistral-large-2407-v1:0"
MISTRAL_SMALL = "mistral.mistral-small-2402-v1:0"

MISTRAL_MODELS = {
    MISTRAL_7B,
    MISTRAL_MIXTRAL,
    MISTRAL_LARGE,
    MISTRAL_LARGE_2407,
    MISTRAL_SMALL
}

# Stability AI Models
STABILITY_SDXL_V0 = "stability.stable-diffusion-xl-v0"
STABILITY_SDXL_V1 = "stability.stable-diffusion-xl-v1"
STABILITY_SD3_LARGE = "stability.sd3-large-v1:0"
STABILITY_IMAGE_ULTRA = "stability.stable-image-ultra-v1:0"
STABILITY_IMAGE_CORE = "stability.stable-image-core-v1:0"

STABILITY_MODELS = {
    STABILITY_SDXL_V0,
    STABILITY_SDXL_V1,
    STABILITY_SD3_LARGE,
    STABILITY_IMAGE_ULTRA,
    STABILITY_IMAGE_CORE
}

# All models combined
ALL_MODELS = (
    AI21_MODELS |
    AMAZON_MODELS |
    ANTHROPIC_MODELS |
    COHERE_MODELS |
    META_MODELS |
    MISTRAL_MODELS |
    STABILITY_MODELS
)
