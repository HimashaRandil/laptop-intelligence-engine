"""
Enhanced data ingestion script for parsing laptop specification PDFs.
This version handles the complex layouts and table structures found in the actual PDFs.

To run: PYTHONPATH=. python scripts/ingest_data.py
"""

import fitz  # PyMuPDF
import re
import sys
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from backend.src.app.core.db import SessionLocal
from backend.src.app.models.laptop import Laptop
from backend.src.app.models.specification import Specification
from backend.src.app.models.price_snapshot import PriceSnapshot
from backend.src.app.models.review import Review
from backend.src.app.models.questions_answer import QuestionsAnswer
from backend.src.utils.logger.logging import logger as logging


class SpecificationExtractor:
    """Base class for extracting specifications from different PDF formats."""

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.full_text = self._get_full_text()

    def _get_full_text(self) -> str:
        """Extract text from PDF with better formatting preservation."""
        try:
            with fitz.open(self.pdf_path) as doc:
                text_parts = []
                for page in doc:
                    # Get text with layout information
                    blocks = page.get_text("dict")["blocks"]
                    for block in blocks:
                        if "lines" in block:
                            for line in block["lines"]:
                                line_text = ""
                                for span in line["spans"]:
                                    line_text += span["text"]
                                if line_text.strip():
                                    text_parts.append(line_text)

                full_text = "\n".join(text_parts)
                # Join hyphenated words split at line breaks
                full_text = re.sub(r"-\s*\n\s*", "", full_text)
                # Normalize multiple whitespace/newlines
                full_text = re.sub(r"[ \t]+\n", "\n", full_text)
                full_text = re.sub(r"\n{2,}", "\n\n", full_text)
                return full_text
        except Exception as e:
            logging.error(f"Could not read PDF {self.pdf_path}: {e}")
            return ""

    def _normalize_text(self, text: str) -> str:
        """Clean and normalize text values."""
        if not text:
            return ""
        # Remove footnote markers
        text = re.sub(r"\[\d+\]", "", text)
        # Clean up whitespace
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def extract_specifications(self, laptop_id: int) -> List[Dict]:
        """Override in subclasses."""
        raise NotImplementedError


class ThinkPadExtractor(SpecificationExtractor):
    """Extractor for Lenovo ThinkPad specification sheets."""

    def extract_specifications(self, laptop_id: int) -> List[Dict]:
        specs = []

        # Extract processor information from table format
        specs.extend(self._extract_processor_specs(laptop_id))

        # Extract memory specifications
        specs.extend(self._extract_memory_specs(laptop_id))

        # Extract storage specifications
        specs.extend(self._extract_storage_specs(laptop_id))

        # Extract display specifications
        specs.extend(self._extract_display_specs(laptop_id))

        # Extract connectivity specs
        specs.extend(self._extract_connectivity_specs(laptop_id))

        # Extract physical specifications
        specs.extend(self._extract_physical_specs(laptop_id))

        # Extract battery specifications
        specs.extend(self._extract_battery_specs(laptop_id))

        return specs

    def _extract_processor_specs(self, laptop_id: int) -> List[Dict]:
        """Extract detailed processor specifications using windowed approach."""
        specs = []

        # Find processor section with more flexible anchoring
        processor_match = re.search(
            r"Processor\b.*?(?=(?:Operating System\b|Memory\b|$))",
            self.full_text,
            re.DOTALL | re.IGNORECASE,
        )
        if not processor_match:
            return specs

        processor_text = processor_match.group(0)

        # Use flexible processor name pattern that handles various Intel/AMD naming schemes
        proc_pattern = re.compile(
            r"(?P<name>(?:Intel(?:®|\(R\))?\s+Core[^\n,;()]+|AMD\s+Ryzen[^\n,;()]+|Core\s+i[^\n,;()]+|Intel\s+Core\s+Ultra[^\n,;()]+))",
            re.I,
        )

        for match in proc_pattern.finditer(processor_text):
            processor_name = self._normalize_text(match.group("name"))
            start = match.start()
            # Examine a window of text around the processor name for specs
            window = processor_text[start : start + 400]

            # Extract specs from the window using flexible patterns
            cores_match = re.search(
                r"(\d+)\s*(?:\([^)]*\))?\s*(?:cores?|P-core|E-core)", window, re.I
            )
            threads_match = re.search(r"(\d+)\s*threads?", window, re.I)
            cache_match = re.search(r"(\d+\s?MB(?:\s*L\d)?)", window, re.I)
            frequency_match = re.search(
                r"((?:\d+\.?\d*\s*GHz[^G]*){1,4})", window, re.I
            )
            graphics_match = re.search(
                r"(Intel[^\n,;]+Graphics|AMD[^\n,;]+Radeon[^\n,;]+|NVIDIA[^\n,;]+)",
                window,
                re.I,
            )

            # Create specs for found attributes
            if cores_match:
                specs.append(
                    {
                        "laptop_id": laptop_id,
                        "category": "Processor",
                        "specification_name": f"{processor_name} - Cores",
                        "specification_value": cores_match.group(1),
                    }
                )

            if threads_match:
                specs.append(
                    {
                        "laptop_id": laptop_id,
                        "category": "Processor",
                        "specification_name": f"{processor_name} - Threads",
                        "specification_value": threads_match.group(1),
                    }
                )

            if cache_match:
                specs.append(
                    {
                        "laptop_id": laptop_id,
                        "category": "Processor",
                        "specification_name": f"{processor_name} - Cache",
                        "specification_value": cache_match.group(1),
                    }
                )

            if frequency_match:
                specs.append(
                    {
                        "laptop_id": laptop_id,
                        "category": "Processor",
                        "specification_name": f"{processor_name} - Frequencies",
                        "specification_value": self._normalize_text(
                            frequency_match.group(1)
                        ),
                    }
                )

            if graphics_match:
                specs.append(
                    {
                        "laptop_id": laptop_id,
                        "category": "Graphics",
                        "specification_name": f"{processor_name} - Integrated Graphics",
                        "specification_value": self._normalize_text(
                            graphics_match.group(1)
                        ),
                    }
                )

        return specs

    def _extract_memory_specs(self, laptop_id: int) -> List[Dict]:
        """Extract memory specifications."""
        specs = []

        memory_section = re.search(
            r"Memory.*?(?=Storage)", self.full_text, re.DOTALL | re.IGNORECASE
        )
        if not memory_section:
            return specs

        memory_text = memory_section.group(0)

        # Extract max memory
        max_memory_match = re.search(r"Up to (\d+GB)[^)]*\(([^)]+)\)", memory_text)
        if max_memory_match:
            specs.append(
                {
                    "laptop_id": laptop_id,
                    "category": "Memory",
                    "specification_name": "Maximum Memory",
                    "specification_value": max_memory_match.group(1),
                }
            )
            specs.append(
                {
                    "laptop_id": laptop_id,
                    "category": "Memory",
                    "specification_name": "Memory Configuration",
                    "specification_value": self._normalize_text(
                        max_memory_match.group(2)
                    ),
                }
            )

        # Extract memory type
        memory_type_match = re.search(r"Memory Type\s+(DDR4-\d+)", memory_text)
        if memory_type_match:
            specs.append(
                {
                    "laptop_id": laptop_id,
                    "category": "Memory",
                    "specification_name": "Memory Type",
                    "specification_value": memory_type_match.group(1),
                }
            )

        return specs

    def _extract_storage_specs(self, laptop_id: int) -> List[Dict]:
        """Extract storage specifications."""
        specs = []

        storage_section = re.search(
            r"Storage.*?(?=Removable Storage)",
            self.full_text,
            re.DOTALL | re.IGNORECASE,
        )
        if not storage_section:
            return specs

        storage_text = storage_section.group(0)

        # Extract storage configurations
        storage_pattern = r"M\.2 (\d+) SSD.*?(\d+GB|\d+TB).*?(Opal 2\.0|-)"
        for match in re.finditer(storage_pattern, storage_text):
            form_factor = match.group(1)
            capacity = match.group(2)
            security = match.group(3)

            specs.append(
                {
                    "laptop_id": laptop_id,
                    "category": "Storage",
                    "specification_name": f"M.2 {form_factor} Storage Option",
                    "specification_value": f'{capacity} {"with " + security if security != "-" else ""}'.strip(),
                }
            )

        return specs

    def _extract_display_specs(self, laptop_id: int) -> List[Dict]:
        """Extract display specifications from table."""
        specs = []

        display_section = re.search(
            r"Display\*\*.*?(?=Touchscreen)", self.full_text, re.DOTALL | re.IGNORECASE
        )
        if not display_section:
            return specs

        display_text = display_section.group(0)

        # Extract display configurations
        display_pattern = r'14"\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+(\d+nits)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+(\d+Hz)\s+([^\n]+)'

        for match in re.finditer(display_pattern, display_text):
            resolution = match.group(1)
            touch = match.group(2)
            panel_type = match.group(3)
            brightness = match.group(4)
            surface = match.group(5)
            aspect_ratio = match.group(6)
            contrast = match.group(7)
            color_gamut = match.group(8)
            refresh_rate = match.group(9)
            features = match.group(10)

            display_name = f"{resolution} {touch}"

            specs.extend(
                [
                    {
                        "laptop_id": laptop_id,
                        "category": "Display",
                        "specification_name": f"{display_name} - Resolution",
                        "specification_value": resolution,
                    },
                    {
                        "laptop_id": laptop_id,
                        "category": "Display",
                        "specification_name": f"{display_name} - Touch Support",
                        "specification_value": touch,
                    },
                    {
                        "laptop_id": laptop_id,
                        "category": "Display",
                        "specification_name": f"{display_name} - Panel Type",
                        "specification_value": panel_type,
                    },
                    {
                        "laptop_id": laptop_id,
                        "category": "Display",
                        "specification_name": f"{display_name} - Brightness",
                        "specification_value": brightness,
                    },
                    {
                        "laptop_id": laptop_id,
                        "category": "Display",
                        "specification_name": f"{display_name} - Color Gamut",
                        "specification_value": self._normalize_text(color_gamut),
                    },
                ]
            )

        return specs

    def _extract_connectivity_specs(self, laptop_id: int) -> List[Dict]:
        """Extract connectivity specifications."""
        specs = []

        # Extract ports
        ports_match = re.search(
            r"Standard Ports(.*?)(?=Notes:|Docking)",
            self.full_text,
            re.DOTALL | re.IGNORECASE,
        )
        if ports_match:
            ports_text = ports_match.group(1)
            port_lines = [
                line.strip()
                for line in ports_text.split("\n")
                if line.strip() and "•" in line
            ]

            for port_line in port_lines:
                port_spec = port_line.replace("•", "").strip()
                if port_spec:
                    specs.append(
                        {
                            "laptop_id": laptop_id,
                            "category": "Connectivity",
                            "specification_name": "Port",
                            "specification_value": port_spec,
                        }
                    )

        # Extract wireless specs
        wlan_match = re.search(
            r"WLAN \+ Bluetooth.*?WWAN", self.full_text, re.DOTALL | re.IGNORECASE
        )
        if wlan_match:
            wlan_text = wlan_match.group(0)
            wireless_options = [
                line.strip() for line in wlan_text.split("\n") if "•" in line
            ]

            for option in wireless_options:
                clean_option = option.replace("•", "").strip()
                if clean_option and "Wi-Fi" in clean_option:
                    specs.append(
                        {
                            "laptop_id": laptop_id,
                            "category": "Connectivity",
                            "specification_name": "Wireless Option",
                            "specification_value": self._normalize_text(clean_option),
                        }
                    )

        return specs

    def _extract_physical_specs(self, laptop_id: int) -> List[Dict]:
        """Extract physical specifications."""
        specs = []

        # Extract dimensions
        dimensions_match = re.search(
            r"Dimensions \(WxDxH\).*?(\d+\.?\d* x \d+\.?\d* x \d+\.?\d* mm)",
            self.full_text,
        )
        if dimensions_match:
            specs.append(
                {
                    "laptop_id": laptop_id,
                    "category": "Physical",
                    "specification_name": "Dimensions",
                    "specification_value": dimensions_match.group(1),
                }
            )

        # Extract weight options
        weight_section = re.search(
            r"Weight.*?Case Color", self.full_text, re.DOTALL | re.IGNORECASE
        )
        if weight_section:
            weight_text = weight_section.group(0)
            weight_matches = re.findall(
                r"Starting at ([\d.]+) kg \(([\d.]+) lbs\)", weight_text
            )

            for weight_match in weight_matches:
                specs.append(
                    {
                        "laptop_id": laptop_id,
                        "category": "Physical",
                        "specification_name": "Weight",
                        "specification_value": f"{weight_match[0]} kg ({weight_match[1]} lbs)",
                    }
                )

        return specs

    def _extract_battery_specs(self, laptop_id: int) -> List[Dict]:
        """Extract battery specifications."""
        specs = []

        battery_section = re.search(
            r"Battery.*?Power Adapter", self.full_text, re.DOTALL | re.IGNORECASE
        )
        if not battery_section:
            return specs

        battery_text = battery_section.group(0)

        # Extract battery options
        battery_options = re.findall(
            r"(\d+Wh) Rechargeable Li-ion Battery", battery_text
        )
        for battery in battery_options:
            specs.append(
                {
                    "laptop_id": laptop_id,
                    "category": "Battery",
                    "specification_name": "Battery Option",
                    "specification_value": f"{battery} Li-ion with Rapid Charge",
                }
            )

        # Extract battery life data
        battery_life_section = re.search(
            r"Battery Life.*?Notes:", battery_text, re.DOTALL
        )
        if battery_life_section:
            life_text = battery_life_section.group(0)
            life_matches = re.findall(
                r"(MobileMark® \d+|JEITA \d+\.\d+|Local video playbook): up to ([\d.]+) hr",
                life_text,
            )

            for test_type, hours in life_matches:
                specs.append(
                    {
                        "laptop_id": laptop_id,
                        "category": "Battery",
                        "specification_name": f"Battery Life - {test_type}",
                        "specification_value": f"{hours} hours",
                    }
                )

        return specs


class HPExtractor(SpecificationExtractor):
    """Extractor for HP ProBook datasheets."""

    def extract_specifications(self, laptop_id: int) -> List[Dict]:
        specs = []

        # Find technical specifications section
        tech_specs_match = re.search(
            r"Technical specifications.*?(?=Footnotes)",
            self.full_text,
            re.DOTALL | re.IGNORECASE,
        )
        if not tech_specs_match:
            logging.warning(
                f"No technical specifications section found in {self.pdf_path}"
            )
            return specs

        tech_specs_text = tech_specs_match.group(0)

        # Extract processor specifications
        specs.extend(self._extract_processor_specs(laptop_id, tech_specs_text))

        # Extract memory specifications
        specs.extend(self._extract_memory_specs(laptop_id, tech_specs_text))

        # Extract storage specifications
        specs.extend(self._extract_storage_specs(laptop_id, tech_specs_text))

        # Extract display specifications
        specs.extend(self._extract_display_specs(laptop_id, tech_specs_text))

        # Extract graphics specifications
        specs.extend(self._extract_graphics_specs(laptop_id, tech_specs_text))

        # Extract connectivity specifications
        specs.extend(self._extract_connectivity_specs(laptop_id, tech_specs_text))

        # Extract physical specifications
        specs.extend(self._extract_physical_specs(laptop_id, tech_specs_text))

        return specs

    def _extract_processor_specs(self, laptop_id: int, text: str) -> List[Dict]:
        """Extract HP processor specifications."""
        specs = []

        # Extract processor families
        family_match = re.search(
            r"Processor family\s+(.*?)Available Processors",
            text,
            re.DOTALL | re.IGNORECASE,
        )
        if family_match:
            families = [
                f.strip() for f in family_match.group(1).split("\n") if f.strip()
            ]
            for family in families:
                if family:
                    specs.append(
                        {
                            "laptop_id": laptop_id,
                            "category": "Processor",
                            "specification_name": "Processor Family",
                            "specification_value": self._normalize_text(family),
                        }
                    )

        # Extract individual processors
        processor_section = re.search(
            r"Available Processors(.*?)(?=Maximum memory|Memory slots)",
            text,
            re.DOTALL | re.IGNORECASE,
        )
        if processor_section:
            proc_text = processor_section.group(1)
            # Match processor patterns like: Intel® Core™ Ultra 7 155H (specifications)
            proc_pattern = r"(Intel® Core™[^(]+)\s+\(([^)]+)\)"

            for match in re.finditer(proc_pattern, proc_text):
                processor_name = self._normalize_text(match.group(1))
                processor_specs = self._normalize_text(match.group(2))

                specs.append(
                    {
                        "laptop_id": laptop_id,
                        "category": "Processor",
                        "specification_name": processor_name,
                        "specification_value": processor_specs,
                    }
                )

        return specs

    def _extract_memory_specs(self, laptop_id: int, text: str) -> List[Dict]:
        """Extract HP memory specifications."""
        specs = []

        # Extract maximum memory
        max_mem_match = re.search(
            r"Maximum memory\s+(.+?)Memory slots", text, re.DOTALL | re.IGNORECASE
        )
        if max_mem_match:
            specs.append(
                {
                    "laptop_id": laptop_id,
                    "category": "Memory",
                    "specification_name": "Maximum Memory",
                    "specification_value": self._normalize_text(max_mem_match.group(1)),
                }
            )

        # Extract memory slots
        slots_match = re.search(
            r"Memory slots\s+(.+?)Internal storage", text, re.DOTALL | re.IGNORECASE
        )
        if slots_match:
            specs.append(
                {
                    "laptop_id": laptop_id,
                    "category": "Memory",
                    "specification_name": "Memory Slots",
                    "specification_value": self._normalize_text(slots_match.group(1)),
                }
            )

        return specs

    def _extract_storage_specs(self, laptop_id: int, text: str) -> List[Dict]:
        """Extract HP storage specifications."""
        specs = []

        storage_match = re.search(
            r"Internal storage\s+(.*?)(?=Display size|Display)",
            text,
            re.DOTALL | re.IGNORECASE,
        )
        if storage_match:
            storage_text = storage_match.group(1)
            storage_lines = [
                line.strip() for line in storage_text.split("\n") if line.strip()
            ]

            for line in storage_lines:
                if line and ("SSD" in line or "GB" in line or "TB" in line):
                    specs.append(
                        {
                            "laptop_id": laptop_id,
                            "category": "Storage",
                            "specification_name": "Storage Option",
                            "specification_value": self._normalize_text(line),
                        }
                    )

        return specs

    def _extract_display_specs(self, laptop_id: int, text: str) -> List[Dict]:
        """Extract HP display specifications."""
        specs = []

        # Extract display size
        size_match = re.search(
            r"Display size \(diagonal, metric\)\s+(.+?)Display",
            text,
            re.DOTALL | re.IGNORECASE,
        )
        if size_match:
            specs.append(
                {
                    "laptop_id": laptop_id,
                    "category": "Display",
                    "specification_name": "Display Size",
                    "specification_value": self._normalize_text(size_match.group(1)),
                }
            )

        # Extract display options
        display_match = re.search(
            r"(?<!size )Display\s+(.*?)(?=Available Graphics|Audio)",
            text,
            re.DOTALL | re.IGNORECASE,
        )
        if display_match:
            display_text = display_match.group(1)
            # Split by semicolons to get different display options
            display_options = [
                opt.strip() for opt in display_text.split(";") if opt.strip()
            ]

            for i, option in enumerate(display_options, 1):
                if option:
                    specs.append(
                        {
                            "laptop_id": laptop_id,
                            "category": "Display",
                            "specification_name": f"Display Option {i}",
                            "specification_value": self._normalize_text(option),
                        }
                    )

        return specs

    def _extract_graphics_specs(self, laptop_id: int, text: str) -> List[Dict]:
        """Extract HP graphics specifications."""
        specs = []

        graphics_match = re.search(
            r"Available Graphics\s+(.*?)(?=Audio|Ports)",
            text,
            re.DOTALL | re.IGNORECASE,
        )
        if graphics_match:
            graphics_text = graphics_match.group(1)
            graphics_lines = [
                line.strip() for line in graphics_text.split("\n") if line.strip()
            ]

            for line in graphics_lines:
                if line and ("Graphics" in line or "GPU" in line):
                    specs.append(
                        {
                            "laptop_id": laptop_id,
                            "category": "Graphics",
                            "specification_name": "Graphics Option",
                            "specification_value": self._normalize_text(line),
                        }
                    )

        return specs

    def _extract_connectivity_specs(self, laptop_id: int, text: str) -> List[Dict]:
        """Extract HP connectivity specifications."""
        specs = []

        # Extract ports
        ports_match = re.search(
            r"Ports and connectors\s+(.*?)(?=Input devices|Communications)",
            text,
            re.DOTALL | re.IGNORECASE,
        )
        if ports_match:
            ports_text = ports_match.group(1)
            specs.append(
                {
                    "laptop_id": laptop_id,
                    "category": "Connectivity",
                    "specification_name": "Ports and Connectors",
                    "specification_value": self._normalize_text(ports_text),
                }
            )

        # Extract communications
        comm_match = re.search(
            r"Communications\s+(.*?)(?=Camera|Software)",
            text,
            re.DOTALL | re.IGNORECASE,
        )
        if comm_match:
            comm_text = comm_match.group(1)
            specs.append(
                {
                    "laptop_id": laptop_id,
                    "category": "Connectivity",
                    "specification_name": "Communications",
                    "specification_value": self._normalize_text(comm_text),
                }
            )

        return specs

    def _extract_physical_specs(self, laptop_id: int, text: str) -> List[Dict]:
        """Extract HP physical specifications."""
        specs = []

        # Extract dimensions
        dimensions_match = re.search(
            r"Dimensions\s+(.*?)Weight", text, re.DOTALL | re.IGNORECASE
        )
        if dimensions_match:
            specs.append(
                {
                    "laptop_id": laptop_id,
                    "category": "Physical",
                    "specification_name": "Dimensions",
                    "specification_value": self._normalize_text(
                        dimensions_match.group(1)
                    ),
                }
            )

        # Extract weight
        weight_match = re.search(
            r"Weight\s+(.*?)(?=Ecolabels|Energy star)", text, re.DOTALL | re.IGNORECASE
        )
        if weight_match:
            specs.append(
                {
                    "laptop_id": laptop_id,
                    "category": "Physical",
                    "specification_name": "Weight",
                    "specification_value": self._normalize_text(weight_match.group(1)),
                }
            )

        return specs


def ingest_specifications(db: Session):
    """Main ingestion function."""
    logging.info("Starting enhanced PDF specification ingestion...")

    laptop_configs = [
        (
            "ThinkPad E14 Gen 5 (Intel)",
            ThinkPadExtractor,
            "data/raw/ThinkPad_E14_Gen_5_Intel_Spec.pdf",
        ),
        (
            "ThinkPad E14 Gen 5 (AMD)",
            ThinkPadExtractor,
            "data/raw/ThinkPad_E14_Gen_5_AMD_Spec.pdf",
        ),
        ("HP ProBook 450 G10", HPExtractor, "data/raw/c08504822.pdf"),
        ("HP ProBook 440 G11", HPExtractor, "data/raw/c08947328.pdf"),
    ]

    for laptop_name, extractor_class, pdf_path in laptop_configs:
        try:
            with db.begin():
                laptop = db.query(Laptop).filter_by(full_model_name=laptop_name).first()
                if not laptop:
                    logging.warning(f"Laptop '{laptop_name}' not found in database.")
                    continue

                # Clear existing specifications
                deleted_count = (
                    db.query(Specification).filter_by(laptop_id=laptop.id).delete()
                )
                if deleted_count > 0:
                    logging.info(
                        f"Cleared {deleted_count} existing specs for '{laptop_name}'."
                    )

                # Extract new specifications
                extractor = extractor_class(pdf_path)
                specs_data = extractor.extract_specifications(laptop.id)

                if specs_data:
                    db.bulk_insert_mappings(Specification, specs_data)
                    logging.info(
                        f"Successfully added {len(specs_data)} specifications for '{laptop_name}'."
                    )
                else:
                    logging.warning(f"No specifications extracted for '{laptop_name}'.")

        except Exception as e:
            logging.exception(f"Failed to process '{laptop_name}': {e}")


def test_extractors():
    """Test function to verify extractors work without database operations."""
    logging.info("Testing extractors...")

    test_configs = [
        (
            "ThinkPad E14 Gen 5 (Intel)",
            ThinkPadExtractor,
            "data/raw/ThinkPad_E14_Gen_5_Intel_Spec.pdf",
        ),
        ("HP ProBook 440 G11", HPExtractor, "data/raw/c08947328.pdf"),
    ]

    for laptop_name, extractor_class, pdf_path in test_configs:
        logging.info(f"\nTesting {laptop_name}...")
        try:
            extractor = extractor_class(pdf_path)
            specs = extractor.extract_specifications(laptop_id=1)  # Test with dummy ID

            logging.info(f"Extracted {len(specs)} specifications:")
            for spec in specs[:10]:  # Show first 10
                logging.info(
                    f"  {spec['category']} -> {spec['specification_name']}: {spec['specification_value'][:100]}..."
                )

        except Exception as e:
            logging.exception(f"Error testing {laptop_name}: {e}")


if __name__ == "__main__":
    if "--test" in sys.argv:
        test_extractors()
    else:
        db_session = SessionLocal()
        try:
            ingest_specifications(db_session)
        finally:
            db_session.close()
        logging.info("PDF ingestion process completed.")
