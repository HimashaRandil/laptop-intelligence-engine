import os
import json
import re
from backend.src.utils.logger.logging import logger as logging
from openai import OpenAI

try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception as e:
    logging.error(
        f"OpenAI client failed to initialize. Check OPENAI_API_KEY. Error: {e}"
    )
    client = None


def extract_processor_model_from_name(spec_name: str) -> str:
    """Extract processor model from specification name."""
    patterns = [
        r"(Intel.*?Core.*?Ultra.*?\d+[A-Z])",
        r"(Core\s+i[3579]-?\d+[A-Z]+)",
        r"(AMD\s+Ryzen.*?\d+[A-Z]?)",
        r"(Intel.*?Pentium.*?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, spec_name, re.I)
        if match:
            return match.group(1).strip()
    return None


PROMPT_TEMPLATES = {
    "Processor": """
You are parsing laptop processor specifications. Extract information into JSON.

IMPORTANT RULES:
1. For hybrid architecture (P-core/E-core) processors:
   - Use the HIGHEST boost/turbo frequency for max_frequency_ghz
   - Use the LOWEST base frequency for base_frequency_ghz
   - Sum P-cores and E-cores for total cores

2. For "X GHz / E-core Y GHz" format:
   - X is P-core frequency, Y is E-core frequency
   - max_frequency_ghz should be the highest turbo mentioned anywhere

3. Brand identification:
   - "Intel" for any Intel processor
   - "AMD" for any AMD processor

Specification Name: "{spec_name}"
Raw Value: "{raw_value}"

Return JSON with:
- model: Full processor name (extract from spec_name if not in raw_value)
- brand: "Intel" or "AMD"
- cores: Total number of cores (integer)
- threads: Total threads (integer)
- base_frequency_ghz: Lowest base frequency (number)
- max_frequency_ghz: Highest turbo/boost frequency (number)
- cache_mb: Total cache in MB (number)
- integrated_graphics: GPU model name (string or null)

Use null for truly missing values only.
""",
    "Display": """
Parse laptop display specification into JSON.

Text may describe one or multiple displays. If multiple displays, return array under "displays" key.

For each display extract:
- diagonal_size_inches: Screen size (number like 14, 15.6)
- resolution: Like "1920x1080" or "2560x1600" (string)
- panel_type: IPS, OLED, TN, VA, etc (string)
- brightness_nits: Brightness level (number)
- color_gamut_percent: Percentage (number, from "45% NTSC" extract 45)
- color_space: NTSC, sRGB, DCI-P3, Adobe RGB (string)
- is_touchscreen: true/false based on "touch" keyword
- aspect_ratio: Like "16:9" or "16:10" (string)
- refresh_rate_hz: Default 60 if not specified (number)

Specification: "{spec_name}"
Text: "{raw_value}"
""",
    "Memory": """
Parse memory specification into JSON.

Extract:
- max_capacity_gb: Maximum RAM (number like 32 for "32GB")
- memory_type: Like "DDR4-3200", "DDR5-5600" (string)
- slots_total: Number of memory slots (integer)
- slots_available: How many can be upgraded (integer)
- is_dual_channel: true/false
- soldered_amount_gb: RAM soldered to motherboard (number)

For "8GB soldered + 32GB SO-DIMM":
- max_capacity_gb: 40
- soldered_amount_gb: 8
- slots_total: 1 (the SO-DIMM slot)
- slots_available: 1

Text: "{raw_value}"
""",
    "Storage": """
Parse storage specification into JSON.

If multiple storage options, return array of objects.

For each storage extract:
- capacity_gb: Use 1000 for 1TB, 512 for 512GB (number or array if range)
- form_factor: Like "M.2 2242", "M.2 2280" (string)
- interface: Like "PCIe Gen4x4 NVMe", "PCIe 4.0 x4" (string)
- type: "SSD" or "HDD" (string)
- security: Like "Opal 2.0" or null

For ranges like "512 GB up to 1 TB", use: "capacity_gb": [512, 1000]

Text: "{raw_value}"
""",
    "Graphics": """
Parse graphics specification into JSON.

Extract:
- model: Full graphics name (string)
- type: "Integrated" or "Discrete" (string)
- memory_gb: VRAM amount for discrete GPUs (number)
- brand: "Intel", "AMD", or "NVIDIA" (string)

For combined listings like "Intel® Arc™ Graphics; Intel® Graphics":
- Just use the first/primary option

Text: "{raw_value}"
""",
    "Physical": """
Parse physical specifications into JSON.

Extract:
- weight_kg: Weight in kilograms (number)
- weight_lbs: Weight in pounds (number)
- dimensions_mm: Object with width, depth, height in mm
- dimensions_inches: Object with width, depth, height in inches

For "35.94 x 23.39 x 1.99 cm" convert to mm:
dimensions_mm: {{"width": 359.4, "depth": 233.9, "height": 19.9}}

Text: "{raw_value}"
""",
    "Battery": """
Parse battery specification into JSON.

DO NOT create separate entries for battery life tests. Instead:

Extract:
- capacity_wh: Watt hours (number like 47 for "47Wh")
- chemistry: Like "Li-ion", "Li-Po" (string)
- cells: Number of cells (integer)
- rapid_charge: true/false
- battery_life_hours: Typical usage hours (number)
- test_results: Array of {{"test_name": "...", "hours": number}}

For "Battery Life - MobileMark® 2018: 11.2 hours":
Add to test_results: [{{"test_name": "MobileMark 2018", "hours": 11.2}}]

Text: "{raw_value}"
""",
    "Connectivity": """
Parse connectivity specification into JSON.

Extract:
- wifi_standard: Like "Wi-Fi 6E", "Wi-Fi 6" (string)
- bluetooth_version: Like "5.3", "5.2" (string)
- ethernet: true/false (check for RJ-45, GbE, ethernet mentions)
- ports: Array of port descriptions (array of strings)
- wireless_wan: true/false (cellular/LTE/5G capability)

For port lists, create clean array entries.

Text: "{raw_value}"
""",
}


def structure_specification(
    spec_name: str, raw_value: str, category: str
) -> dict | None:
    """
    Enhanced LLM structuring with better prompts and post-processing.
    """
    if not client:
        return None

    # Skip obviously bad data
    if len(raw_value.strip()) < 3:
        return None

    # Category-based prompt selection
    prompt_template = PROMPT_TEMPLATES.get(category)

    # Fallback: try to infer from spec name
    if not prompt_template:
        for key in PROMPT_TEMPLATES.keys():
            if key.lower() in spec_name.lower() or key.lower() in category.lower():
                prompt_template = PROMPT_TEMPLATES[key]
                break

    if not prompt_template:
        logging.warning(
            f"No suitable prompt for category '{category}', spec '{spec_name}'"
        )
        return None

    prompt = prompt_template.format(spec_name=spec_name, raw_value=raw_value)

    try:
        logging.info(f"Structuring '{spec_name}' (category: {category})...")
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise technical specification parser. Always return valid JSON. Extract ALL available information. Use null only when information is truly absent.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )

        content = response.choices[0].message.content
        structured_data = json.loads(content)

        # Post-processing validation and enrichment
        structured_data = post_process_structured_data(
            structured_data, spec_name, raw_value, category
        )

        return structured_data

    except Exception as e:
        logging.error(f"LLM structuring failed for '{spec_name}'. Error: {e}")
        return None


def post_process_structured_data(
    data: dict, spec_name: str, raw_value: str, category: str
) -> dict:
    """
    Validate and enrich structured data after LLM processing.
    """
    if category == "Processor":
        # Extract model from spec_name if missing
        if not data.get("model") or data.get("model") == "null":
            extracted_model = extract_processor_model_from_name(spec_name)
            if extracted_model:
                data["model"] = extracted_model

        # Infer brand from model
        if not data.get("brand"):
            model = data.get("model", "")
            if "intel" in model.lower() or "core" in model.lower():
                data["brand"] = "Intel"
            elif "amd" in model.lower() or "ryzen" in model.lower():
                data["brand"] = "AMD"

        # Parse frequencies from raw_value if missing
        if not data.get("max_frequency_ghz"):
            freq_match = re.search(r"(\d+\.?\d*)\s*GHz", raw_value)
            if freq_match:
                data["max_frequency_ghz"] = float(freq_match.group(1))

    elif category == "Display":
        # Ensure refresh_rate defaults to 60
        if not data.get("refresh_rate_hz"):
            data["refresh_rate_hz"] = 60

        # Handle displays array vs single display
        if "displays" in data and isinstance(data["displays"], list):
            for display in data["displays"]:
                if not display.get("refresh_rate_hz"):
                    display["refresh_rate_hz"] = 60

    elif category == "Memory":
        # Calculate max_capacity from components
        if not data.get("max_capacity_gb"):
            soldered = data.get("soldered_amount_gb", 0) or 0
            # Try to infer from raw text
            gb_match = re.search(r"(\d+)\s*GB", raw_value, re.I)
            if gb_match:
                data["max_capacity_gb"] = int(gb_match.group(1))

    return data
